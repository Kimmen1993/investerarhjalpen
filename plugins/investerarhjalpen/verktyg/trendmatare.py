#!/usr/bin/env python3
"""Trendmätaren: hämtar mätarna för varje trend i trender/ och räknar fram signalen. Gratis, ingen AI.

Mätarna beskrivs i trendens fil (trender/<trend>.json, "matare"). Värdena sparas i "serier" och
skrivs bara över av nyare hämtningar av samma källa; manuella värden rörs aldrig. Metod 21.

Källor (alla gratis, utan konto):
  openalex   antal forskningsartiklar per år     fraga = sökord
  kliniska   antal kliniska prövningar per år    fraga = sjukdom eller behandling
  owid       Our World in Data, värde per år     fraga = grafens namn, entitet = land eller "World"
  wikipedia  sidvisningar per år (snitt per dag) fraga = artikelns namn på engelska Wikipedia
  manuell    skrivs in av spaningen med källa    (inget hämtas)

Kör från datamappen:
  python3 -I "$IH/verktyg/trendmatare.py"            alla trender (hoppar över de som mätts senaste 6 dagarna)
  python3 -I "$IH/verktyg/trendmatare.py" --alla     mät alla oavsett datum
  python3 -I "$IH/verktyg/trendmatare.py" <trend>    bara en trend (filnamnet utan .json)
"""
import csv
import io
import json
import math
import sys
import time
import urllib.parse
import urllib.request
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rot import VERKTYG, DATA as ROT  # noqa: E402

MAPP = ROT / "trender"
UA = {"User-Agent": "Mozilla/5.0 (investerarhjalpen trendmatare)"}
HARDA = ("adoption", "kostnad", "pengar")  # det folk faktiskt köper, betalar eller beslutar
MJUKA = ("kunskap",)  # forskning och prövningar: viktigt tidigt, men räcker inte ensamt


def hamta(url, text=False):
    for forsok in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
                data = r.read().decode("utf-8")
                return data if text else json.loads(data)
        except urllib.error.HTTPError as e:
            if e.code == 429 and forsok < 2:
                time.sleep(5 * (forsok + 1))
                continue
            raise


# ---------- källor: returnerar {"ÅÅÅÅ": värde} ----------

def openalex(m):
    u = "https://api.openalex.org/works?" + urllib.parse.urlencode({"search": m["fraga"], "group_by": "publication_year", "per-page": 200})
    return {g["key"]: g["count"] for g in hamta(u)["group_by"] if str(g["key"]).isdigit() and int(g["key"]) >= 1990}


def kliniska(m):
    ut = {}
    for ar in range(m.get("fran_ar", 2005), date.today().year + 1):
        u = "https://clinicaltrials.gov/api/v2/studies?" + urllib.parse.urlencode({
            "query.term" if m.get("sok_i") == "allt" else "query.cond": m["fraga"],
            "filter.advanced": f"AREA[StartDate]RANGE[{ar}-01-01,{ar}-12-31]", "countTotal": "true", "pageSize": 1})
        ut[str(ar)] = hamta(u).get("totalCount", 0)
    return ut


def owid(m):
    t = hamta(f"https://ourworldindata.org/grapher/{m['fraga']}.csv?v=1&csvType=full&useColumnShortNames=true", text=True)
    rader = list(csv.reader(io.StringIO(t)))
    h = rader[0]
    kol = h.index(m["kolumn"]) if m.get("kolumn") in h else 3
    ent = m.get("entitet", "World")
    return {r[2]: float(r[kol]) for r in rader[1:] if r[0] == ent and r[kol] not in ("", None)}


def wikipedia(m):
    slut = date.today().replace(day=1) - timedelta(days=1)
    u = ("https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/"
         f"{urllib.parse.quote(m['fraga'], safe='')}/monthly/2015070100/{slut.strftime('%Y%m%d')}00")
    per_ar = {}
    for i in hamta(u).get("items", []):
        per_ar.setdefault(i["timestamp"][:4], []).append(i["views"])
    return {ar: round(sum(v) / (len(v) * 30.4), 1) for ar, v in per_ar.items()}


KALLOR = {"openalex": openalex, "kliniska": kliniska, "owid": owid, "wikipedia": wikipedia}


