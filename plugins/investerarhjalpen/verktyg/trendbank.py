#!/usr/bin/env python3
"""Informationsbanken för trendradarn (metod 21). Gratis, ingen AI.

Allt spaningen hittar sparas här som observationer, även sådant som inte hör till någon trend än.
Banken raderas aldrig. Den gör tre saker:
  1. Följer TIDSPLANER: vad någon har lovat ska hända när, och varje försening eller milstolpe efteråt.
  2. Räknar KÄLLFACIT: hur ofta olika slags aktörer (stater, storbolag, nystartade bolag …) håller sina tidsplaner.
  3. Föreslår KANDIDATER: ämnen (taggar) som dyker upp gång på gång utan att höra till någon trend.

Filer i datamappen:
  trender/bank/ÅÅÅÅ.jsonl          en observation per rad, aldrig raderad
  trender/_bank-sammanfattning.json det som sidan och spaningen läser

Kör från datamappen:
  python3 -I "$IH/verktyg/trendbank.py"                       sammanfattning
  python3 -I "$IH/verktyg/trendbank.py" --lagg-till obs.json  lägg till observationer (en JSON-lista)
  python3 -I "$IH/verktyg/trendbank.py" --trend <trend>       alla observationer för en trend
  python3 -I "$IH/verktyg/trendbank.py" --tagg <tagg>         alla observationer med en tagg

En observation:
  {"datum": "ÅÅÅÅ-MM-DD", "doman": "<se DOMANER>", "typ": "<se TYPER>", "rubrik": "kort, svenska",
   "text": "1–2 meningar", "aktor": "vem", "aktor_typ": "<se AKTORER>", "land": "US", "kalla": "url",
   "niva": "A|B|C|?", "trender": ["<trend>"], "taggar": ["mars", "rymdmat"],
   "tidsplan": {"vad": "det som ska hända", "lovat": "ÅÅÅÅ eller ÅÅÅÅ-MM"},      bara för typ tidsplan
   "galler": "<id för tidsplanen>", "nytt_datum": "ÅÅÅÅ", "utfall": "klar|struken"}  för uppföljningar
"""
import json
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rot import DATA as ROT  # noqa: E402

MAPP = ROT / "trender"
BANK = MAPP / "bank"

DOMANER = {
    "energi": "Energi och elnät", "transport": "Transport och resor", "halsa": "Hälsa, läkemedel och vård",
    "livsmedel": "Livsmedel, jordbruk och vatten", "rymd": "Rymd", "forsvar": "Försvar och säkerhet",
    "ai_data": "AI, data och mjukvara", "halvledare": "Halvledare och elektronik", "material": "Material och råvaror",
    "bygg": "Bygg, infrastruktur och städer", "finans": "Finans och betalningar", "demografi": "Demografi och arbete",
    "klimat": "Klimat och anpassning", "konsument": "Konsumenter och beteenden", "geopolitik": "Geopolitik och handel",
    "industri": "Industri och automation",
}
TYPER = {"beslut", "investering", "regel", "tidsplan", "milstolpe", "forsening", "bakslag", "siffra", "forskning", "ovrigt"}
AKTORER = {"stat": "Stater och myndigheter", "overstatlig": "EU, FN, NATO och liknande", "storbolag": "Storbolag",
           "startup": "Nystartade bolag", "forskning": "Universitet och forskare", "analytiker": "Analytiker och konsulter",
           "media": "Media", "ovrigt": "Övriga"}
KRAV = ("datum", "doman", "typ", "rubrik", "kalla")


def las_alla():
    obs = []
    for f in sorted(BANK.glob("*.jsonl")):
        for rad in f.read_text(encoding="utf-8").splitlines():
            if rad.strip():
                obs.append(json.loads(rad))
    return obs


