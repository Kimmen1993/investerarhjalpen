#!/usr/bin/env python3
"""Facit: håller verktygets signaler och bedömningar? Gratis, ingen AI.

Verktyget sparar NÄR det sa VAD om ett bolag, till exempel att det kom in på radarn, fick
fas 2 eller kastades. Loggen raderas aldrig, så uppföljningen kan sträcka sig hur många år
som helst. Kurserna hämtas i efterhand från Yahoo Finance, och varje händelse jämförs med
Stockholmsbörsen (OMX Stockholm PI) under samma tid.

Filer i datamappen (privata):
  facit/handelser.json   alla händelser, raderas aldrig
  facit/lage.json        läget vid förra körningen (för att se vad som är nytt)
  facit/symboler.json    ISIN/namn → kurssymbol (rätta här om en symbol blev fel)
  facit/kurser/          dagskurser per symbol (cache)
  facit/resultat.json    utfallet per händelse och sammanfattningen som sidan visar

Kör från datamappen:  python3 -I "$IH/verktyg/facit.py"        (morgonkollen, varje dag)
                      python3 -I "$IH/verktyg/facit.py" --utan-kurser   (bara logga, ingen hämtning)
"""
import json
import statistics
import sys
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rot import DATA as ROT  # noqa: E402

MAPP = ROT / "facit"
INDEX = "^OMXSPI"
UA = {"User-Agent": "Mozilla/5.0"}
HORISONTER = [("6 mån", 182), ("1 år", 365), ("2 år", 730), ("3 år", 1095), ("5 år", 1826)]
MINSTA_ALDER = 91  # dagar innan en händelse räknas i sammanfattningen

TYPNAMN = {
    "radar_ny": "Kom in på radarn (minst 3 poäng)",
    "radar_7": "Fick minst 7 poäng på radarn",
    "triage": "Triage",
    "bevaka": "Började bevakas",
    "kasta": "Kastades",
    "fas1": "Fas 1 (redo-poäng 10–14)",
    "fas2": "Fas 2 (redo-poäng minst 15)",
    "fas_ner": "Föll under 10 i redo-poäng",
    "steg": "Nytt turnaround-steg",
    "rod": "Trafikljuset blev rött",
    "gron": "Trafikljuset blev grönt",
}


def las(p, standard):
    try:
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else standard
    except (OSError, ValueError):
        return standard