def baslinje():
    """Totalen per år för forskning och Wikipedia, så att ett ämnes andel kan räknas.
    Utan den ser allt ut att växa (forskningen ökar överlag) eller minska (färre läser Wikipedia)."""
    fil = MAPP / "_baslinje.json"
    bas = json.loads(fil.read_text(encoding="utf-8")) if fil.exists() else {}
    if bas.get("hamtad") == date.today().isoformat():
        return bas
    try:
        u = "https://api.openalex.org/works?" + urllib.parse.urlencode({"group_by": "publication_year", "per-page": 200})
        bas["openalex"] = {g["key"]: g["count"] for g in hamta(u)["group_by"] if str(g["key"]).isdigit()}
    except Exception:  # noqa: BLE001
        pass
    try:
        slut = date.today().replace(day=1) - timedelta(days=1)
        u = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/aggregate/en.wikipedia/all-access/user/monthly/2015070100/{slut.strftime('%Y%m%d')}00"
        per_ar = {}
        for i in hamta(u).get("items", []):
            per_ar.setdefault(i["timestamp"][:4], []).append(i["views"])
        bas["wikipedia"] = {ar: sum(v) / (len(v) * 30.4) for ar, v in per_ar.items()}
    except Exception:  # noqa: BLE001
        pass
    bas["hamtad"] = date.today().isoformat()
    fil.write_text(json.dumps(bas, ensure_ascii=False), encoding="utf-8")
    return bas


BAS = {}


def relativ(m, serie):
    """Forskning och läsning räknas som andel av totalen (per miljon), övriga mätare som de är."""
    b = BAS.get(m.get("kalla")) if m.get("kalla") in ("openalex", "wikipedia") else None
    if not b:
        return serie
    return {a: v / b[str(a)] * 1e6 for a, v in serie.items() if b.get(str(a))}


# ---------- signalen ----------

def fulla_ar(serie, till_ar):
    """Bara hela år, och bara till och med till_ar."""
    return {int(a): v for a, v in serie.items() if str(a).isdigit() and int(a) <= till_ar and v is not None}


def cagr(s, slut, ar=3):
    a, b = s.get(slut - ar), s.get(slut)
    if not a or not b or a <= 0 or b <= 0:
        return None
    return round(((b / a) ** (1 / ar) - 1) * 100, 1)


def s_kurva(andel):
    if andel is None:
        return None
    return "tidigt" if andel < 2 else "genombrott" if andel < 10 else "mainstream" if andel < 50 else "mattnad"


def signal(trend, till_ar=None):
    """Signalen som den såg ut vid slutet av till_ar (standard: förra året)."""
    till_ar = till_ar or date.today().year - 1
    ut = {"till_ar": till_ar, "matare": {}}
    tillvaxt = {"hard": [], "mjuk": [], "uppmarksamhet": []}
    for m in trend.get("matare", []):
        s = relativ(m, fulla_ar(trend.get("serier", {}).get(m["id"], {}).get("ar", {}), till_ar))
        if not s:
            continue
        slut = max(s)
        rad = {"senaste": s[slut], "ar": slut, "tillvaxt_3ar": cagr(s, slut), "tillvaxt_3ar_fore": cagr(s, slut - 3)}
        if rad["tillvaxt_3ar"] is not None and rad["tillvaxt_3ar_fore"] is not None:
            rad["acceleration"] = round(rad["tillvaxt_3ar"] - rad["tillvaxt_3ar_fore"], 1)
        typ = m.get("typ")
        if typ == "adoption":
            rad["s_kurva"] = s_kurva(s[slut])
            ut["s_kurva"], ut["andel"] = rad["s_kurva"], s[slut]
        vaxt = rad["tillvaxt_3ar"]
        if vaxt is not None:
            if typ == "kostnad":
                vaxt = -vaxt  # fallande kostnad är en positiv signal
            if typ in HARDA:
                tillvaxt["hard"].append(vaxt)
            elif typ in MJUKA:
                tillvaxt["mjuk"].append(vaxt)
            elif typ == "uppmarksamhet":
                tillvaxt["uppmarksamhet"].append(vaxt)
        ut["matare"][m["id"]] = rad
    medel = lambda v: round(sum(v) / len(v), 1) if v else None  # noqa: E731
    ut["hard_tillvaxt"] = medel(tillvaxt["hard"])
    ut["kunskap_tillvaxt"] = medel(tillvaxt["mjuk"])
    ut["substans_tillvaxt"] = ut["hard_tillvaxt"] if ut["hard_tillvaxt"] is not None else ut["kunskap_tillvaxt"]
    ut["uppmarksamhet_tillvaxt"] = medel(tillvaxt["uppmarksamhet"])
    ut["saknar_hard_data"] = not tillvaxt["hard"] and ut.get("andel") is None
    # Hypevarning bara när det finns hårda data att jämföra med (annars går det inte att bedöma).
    # Hypevarning kräver en mätare för adoption: uppmärksamheten rusar medan nästan ingen köper.
    ut["hypevarning"] = bool(ut.get("s_kurva") == "tidigt" and tillvaxt["uppmarksamhet"] and tillvaxt["hard"]
                             and ut["uppmarksamhet_tillvaxt"] > ut["hard_tillvaxt"] + 25)
    return ut


def profil(sig):
    """Siffror att jämföra trender med, på jämförbar skala: andel (log), hårda data, kunskap och uppmärksamhet."""
    andel = sig.get("andel")
    skala = lambda v: v / 50 if v is not None else None  # noqa: E731
    return [math.log10(andel + 0.1) if andel is not None else None, skala(sig.get("hard_tillvaxt")),
            skala(sig.get("kunskap_tillvaxt")), skala(sig.get("uppmarksamhet_tillvaxt"))]