def lagg_till(fil):
    nya = json.loads(Path(fil).read_text(encoding="utf-8"))
    nya = nya if isinstance(nya, list) else [nya]
    alla = las_alla()
    sedda = {(o.get("kalla"), o.get("rubrik")) for o in alla}
    idag = date.today().isoformat()
    lopnr = sum(1 for o in alla if o["id"].startswith(idag))
    BANK.mkdir(parents=True, exist_ok=True)
    tillagda, fel = 0, []
    with (BANK / f"{date.today().year}.jsonl").open("a", encoding="utf-8") as ut:
        for o in nya:
            saknas = [k for k in KRAV if not o.get(k)]
            if saknas:
                fel.append(f'{o.get("rubrik", "?")}: saknar {", ".join(saknas)}')
                continue
            if o["doman"] not in DOMANER:
                fel.append(f'{o["rubrik"]}: okänd domän {o["doman"]}')
                continue
            if o["typ"] not in TYPER:
                fel.append(f'{o["rubrik"]}: okänd typ {o["typ"]}')
                continue
            if o["typ"] == "tidsplan" and not (o.get("tidsplan") or {}).get("lovat"):
                fel.append(f'{o["rubrik"]}: en tidsplan behöver tidsplan.lovat')
                continue
            if (o.get("kalla"), o.get("rubrik")) in sedda:
                continue
            lopnr += 1
            o = {"id": f"{idag}-{lopnr:03d}", "observerad": idag, **o}
            ut.write(json.dumps(o, ensure_ascii=False) + "\n")
            sedda.add((o.get("kalla"), o.get("rubrik")))
            tillagda += 1
    print(f"Lade till {tillagda} observationer." + (" Fel:\n  " + "\n  ".join(fel) if fel else ""))


def ar_av(s):
    try:
        return int(str(s)[:4])
    except (TypeError, ValueError):
        return None


def tidsplaner(obs):
    """Varje tidsplan med sin historia: ursprungligt datum, förseningar och utfall."""
    uppf = defaultdict(list)
    for o in obs:
        if o.get("galler"):
            uppf[o["galler"]].append(o)
    idag = date.today().isoformat()
    ut = []
    for o in obs:
        if o.get("typ") != "tidsplan":
            continue
        tp = o["tidsplan"]
        historik = sorted(uppf.get(o["id"], []), key=lambda x: x["datum"])
        nu = tp["lovat"]
        utfall = None
        for h in historik:
            if h.get("nytt_datum"):
                nu = h["nytt_datum"]
            if h.get("utfall"):
                utfall = h["utfall"]
                klar_datum = h["datum"]
        forsening = None
        if utfall == "klar":
            forsening = max(0, (ar_av(klar_datum) or 0) - (ar_av(tp["lovat"]) or 0))
        elif nu != tp["lovat"]:
            forsening = (ar_av(nu) or 0) - (ar_av(tp["lovat"]) or 0)
        ut.append({"id": o["id"], "vad": tp["vad"], "aktor": o.get("aktor"), "aktor_typ": o.get("aktor_typ", "ovrigt"),
                   "trender": o.get("trender", []), "lovat": tp["lovat"], "nu": nu, "utfall": utfall,
                   "forsening_ar": forsening, "antal_forseningar": sum(1 for h in historik if h.get("nytt_datum")),
                   "forfallen": utfall is None and str(nu) < idag[:len(str(nu))], "kalla": o.get("kalla"), "datum": o["datum"]})
    return ut


def kallfacit(tp):
    """Hur ofta håller olika slags aktörer sina tidsplaner? Bara avslutade tidsplaner räknas."""
    per = defaultdict(list)
    for t in tp:
        if t["utfall"] in ("klar", "struken"):
            per[t["aktor_typ"]].append(t)
    ut = []
    for typ, rr in per.items():
        klara = [r for r in rr if r["utfall"] == "klar"]
        ut.append({"aktor_typ": typ, "namn": AKTORER.get(typ, typ), "avslutade": len(rr),
                   "i_tid": sum(1 for r in klara if not r["forsening_ar"]),
                   "andel_i_tid": round(100 * sum(1 for r in klara if not r["forsening_ar"]) / len(rr)),
                   "struken": sum(1 for r in rr if r["utfall"] == "struken"),
                   "snittforsening_ar": round(sum(r["forsening_ar"] or 0 for r in klara) / len(klara), 1) if klara else None})
    return sorted(ut, key=lambda x: -x["avslutade"])