def skriv(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")


def redo_summa(s):
    r = s.get("redo") or {}
    return sum(p.get("poang", 0) for p in r.get("punkter", [])) if r.get("punkter") else None


def fas(s):
    if s.get("spar", "vandning") != "vandning":
        return None
    p = redo_summa(s)
    return None if p is None else (2 if p >= 15 else 1 if p >= 10 else 0)


# ---------- läget nu ----------

def nulage():
    """Ett läge per bolag. Nyckeln är ISIN när den finns, så att radar och bevakning hör ihop."""
    lage = {}
    for p in sorted(ROT.glob("bolag/*/status.json")):
        s = las(p, {})
        nyckel = s.get("isin") or p.parent.name
        lage[nyckel] = {
            "namn": s.get("namn", p.parent.name), "slug": p.parent.name, "isin": s.get("isin"),
            "symbol": (s.get("kallor_bevakning") or {}).get("yahoo"),
            "beslut": s.get("beslut"), "beslut_datum": s.get("beslut_datum"),
            "fas": fas(s), "redo_datum": (s.get("redo") or {}).get("datum"), "redo": redo_summa(s),
            "steg": s.get("steg") if s.get("spar", "vandning") == "vandning" else None,
            "trafikljus": s.get("trafikljus"),
        }
    radar = las(ROT / "radar" / "radar.json", {}).get("bolag", [])
    triage = las(ROT / "radar" / "triage.json", {}).get("bolag", {})
    for r in radar:
        isin = next((x.get("isin") for x in r.get("signaler", []) if x.get("isin")), None)
        nyckel = isin or r["nyckel"]
        b = lage.setdefault(nyckel, {"namn": r["bolag"], "isin": isin})
        b.update({"radar_nyckel": r["nyckel"], "radar_poang": r["poang"], "radar_typer": r.get("typer", []),
                  "radar_signaler": [(x.get("datum"), x.get("poang", 0)) for x in r.get("signaler", [])]})
        t = triage.get(r["nyckel"]) or r.get("triage") or {}
        if t.get("beslut"):
            b["triage"], b["triage_datum"] = t["beslut"], t.get("datum")
    for k, t in triage.items():
        if any(v.get("radar_nyckel") == k for v in lage.values()) or not t.get("beslut"):
            continue
        # Triagerat bolag som sedan blev bevakat: koppla till den bevakade mappen.
        mal = next((nk for nk, v in lage.items() if v.get("slug") == k), k)
        lage.setdefault(mal, {"namn": k}).update({"triage": t["beslut"], "triage_datum": t.get("datum"), "radar_nyckel": k})
    return lage


# ---------- händelser ----------

def ny_handelse(datum, typ, nyckel, b, detalj=None, uppskattad=False):
    return {"datum": datum, "typ": typ, "nyckel": nyckel, "namn": b.get("namn"), "isin": b.get("isin"),
            "slug": b.get("slug"), "detalj": detalj, "uppskattad": uppskattad or None}


def forsta_gang(signaler, grans):
    """Första datum då summan av radarpoängen nådde gränsen (uppskattning bakåt)."""
    summa = 0
    for d, p in sorted((x for x in signaler if x[0]), key=lambda x: x[0]):
        summa += p or 0
        if summa >= grans:
            return d
    return None


def bakat(lage):
    """Första körningen: återskapa det som går ur befintliga data."""
    ut = []
    for k, b in lage.items():
        if b.get("radar_signaler"):
            for typ, grans in (("radar_ny", 3), ("radar_7", 7)):
                d = forsta_gang(b["radar_signaler"], grans)
                if d and (b.get("radar_poang") or 0) >= grans:
                    ut.append(ny_handelse(d, typ, k, b, f'{b["radar_poang"]:g} poäng', True))
        if b.get("triage"):
            ut.append(ny_handelse(b.get("triage_datum") or date.today().isoformat(), "triage", k, b, b["triage"]))
        if b.get("beslut") in ("Bevaka", "Avvakta"):
            ut.append(ny_handelse(b.get("beslut_datum") or date.today().isoformat(), "bevaka", k, b, b["beslut"]))
        elif b.get("beslut") == "Kasta":
            ut.append(ny_handelse(b.get("beslut_datum") or date.today().isoformat(), "kasta", k, b))
        if b.get("fas") in (1, 2):
            ut.append(ny_handelse(b.get("redo_datum") or date.today().isoformat(), f'fas{b["fas"]}', k, b, f'{b["redo"]} poäng'))
        if b.get("trafikljus") == "rod":
            ut.append(ny_handelse(date.today().isoformat(), "rod", k, b))
    return ut


def jamfor(fore, nu):
    idag = date.today().isoformat()
    ut = []
    for k, b in nu.items():
        f = fore.get(k, {})
        p, fp = b.get("radar_poang") or 0, f.get("radar_poang") or 0
        if p >= 3 and fp < 3 and not f.get("radar_sedd"):
            ut.append(ny_handelse(idag, "radar_ny", k, b, f"{p:g} poäng"))
        if p >= 7 and fp < 7 and not f.get("radar_7_sedd"):
            ut.append(ny_handelse(idag, "radar_7", k, b, f"{p:g} poäng"))
        if b.get("triage") and b.get("triage") != f.get("triage"):
            ut.append(ny_handelse(b.get("triage_datum") or idag, "triage", k, b, b["triage"]))
        if b.get("beslut") != f.get("beslut"):
            if b.get("beslut") in ("Bevaka", "Avvakta") and f.get("beslut") not in ("Bevaka", "Avvakta"):
                ut.append(ny_handelse(idag, "bevaka", k, b, b["beslut"]))
            elif b.get("beslut") == "Kasta":
                ut.append(ny_handelse(idag, "kasta", k, b))
        nf, ff = b.get("fas"), f.get("fas")
        if nf is not None and nf != ff:
            if nf == 2:
                ut.append(ny_handelse(idag, "fas2", k, b, f'{b["redo"]} poäng'))
            elif nf == 1 and (ff or 0) < 1:
                ut.append(ny_handelse(idag, "fas1", k, b, f'{b["redo"]} poäng'))
            elif nf == 0 and (ff or 0) >= 1:
                ut.append(ny_handelse(idag, "fas_ner", k, b, f'{b["redo"]} poäng'))
        if b.get("steg") and f.get("steg") and b["steg"] > f["steg"]:
            ut.append(ny_handelse(idag, "steg", k, b, f'{f["steg"]} → {b["steg"]}'))
        if b.get("trafikljus") != f.get("trafikljus") and b.get("trafikljus") in ("rod", "gron") and f.get("trafikljus"):
            ut.append(ny_handelse(idag, b["trafikljus"], k, b, f'från {f["trafikljus"]}'))
    return ut


def minne(fore, nu):
    """Kom ihåg att ett bolag redan har varit på radarn, så att det inte räknas som nytt igen när poängen pendlar."""
    for k, b in nu.items():
        f = fore.get(k, {})
        b["radar_sedd"] = f.get("radar_sedd") or (b.get("radar_poang") or 0) >= 3
        b["radar_7_sedd"] = f.get("radar_7_sedd") or (b.get("radar_poang") or 0) >= 7
        b.pop("radar_signaler", None)
    return nu


# ---------- kurser ----------

def hamta(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20) as r:
        return json.loads(r.read())


def symbol(h, b, symboler):
    if b.get("symbol"):
        return b["symbol"]
    nyckel = h.get("isin") or h.get("namn")
    if nyckel in symboler:
        return symboler[nyckel]
    sym = None
    for q in [x for x in (h.get("isin"), h.get("namn")) if x]:
        try:
            res = hamta("https://query1.finance.yahoo.com/v1/finance/search?" + urllib.parse.urlencode({"q": q, "quotesCount": 8, "newsCount": 0}))
        except Exception:
            continue
        st = [x["symbol"] for x in res.get("quotes", []) if str(x.get("symbol", "")).endswith((".ST", ".HE", ".CO", ".OL"))]
        if st:
            sym = st[0]
            break
    symboler[nyckel] = sym
    return sym


def serie(sym, fran, fel):
    """Dagskurser från och med datumet `fran`. Hämtas högst en gång per dag."""
    fil = MAPP / "kurser" / (sym.replace("^", "_").replace("/", "_") + ".json")
    c = las(fil, {})
    if c.get("hamtad") == date.today().isoformat() and c.get("fran", "9999") <= fran:
        return c
    start = int(datetime.fromisoformat(fran).timestamp()) - 10 * 86400
    try:
        r = hamta(f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(sym)}?period1={start}&period2={int(datetime.now().timestamp())}&interval=1d")["chart"]["result"][0]
    except Exception as e:  # noqa: BLE001
        fel.append(f"{sym}: {e}")
        return c or None
    ts = r.get("timestamp") or []
    cl = (r.get("indicators", {}).get("quote") or [{}])[0].get("close") or []
    ftd = r["meta"].get("firstTradeDate")
    c = {"hamtad": date.today().isoformat(), "fran": fran, "valuta": r["meta"].get("currency"),
         "noterad": date.fromtimestamp(ftd).isoformat() if ftd else None,
         "serie": [[date.fromtimestamp(t).isoformat(), round(v, 4)] for t, v in zip(ts, cl) if v is not None]}
    skriv(fil, c)
    return c


def kurs_vid(s, datum):
    """Stängningskursen på datumet, eller närmaste handelsdag efter."""
    for d, v in s:
        if d >= datum:
            return d, v
    return None


def senast(s):
    return s[-1] if s else None


def utfall(h, ks, idx):
    if not ks or not ks.get("serie"):
        return None
    s, i = ks["serie"], (idx or {}).get("serie") or []
    start = kurs_vid(s, h["datum"])
    if not start:
        return None
    nu = senast(s)
    istart, inu = kurs_vid(i, start[0]), senast(i)
    pct = lambda a, b: round((b / a - 1) * 100, 1)  # noqa: E731
    r = {"kurs_vid": start[1], "kurs_datum": start[0], "kurs_nu": nu[1], "nu_datum": nu[0],
         "alder_dagar": (date.fromisoformat(nu[0]) - date.fromisoformat(start[0])).days,
         "avk": pct(start[1], nu[1]), "index": pct(istart[1], inu[1]) if istart and inu else None,
         "noterad": ks.get("noterad")}
    r["mot_index"] = round(r["avk"] - r["index"], 1) if r["index"] is not None else None
    r["horisonter"] = {}
    for namn, dagar in HORISONTER:
        mal = (date.fromisoformat(start[0]) + timedelta(days=dagar)).isoformat()
        if mal > nu[0]:
            break
        e, ie = kurs_vid(s, mal), kurs_vid(i, mal)
        if e:
            r["horisonter"][namn] = {"avk": pct(start[1], e[1]), "mot_index": round(pct(start[1], e[1]) - pct(istart[1], ie[1]), 1) if istart and ie else None}
    return r


def sammanfatta(rader):
    grupper = {}
    for r in rader:
        nyckel = r["typ"] + (f':{r["detalj"]}' if r["typ"] == "triage" else "")
        grupper.setdefault(nyckel, []).append(r)
    ut = []
    for nyckel, rr in grupper.items():
        typ, _, detalj = nyckel.partition(":")
        mogna = [x for x in rr if x.get("utfall") and x["utfall"]["alder_dagar"] >= MINSTA_ALDER]
        mi = [x["utfall"]["mot_index"] for x in mogna if x["utfall"]["mot_index"] is not None]
        ut.append({"typ": typ, "detalj": detalj or None, "namn": TYPNAMN.get(typ, typ) + (f": {detalj}" if detalj else ""),
                   "antal": len(rr), "mogna": len(mogna),
                   "median_avk": round(statistics.median([x["utfall"]["avk"] for x in mogna]), 1) if mogna else None,
                   "median_mot_index": round(statistics.median(mi), 1) if mi else None,
                   "andel_slog_index": round(100 * sum(1 for v in mi if v > 0) / len(mi)) if mi else None})
    ordning = list(TYPNAMN)
    return sorted(ut, key=lambda x: (ordning.index(x["typ"]) if x["typ"] in ordning else 99, x["detalj"] or ""))


def main(argv):
    MAPP.mkdir(exist_ok=True)
    hfil, lfil, sfil = MAPP / "handelser.json", MAPP / "lage.json", MAPP / "symboler.json"
    logg = las(hfil, {"handelser": []})["handelser"]
    nu = nulage()
    fore = las(lfil, None)
    nya = bakat(nu) if fore is None else jamfor(fore, nu)
    if nya:
        logg += nya
        logg.sort(key=lambda h: (h["datum"], h["typ"]))
        skriv(hfil, {"om": "Facit: när verktyget sa vad. Raderas aldrig.", "handelser": logg})
    skriv(lfil, minne(fore or {}, nu))
    for h in nya:
        print(f'Ny i facit: {h["datum"]} {TYPNAMN.get(h["typ"], h["typ"])} – {h["namn"]}{" (" + h["detalj"] + ")" if h.get("detalj") else ""}')
    if "--utan-kurser" in argv:
        return
    symboler, fel = las(sfil, {}), []
    forsta = min((h["datum"] for h in logg), default=date.today().isoformat())
    idx = serie(INDEX, forsta, fel)
    rader = []
    per_symbol = {}
    for h in logg:
        b = nu.get(h["nyckel"], {})
        sym = symbol(h, b, symboler)
        if sym:
            per_symbol[sym] = min(per_symbol.get(sym, "9999"), h["datum"])
        rader.append({**h, "symbol": sym})
    serier = {sym: serie(sym, fran, fel) for sym, fran in per_symbol.items()}
    for r in rader:
        r["utfall"] = utfall(r, serier.get(r["symbol"]), idx) if r["symbol"] else None
    # Samma bolag under två namn på radarn (samma symbol, typ och utfall): räkna bara det första.
    sett, unika = set(), []
    for r in rader:
        k = (r["symbol"], r["typ"], r.get("detalj")) if r["symbol"] else id(r)
        if k not in sett:
            sett.add(k)
            unika.append(r)
    rader = unika
    skriv(sfil, symboler)
    skriv(MAPP / "resultat.json", {"uppdaterad": datetime.now().strftime("%Y-%m-%d %H:%M"), "index": "OMX Stockholm PI",
                                   "minsta_alder_dagar": MINSTA_ALDER, "sammanfattning": sammanfatta(rader),
                                   "handelser": rader, "fel": fel[:20]})
    utan = sum(1 for r in rader if not r["utfall"])
    print(f"Facit: {len(rader)} händelser, {len(rader) - utan} med kurs." + (f" {len(fel)} fel vid kurshämtningen." if fel else ""))


if __name__ == "__main__":
    main(sys.argv[1:])