def liknar(sig, historia):
    """Vilket historiskt läge liknar trenden mest? Jämför de siffror som finns hos båda (minst två)."""
    p = profil(sig)
    ut = []
    for h in historia:
        for ar in h.get("jamfor_ar", []):
            q = profil(signal(h, ar))
            par = [(a, b) for a, b in zip(p, q) if a is not None and b is not None]
            # Kräv minst två gemensamma siffror, varav en hård (andel eller hårda data). Annars går det inte att jämföra.
            if len(par) < 2 or not any(x is not None and y is not None for x, y in zip(p[:2], q[:2])):
                continue
            avst = math.sqrt(sum((a - b) ** 2 for a, b in par) / len(par))
            ut.append({"trend": h["namn"], "slug": h["slug"], "ar": ar, "utfall": (h.get("facit") or {}).get("utfall"),
                       "avstand": round(avst, 2), "jamfort": len(par)})
    return sorted(ut, key=lambda x: x["avstand"])[:3]


# ---------- körning ----------

def mat(trend, fel):
    serier = trend.setdefault("serier", {})
    for m in trend.get("matare", []):
        if m.get("kalla") in (None, "manuell"):
            continue
        try:
            varden = KALLOR[m["kalla"]](m)
        except Exception as e:  # noqa: BLE001
            fel.append(f'{trend["slug"]}/{m["id"]}: {e}')
            continue
        gammal = serier.get(m["id"], {}).get("ar", {})
        serier[m["id"]] = {"kalla": m["kalla"], "hamtad": date.today().isoformat(), "ar": {**gammal, **{str(k): v for k, v in varden.items()}}}


def main(argv):
    # Historiebiblioteket följer med tillägget; en egen kopia i datamappen samlar mätvärdena.
    (MAPP / "historia").mkdir(parents=True, exist_ok=True)
    for f in sorted((VERKTYG / "trendhistoria").glob("*.json")):
        mal = MAPP / "historia" / f.name
        if not mal.exists():
            mal.write_text(f.read_text(encoding="utf-8"), encoding="utf-8")
        else:  # nya texter från tillägget, men behåll mätvärdena
            ny, gammal = json.loads(f.read_text(encoding="utf-8")), json.loads(mal.read_text(encoding="utf-8"))
            ny.update({k: gammal[k] for k in ("serier", "signal", "signal_vid", "matt") if k in gammal})
            mal.write_text(json.dumps(ny, ensure_ascii=False, indent=1), encoding="utf-8")
    alla = "--alla" in argv
    bara = [a for a in argv if not a.startswith("--")]
    BAS.update(baslinje())
    historia = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((MAPP / "historia").glob("*.json"))]
    fel = []
    filer = [f for f in sorted(MAPP.glob("*.json")) + sorted((MAPP / "historia").glob("*.json")) if not f.name.startswith("_")]
    for p in filer:
        if bara and p.stem not in bara:
            continue
        t = json.loads(p.read_text(encoding="utf-8"))
        t.setdefault("slug", p.stem)
        senast = t.get("matt")
        if not alla and not bara and senast and senast > (date.today() - timedelta(days=6)).isoformat():
            continue
        mat(t, fel)
        t["matt"] = date.today().isoformat()
        t["signal"] = signal(t)
        if t.get("status") != "historisk":
            t["signal"]["liknar"] = liknar(t["signal"], historia)
            logg = t.setdefault("signal_historik", [])
            manad = date.today().isoformat()[:7]
            kort = {"datum": date.today().isoformat(), "andel": t["signal"].get("andel"), "hard": t["signal"]["hard_tillvaxt"], "kunskap": t["signal"]["kunskap_tillvaxt"],
                    "uppmarksamhet": t["signal"]["uppmarksamhet_tillvaxt"], "hypevarning": t["signal"]["hypevarning"]}
            if logg and logg[-1]["datum"][:7] == manad:
                logg[-1] = kort
            else:
                logg.append(kort)
        else:
            t["signal_vid"] = {str(a): signal(t, a) for a in t.get("jamfor_ar", [])}
        p.write_text(json.dumps(t, ensure_ascii=False, indent=1), encoding="utf-8")
        s = t["signal"]
        print(f'{t["namn"][:40]:40s} hårda {s["hard_tillvaxt"]} %/år, kunskap {s["kunskap_tillvaxt"]} %/år, uppmärksamhet {s["uppmarksamhet_tillvaxt"]} %/år'
              + (f', andel {s["andel"]} % ({s["s_kurva"]})' if s.get("andel") is not None else "")
              + (" HYPEVARNING" if s["hypevarning"] else "") + (" (saknar hårda data)" if s["saknar_hard_data"] else ""))
    if fel:
        print("Fel:", *fel, sep="\n  ")


if __name__ == "__main__":
    main(sys.argv[1:])