def kandidater(obs):
    """Taggar som återkommer utan trend: minst 3 observationer, minst 2 slags typer och minst 2 källor."""
    trender = [json.loads(p.read_text(encoding="utf-8")) for p in MAPP.glob("*.json") if not p.name.startswith("_")]
    kanda = {t.lower() for tr in trender for t in tr.get("taggar", []) + [tr.get("slug", "")]}
    per = defaultdict(list)
    for o in obs:
        if not o.get("trender"):
            for t in o.get("taggar", []):
                if t.lower() not in kanda:
                    per[t.lower()].append(o)
    ut = []
    for tagg, rr in per.items():
        if len(rr) >= 3 and len({o["typ"] for o in rr}) >= 2 and len({o.get("kalla") for o in rr}) >= 2:
            ut.append({"tagg": tagg, "antal": len(rr), "domaner": sorted({o["doman"] for o in rr}),
                       "starkast": min((o.get("niva") or "?" for o in rr), key="ABC?".find), "senast": max(o["datum"] for o in rr)})
    return sorted(ut, key=lambda x: -x["antal"])


def sammanfatta():
    obs = las_alla()
    tp = tidsplaner(obs)
    per_trend = defaultdict(lambda: {"antal": 0, "senast": None})
    for o in obs:
        for t in o.get("trender", []):
            per_trend[t]["antal"] += 1
            per_trend[t]["senast"] = max(per_trend[t]["senast"] or "", o["datum"])
    s = {"uppdaterad": date.today().isoformat(), "antal": len(obs),
         "per_doman": dict(Counter(o["doman"] for o in obs)),
         "senaste_svep": max((o["observerad"] for o in obs), default=None),
         "per_trend": per_trend, "tidsplaner": tp, "kallfacit": kallfacit(tp), "kandidater": kandidater(obs),
         "domaner": DOMANER, "aktorer": AKTORER}
    MAPP.mkdir(exist_ok=True)
    (MAPP / "_bank-sammanfattning.json").write_text(json.dumps(s, ensure_ascii=False, indent=1), encoding="utf-8")
    return s


def main(argv):
    if "--lagg-till" in argv:
        lagg_till(argv[argv.index("--lagg-till") + 1])
    obs = las_alla()
    for flagga, falt in (("--trend", "trender"), ("--tagg", "taggar")):
        if flagga in argv:
            v = argv[argv.index(flagga) + 1].lower()
            for o in sorted(obs, key=lambda x: x["datum"]):
                if v in [x.lower() for x in o.get(falt, [])]:
                    print(f'{o["datum"]}  {o["typ"]:10s} {o["rubrik"]}  ({o.get("aktor", "")}, {o.get("niva", "?")})')
            return
    s = sammanfatta()
    print(f'Banken: {s["antal"]} observationer i {len(s["per_doman"])} av {len(DOMANER)} områden.')
    tomma = [DOMANER[d] for d in DOMANER if d not in s["per_doman"]]
    if tomma:
        print("Områden utan observationer än:", ", ".join(tomma))
    forfallna = [t for t in s["tidsplaner"] if t["forfallen"]]
    for t in forfallna:
        print(f'Följ upp: "{t["vad"]}" ({t["aktor"]}) skulle ha hänt {t["nu"]}. Id {t["id"]}')
    for k in s["kandidater"][:5]:
        print(f'Möjlig ny trend: "{k["tagg"]}" ({k["antal"]} observationer, {", ".join(k["domaner"])})')


if __name__ == "__main__":
    main(sys.argv[1:])
