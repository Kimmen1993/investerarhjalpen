#!/usr/bin/env python3
"""Fondverktyget: hämtar Finansinspektionens kvartalsdata om svenska fonders innehav.

Gratis och utan AI. FI publicerar varje svensk värdepappersfonds hela innehav, avgifter,
jämförelseindex, aktiv risk och standardavvikelse en gång per kvartal (med några månaders
fördröjning). Bara svenskregistrerade fonder finns med.

Kör från datamappen:
  python3 -I fonder.py                      hämta nytt kvartal om det finns och uppdatera allt
  python3 -I fonder.py --sok "småbolag"     sök fonder i senaste kvartalet
  python3 -I fonder.py --lagg-till SE0011527613 [ISIN ...]   börja följa fonder (ISIN eller exakt namn)
  python3 -I fonder.py --ta-bort SE0011527613                sluta följa en fond
  python3 -I fonder.py --utlandsk ISIN --namn "Namn" [--index "MSCI World"] [--avgift 0.2]
                       [--kalla URL] [--ersattning auto|FI-ISIN]
                        följ en fond som inte finns i FI:s data (registrerad utomlands). Innehaven hämtas från
                        fondbolagets Excel/CSV-fil (--kalla), annars lånas de från en svensk indexfond med
                        liknande index (--ersattning). Claude kan också skriva fonder/<fond>/innehav-manuellt.json
                        efter att ha läst fondbolagets månadsrapport.

Skriver:
  fonder/fonder.json            vilka fonder som följs (användarens val)
  fonder/<slug>/fond.json       faktaruta, innehav, sektorer, länder, köpt/sålt, överlapp
  bolag/<namn>/fondagare.json   vilka svenska fonder som äger ett bevakat bolag, och förändringen
  fonder/fondsignaler.json      bevakade bolag där fonderna ökat eller minskat mest
"""
import json
import re
import sys
import unicodedata
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import csv
import io
import zipfile
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rot import DATA as ROT  # noqa: E402  (ROT = användarens datamapp)

UA = {"User-Agent": "Mozilla/5.0 (investerarhjalpen fonder)"}
LISTA = "https://fi.se/sv/vara-register/fondinnehav/fondinnehav-per-kvartal/"
NS = "{http://schemas.fi.se/publika/vardepappersfonder/20200331}"
MAPP = ROT / "fonder"
CACHE = MAPP / "_fi"
MAX_INNEHAV = 150  # så många innehav sparas per fond; resten slås ihop till "Övriga"

SEKTOR = {"10": "Energi", "15": "Material", "20": "Industri", "25": "Sällanköpsvaror", "30": "Dagligvaror",
          "35": "Hälsovård", "40": "Finans", "45": "IT", "50": "Kommunikation", "55": "Kraftförsörjning",
          "60": "Fastigheter"}


def hamta(url, timeout=60):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def slug(namn):
    s = unicodedata.normalize("NFKD", namn.lower()).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def tal(x):
    try:
        return float(str(x).replace(",", "."))
    except (TypeError, ValueError):
        return None


# ---------- FI:s filer ----------

def fi_filer():
    """Lista över kvartalsfiler på FI:s sida, nyast först: [(kvartal, filnamn)]."""
    html = hamta(LISTA).decode("utf-8", "replace")
    namn = re.findall(r"FondInnehavLista/download\?filnamn=([^\"'&<>]+?\.zip)", html)
    ut, sedda = [], set()
    for n in namn:
        n = urllib.parse.unquote(n.replace("&amp;", "&"))
        m = re.search(r"(\d{4}Q[1-4])", n)
        if m and m.group(1) not in sedda:
            sedda.add(m.group(1))
            ut.append((m.group(1), n))
    return sorted(ut, reverse=True)


def zip_for(kvartal, filnamn):
    """Hämtar zipfilen om den inte redan finns (en ny revidering ger ett nytt filnamn)."""
    CACHE.mkdir(parents=True, exist_ok=True)
    lokal = CACHE / (filnamn.replace(" ", "_").replace(":", "."))
    if not lokal.exists():
        for gammal in CACHE.glob(f"Fondinnehav_{kvartal}_*.zip"):
            gammal.unlink()
        url = "https://fi.se/FondInnehavLista/download?filnamn=" + urllib.parse.quote(filnamn)
        data = hamta(url, timeout=180)
        if not data.startswith(b"PK"):
            raise RuntimeError(f"FI skickade ingen zipfil för {kvartal}")
        lokal.write_bytes(data)
        print(f"Hämtade {filnamn} ({len(data) // 1024} kB)")
    return lokal


def las_kvartal(zipfil):
    """Läser alla fonder i en kvartalsfil: {fond_isin: fond}."""
    fonder = {}
    with zipfile.ZipFile(zipfil) as z:
        for n in z.namelist():
            if not n.lower().endswith(".xml"):
                continue
            try:
                root = ET.fromstring(z.read(n))
            except ET.ParseError:
                continue
            kvartalsslut = root.findtext(f"{NS}Rapportinformation/{NS}Kvartalsslut")
            fondbolag = root.findtext(f"{NS}Bolagsinformation/{NS}Fondbolag_namn")
            for f in root.findall(NS + "Fondinformation"):
                namn = f.findtext(NS + "Fond_namn")
                isin = f.findtext(NS + "Fond_ISIN-kod")
                if not namn or not isin:
                    continue
                klasser = []
                for a in f.iter(NS + "Förvaltningsavgift"):
                    kn = a.findtext(NS + "Andelsklass_namn")
                    if kn is None:
                        continue
                    typ = a.find(NS + "Förvaltningsavgift_Typ")
                    klasser.append({"namn": kn.strip(),
                                    "fast": tal(typ.findtext(NS + "Förvaltningsavgift_fast")) if typ is not None else None,
                                    "prestation": typ is not None and typ.find(NS + "Förvaltningsavgift_Prestationsbaserad") is not None})
                utan = f.findtext(f"{NS}Förvaltningsavgift/{NS}UtanAndelsklasser/{NS}Förvaltningsavgift_fast")
                if not klasser and utan is not None:
                    klasser = [{"namn": "", "fast": tal(utan), "prestation": f.find(f"{NS}Förvaltningsavgift/{NS}UtanAndelsklasser/{NS}Förvaltningsavgift_Prestationsbaserad") is not None}]
                innehav = []
                for i in f.iter(NS + "FinansielltInstrument"):
                    innehav.append({"namn": (i.findtext(NS + "Instrumentnamn") or "").strip(),
                                    "isin": (i.findtext(NS + "ISIN-kod_instrument") or "").strip(),
                                    "typ": i.findtext(NS + "Tillgångsslag_enligt_LVF_5_kap") or "",
                                    "land": i.findtext(NS + "Landkod_Emittent") or "",
                                    "antal": tal(i.findtext(NS + "Antal")),
                                    "nominellt": tal(i.findtext(NS + "Nominellt_belopp")),
                                    "varde": tal(i.findtext(NS + "Marknadsvärde_instrument")) or 0,
                                    "andel": tal(i.findtext(NS + "Andel_av_fondförmögenhet_instrument")) or 0,
                                    "sektor": (i.findtext(f"{NS}Bransch/{NS}Branschkod_instrument") or "").strip()[:2]})
                index = [j.text.strip() for j in f.iter(NS + "Jämförelseindex") if j.text and j.text.strip()]
                fonder[isin] = {"namn": namn.strip(), "isin": isin, "fondbolag": fondbolag, "kvartal": kvartalsslut,
                                "formogenhet": tal(f.findtext(NS + "Fondförmögenhet")),
                                "likvida": tal(f.findtext(NS + "Likvida_medel")),
                                "std24": tal(f.findtext(NS + "Standardavvikelse_24_månader")),
                                "aktiv_risk": tal(f.findtext(NS + "Aktiv_risk")),
                                "index": [x for x in index if "saknas" not in x.lower()],
                                "avgift_klasser": klasser, "innehav": innehav}
    return fonder


# ---------- utländska fonder: fondbolagets fil, egen fil eller ersättningsfond ----------

# Svenska indexfonder i FI:s data som kan låna ut sina innehav till en utländsk fond med liknande index.
ERSATTARE = [
    (r"small ?cap|småbolag", r"world|global|developed|acwi|all country", "SE0010323675"),  # Handelsbanken Global Småbolag Index Criteria
    (r"s&p ?500|msci usa|\busa\b|us large|united states|amerika", None, "SE0007074083"),     # Swedbank Robur Access USA
    (r"msci europe|stoxx|europe|europa", None, "SE0026526568"),                              # SEB Europe Exposure
    (r"nordic|norden", None, "SE0010127894"),                                                # Handelsbanken Norden Index Criteria
    (r"omx|six|sweden|sverige", None, "SE0001718388"),                                      # Avanza Zero
    (r"msci world|developed|acwi|all country|world|global", None, "SE0007074059"),          # Swedbank Robur Access Global
]

ENG_SEKTOR = {"energy": "Energi", "materials": "Material", "industrials": "Industri", "consumer discretionary": "Sällanköpsvaror",
              "consumer staples": "Dagligvaror", "health care": "Hälsovård", "healthcare": "Hälsovård", "financials": "Finans",
              "information technology": "IT", "technology": "IT", "communication": "Kommunikation", "communication services": "Kommunikation",
              "utilities": "Kraftförsörjning", "real estate": "Fastigheter"}
ENG_LAND = {"united states": "US", "usa": "US", "japan": "JP", "united kingdom": "GB", "canada": "CA", "switzerland": "CH",
            "france": "FR", "germany": "DE", "netherlands": "NL", "australia": "AU", "sweden": "SE", "denmark": "DK",
            "ireland": "IE", "spain": "ES", "italy": "IT", "taiwan": "TW", "korea (south)": "KR", "south korea": "KR", "korea": "KR",
            "china": "CN", "india": "IN", "hong kong": "HK", "finland": "FI", "norway": "NO", "belgium": "BE", "singapore": "SG",
            "israel": "IL", "brazil": "BR", "luxembourg": "LU", "cayman islands": "KY", "bermuda": "BM", "jersey": "JE"}


def ersattare_for(index_text, nu):
    txt = (index_text or "").lower()
    for a, b, isin in ERSATTARE:
        if re.search(a, txt) and (b is None or re.search(b, txt)) and isin in nu:
            return isin
    return None


def xlsx_rader(data):
    """Läser första bladet i en Excel-fil (xlsx) med bara standardbiblioteket."""
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        S = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
        delade = []
        if "xl/sharedStrings.xml" in z.namelist():
            for si in ET.fromstring(z.read("xl/sharedStrings.xml")).iter(S + "si"):
                delade.append("".join(x.text or "" for x in si.iter(S + "t")))
        blad = sorted(n for n in z.namelist() if re.match(r"xl/worksheets/sheet\d+\.xml$", n))
        if not blad:
            return []
        rader = []
        for row in ET.fromstring(z.read(blad[0])).iter(S + "row"):
            celler = {}
            for c in row.iter(S + "c"):
                ref = re.match(r"([A-Z]+)", c.get("r", "A"))
                kol = 0
                for ch in ref.group(1):
                    kol = kol * 26 + ord(ch) - 64
                v = c.find(S + "v")
                if c.get("t") == "s" and v is not None:
                    val = delade[int(v.text)]
                elif c.get("t") == "inlineStr":
                    val = "".join(x.text or "" for x in c.iter(S + "t"))
                else:
                    val = v.text if v is not None else ""
                celler[kol - 1] = (val or "").strip()
            if celler:
                rader.append([celler.get(i, "") for i in range(max(celler) + 1)])
        return rader


def tabell_rader(data):
    if data[:2] == b"PK":
        return xlsx_rader(data)
    text = data.decode("utf-8-sig", "replace")
    if "<html" in text[:2000].lower():
        raise RuntimeError("Adressen gav en webbsida, inte en fil. Leta upp den direkta länken till Excel- eller CSV-filen.")
    prov = "\n".join(text.splitlines()[:40])
    sep = max([",", ";", "\t"], key=prov.count)
    return [[c.strip() for c in r] for r in csv.reader(io.StringIO(text), delimiter=sep)]


KOLUMNER = {"namn": r"^(name|namn|holding|holdings|security|security name|issuer|instrument|description|company|constituent|värdepapper|beskrivning)\b",
            "vikt": r"(weight|vikt|% of|%of|andel|% net|allocation|portfolio %|% av|percent)",
            "isin": r"\bisin\b", "land": r"(location|country|land|domicile)", "sektor": r"(sector|sektor|industry|bransch|gics)",
            "klass": r"(asset class|tillgångsslag|type)"}


def las_fondbolagets_fil(data):
    rader = tabell_rader(data)
    for i, r in enumerate(rader[:60]):
        low = [c.lower() for c in r]
        hitta = {k: next((j for j, c in enumerate(low) if re.search(m, c)), None) for k, m in KOLUMNER.items()}
        if hitta["namn"] is not None and hitta["vikt"] is not None:
            break
    else:
        raise RuntimeError("Hittade ingen tabell med namn och vikt i filen.")
    ut = []
    for r in rader[i + 1:]:
        g = lambda k: r[hitta[k]] if hitta[k] is not None and hitta[k] < len(r) else ""
        namn, vikt = g("namn"), tal(re.sub(r"[%\s]", "", g("vikt")))
        if not namn or vikt is None:
            continue
        if hitta["klass"] is not None and re.search(r"cash|kassa|futures|fx|currency|money market", g("klass"), re.I):
            continue
        land = g("land")
        ut.append({"namn": namn, "isin": g("isin").upper() if re.match(r"^[A-Z]{2}[A-Z0-9]{9}\d$", g("isin").upper()) else "",
                   "land": ENG_LAND.get(land.lower(), land[:2].upper() if len(land) == 2 else land),
                   "sektor": ENG_SEKTOR.get(g("sektor").lower(), ""), "andel": vikt, "typ": "ÖverlåtbartVärdepapper", "antal": None, "varde": 0})
    summa = sum(x["andel"] for x in ut)
    if 0.5 < summa < 1.5:  # vikter i decimalform
        for x in ut:
            x["andel"] *= 100
    if not ut:
        raise RuntimeError("Filen innehöll inga innehav med vikt.")
    return ut


def namn_nyckel(n):
    n = unicodedata.normalize("NFKD", str(n).lower()).encode("ascii", "ignore").decode()
    n = re.sub(r"\b(inc|corp|corporation|co|ltd|plc|ag|sa|se|nv|ab|asa|oyj|a/s|as|holdings?|group|the|class|cl|shs|reg|registered|ord|adr|common|stock|[abc])\b", " ", n)
    return re.sub(r"[^a-z0-9]+", "", n)


def namn_till_isin(nu):
    """Namn → ISIN från alla aktier i FI:s data, så att innehav utan ISIN kan kopplas ihop med samma bolag i andra fonder."""
    m = {}
    for f in nu.values():
        for i in f["innehav"]:
            if i["isin"] and i["typ"] == "ÖverlåtbartVärdepapper":
                m.setdefault(namn_nyckel(i["namn"]), i["isin"])
    return m


def utlandsk_fond(x, nu, mapp):
    """Bygger en fond i samma form som FI:s för en fond som inte finns i FI:s data."""
    bas = {"namn": x["namn"], "isin": x["isin"], "fondbolag": x.get("fondbolag"), "kvartal": None, "formogenhet": None,
           "likvida": None, "std24": None, "aktiv_risk": None, "index": [x["index"]] if x.get("index") else [],
           "avgift_klasser": [{"namn": "", "fast": x.get("avgift"), "prestation": False}] if x.get("avgift") is not None else []}
    manuell = mapp / "innehav-manuellt.json"
    if x.get("kalla"):
        cache = mapp / "fondbolagets-fil.json"
        gammal = json.loads(cache.read_text(encoding="utf-8")) if cache.exists() else None
        if not gammal or (datetime.now() - datetime.fromisoformat(gammal["hamtad"])).days >= 25:
            try:
                innehav = las_fondbolagets_fil(hamta(x["kalla"], timeout=120))
                gammal = {"hamtad": datetime.now().strftime("%Y-%m-%d"), "innehav": innehav}
                cache.write_text(json.dumps(gammal, ensure_ascii=False), encoding="utf-8")
            except Exception as e:  # noqa: BLE001 – fondbolagens sidor ändras; fall tillbaka på det som finns
                print(f"Kunde inte hämta innehaven för {x['namn']}: {e}")
        if gammal:
            return {**bas, "kvartal": gammal["hamtad"], "innehav": gammal["innehav"], "kalla_typ": "fondbolaget", "kalla_url": x["kalla"]}
    if manuell.exists():
        m = json.loads(manuell.read_text(encoding="utf-8"))
        innehav = [{"namn": i["namn"], "isin": i.get("isin", ""), "land": i.get("land", ""), "sektor": i.get("sektor", ""),
                    "andel": i["andel"], "typ": "ÖverlåtbartVärdepapper", "antal": None, "varde": 0} for i in m.get("innehav", [])]
        return {**bas, "kvartal": m.get("datum"), "innehav": innehav, "kalla_typ": "manuell", "kalla_url": m.get("kalla"),
                "sektorer_manuell": m.get("sektorer"), "lander_manuell": m.get("lander")}
    ers = x.get("ersattning")
    if ers == "auto":
        ers = ersattare_for(x.get("index") or x["namn"], nu)
    if ers and ers in nu:
        e = nu[ers]
        return {**bas, "kvartal": e["kvartal"], "innehav": e["innehav"], "kalla_typ": "ersattning",
                "ersattning": {"isin": e["isin"], "namn": e["namn"], "index": e["index"]}}
    return {**bas, "innehav": [], "kalla_typ": "saknas"}


# ---------- beräkningar ----------

def vanlig_avgift(klasser):
    """Avgiften för den andelsklass som privatpersoner oftast köper (A-klass i SEK), annars den högsta i SEK."""
    if not klasser:
        return None
    sek = [k for k in klasser if not re.search(r"\b(EUR|NOK|USD|DKK)\b", k["namn"], re.I)] or klasser
    for k in sek:
        if re.search(r"(^|\s)(A|A1)(\s+SEK)?$", k["namn"].strip(), re.I) or re.search(r"\bA\b(?!\d)", k["namn"]):
            return k
    return max(sek, key=lambda k: k["fast"] or 0)


def fondtyp(f):
    if f.get("kalla_typ") in ("ersattning", "fondbolaget", "manuell", "saknas"):
        return "Indexfond" if f.get("ersattning") or re.search(r"index|etf|msci|s&p|ftse|stoxx|solactive", (f["namn"] + " ".join(f.get("index") or [])).lower()) else "Aktivt förvaltad"
    namn = f["namn"].lower()
    ar = f.get("aktiv_risk")
    aktier = sum(i["andel"] for i in f["innehav"] if i["typ"] == "ÖverlåtbartVärdepapper" and not i.get("nominellt"))
    fondandel = sum(i["andel"] for i in f["innehav"] if "fondandel" in i["typ"].lower())
    if fondandel > 50:
        return "Fond i fonder"
    if aktier < 40:
        return "Ränte- eller blandfond"
    avg = (vanlig_avgift(f["avgift_klasser"]) or {}).get("fast")
    if "index" in namn or "zero" in namn or (ar is not None and ar < 1) or (ar is None and avg is not None and avg <= 0.3):
        return "Indexfond"
    return "Aktivt förvaltad"


def nyckel(i):
    return i["isin"] or i["namn"].upper()


def flode(nu, fore):
    """Hur mycket fonden har vuxit eller krympt genom in- och utflöden: medianförändringen av antalet aktier.
    En indexfond som får in pengar köper mer av allt; det är inget aktivt val och räknas bort."""
    if not fore:
        return 1.0
    a = {nyckel(i): i.get("antal") for i in fore["innehav"]}
    kvoter = sorted(i["antal"] / a[nyckel(i)] for i in nu["innehav"] if i.get("antal") and a.get(nyckel(i)))
    return kvoter[len(kvoter) // 2] if kvoter else 1.0


def forandring(nu, fore):
    """Köpt och sålt mellan två kvartal. Antalet aktier visar riktiga köp; andelen ändras även när kursen rör sig."""
    if not fore:
        return None
    a = {nyckel(i): i for i in fore["innehav"] if i["typ"] != "Övrigt"}
    b = {nyckel(i): i for i in nu["innehav"]}
    nya = [i for k, i in b.items() if k not in a and i["andel"] >= 0.05]
    salda = [i for k, i in a.items() if k not in b and i["andel"] >= 0.05]
    okat, minskat = [], []
    fl = flode(nu, fore)
    for k, i in b.items():
        g = a.get(k)
        if not g or not g.get("antal") or not i.get("antal"):
            continue
        d = i["antal"] / g["antal"] / fl - 1
        rad = {"namn": i["namn"], "isin": i["isin"], "andel": round(i["andel"], 2), "andel_fore": round(g["andel"], 2), "antal_pct": round(d * 100)}
        if d >= 0.15 and i["andel"] >= 0.3:
            okat.append(rad)
        elif d <= -0.15 and g["andel"] >= 0.3:
            minskat.append(rad)
    kort = lambda i: {"namn": i["namn"], "isin": i["isin"], "andel": round(i["andel"], 2)}
    return {"fran": fore["kvartal"], "flode_pct": round((fl - 1) * 100),
            "nya": [kort(i) for i in sorted(nya, key=lambda x: -x["andel"])[:15]],
            "salda": [kort(i) for i in sorted(salda, key=lambda x: -x["andel"])[:15]],
            "okat": sorted(okat, key=lambda x: -x["andel"])[:15],
            "minskat": sorted(minskat, key=lambda x: -x["andel_fore"])[:15]}


def overlapp(f1, f2):
    """Hur stor del av fonderna som äger samma sak: summan av den minsta vikten per innehav."""
    a = {nyckel(i): i["andel"] for i in f1["innehav"]}
    return round(sum(min(v, a.get(nyckel(i), 0)) for i in f2["innehav"] for v in [i["andel"]] if nyckel(i) in a), 1)


def bevakade_bolag():
    ut = {}
    for p in sorted(ROT.glob("bolag/*/status.json")):
        try:
            s = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if s.get("isin") and s.get("beslut") != "Kasta":
            ut[s["isin"]] = {"slug": p.parent.name, "namn": s.get("namn", p.parent.name)}
    return ut


def sammanfatta(f, fore, alla_foljda, bolag):
    vanlig = vanlig_avgift(f["avgift_klasser"])
    sorterade = sorted(f["innehav"], key=lambda i: -i["andel"])
    sektorer, lander = {}, {}
    for i in sorterade:
        sk = SEKTOR.get(i["sektor"], i["sektor"] if i["sektor"] in SEKTOR.values() else None)
        if sk:
            sektorer[sk] = sektorer.get(sk, 0) + i["andel"]
        if i["land"]:
            lander[i["land"]] = lander.get(i["land"], 0) + i["andel"]
    topp = sorterade[:MAX_INNEHAV]
    rest = sorterade[MAX_INNEHAV:]
    i_bevakade = [{"slug": bolag[i["isin"]]["slug"], "namn": bolag[i["isin"]]["namn"], "andel": round(i["andel"], 2)}
                  for i in sorterade if i["isin"] in bolag]
    return {
        "namn": f["namn"], "isin": f["isin"], "fondbolag": f["fondbolag"], "kvartal": f["kvartal"],
        "typ": fondtyp(f),
        "formogenhet_mdr": round(f["formogenhet"] / 1e9, 2) if f.get("formogenhet") else None,
        "likvida_pct": round(100 * f["likvida"] / f["formogenhet"], 1) if f.get("likvida") is not None and f.get("formogenhet") else None,
        "std24": f["std24"], "aktiv_risk": f["aktiv_risk"], "index": f["index"],
        "avgift": vanlig and vanlig["fast"], "avgift_klass": vanlig and vanlig["namn"],
        "prestationsavgift": any(k["prestation"] for k in f["avgift_klasser"]),
        "avgift_klasser": f["avgift_klasser"],
        "antal_innehav": len(sorterade),
        "topp10_pct": round(sum(i["andel"] for i in sorterade[:10]), 1),
        "sektorer": f.get("sektorer_manuell") or {k: round(v, 1) for k, v in sorted(sektorer.items(), key=lambda x: -x[1]) if v >= 0.05},
        "lander": f.get("lander_manuell") or {k: round(v, 1) for k, v in sorted(lander.items(), key=lambda x: -x[1])[:12] if v >= 0.05},
        "kalla_typ": f.get("kalla_typ", "FI"), "kalla_url": f.get("kalla_url"), "ersattning": f.get("ersattning"),
        "innehav": [{"namn": i["namn"], "isin": i["isin"], "land": i["land"], "sektor": SEKTOR.get(i["sektor"], i["sektor"] if i["sektor"] in SEKTOR.values() else ""),
                     "andel": round(i["andel"], 2), "typ": i["typ"]} for i in topp]
                   + ([{"namn": f"Övriga {len(rest)} innehav", "isin": "", "land": "", "sektor": "", "andel": round(sum(i["andel"] for i in rest), 2), "typ": "Övrigt"}] if rest else []),
        "forandring": forandring(f, fore),
        "overlapp": {o["isin"]: overlapp(f, o) for o in alla_foljda if o["isin"] != f["isin"]},
        "bevakade_bolag": i_bevakade,
    }


# ---------- huvudprogram ----------

def folj_lista():
    p = MAPP / "fonder.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"fonder": []}


def spara_folj(d):
    MAPP.mkdir(parents=True, exist_ok=True)
    (MAPP / "fonder.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")


def ladda(antal=2):
    filer = fi_filer()
    if not filer:
        raise RuntimeError("Hittade inga kvartalsfiler på FI:s sida. Sidan kan ha ändrats.")
    return [(k, las_kvartal(zip_for(k, n))) for k, n in filer[:antal]]


def rensa_fondnamn(n):
    n = unicodedata.normalize("NFKD", str(n).lower()).encode("ascii", "ignore").decode()
    n = re.sub(r"\b(sek|eur|nok|usd|acc|dis|klass|class|a|b|c|d)\d*\b", " ", n)
    return re.sub(r"[^a-z0-9]+", " ", n).strip()


def kontroll(fil):
    """Fondkollen för morgonkollen: vilka fonder äger användaren, och överlappar de?
    Läser en export av portföljen (transaktioner med isin, namn, typ och antal) och skriver bara varningar."""
    d = json.loads(Path(fil).read_text(encoding="utf-8"))
    netto = {}
    namn = {}
    for tx in d.get("transaktioner", []):
        k = tx.get("isin") or tx.get("namn")
        if not k:
            continue
        a = abs(tx.get("antal") or 0)
        typ = tx.get("typ")
        netto[k] = netto.get(k, 0) + (a if typ == "köp" else -a if typ == "sälj" else (tx.get("antal") or 0) if typ == "händelse" else 0)
        namn[k] = tx.get("namn") or namn.get(k)
    ager = [k for k, v in netto.items() if v > 1e-6]
    reg = json.loads((MAPP / "fondregister.json").read_text(encoding="utf-8"))["fonder"]
    folj = {x["isin"] for x in folj_lista()["fonder"]}
    hittade, saknas = [], []
    for k in ager:
        r = next((x for x in reg if x[0] == k), None) or next((x for x in reg if len(rensa_fondnamn(x[1])) > 6 and rensa_fondnamn(x[1]) == rensa_fondnamn(namn.get(k, ""))), None)
        if r:
            hittade.append(r)
        elif re.search(r"fond|fund|index|ucits|etf", str(namn.get(k, "")), re.I):
            saknas.append(namn.get(k, k))
    ut = {"fonder": [r[1] for r in hittade], "foljs_inte": [r[1] for r in hittade if r[0] not in folj],
          "foljs_inte_isin": [r[0] for r in hittade if r[0] not in folj], "utanfor_fi": saknas, "overlapp": []}
    for i, a in enumerate(hittade):
        for b in hittade[i + 1:]:
            fa = next((p for p in MAPP.glob("*/fond.json") if json.loads(p.read_text(encoding="utf-8")).get("isin") == a[0]), None)
            if fa:
                o = json.loads(fa.read_text(encoding="utf-8")).get("overlapp", {}).get(b[0])
                if o is not None and o >= 50:
                    ut["overlapp"].append({"fonder": [a[1], b[1]], "procent": o})
    print(json.dumps(ut, ensure_ascii=False, indent=1))


def main(argv):
    if "--kontroll" in argv:
        return kontroll(argv[argv.index("--kontroll") + 1])
    if "--sok" in argv:
        q = argv[argv.index("--sok") + 1].lower()
        kvartal, nu = ladda(1)[0]
        traff = sorted((f for f in nu.values() if q in f["namn"].lower() or q == f["isin"].lower()), key=lambda f: -(f["formogenhet"] or 0))
        print(f"{len(traff)} träffar i {kvartal}:")
        for f in traff[:40]:
            v = vanlig_avgift(f["avgift_klasser"])
            print(f"  {f['isin']}  {f['namn']}  ({f['fondbolag']}) · {(f['formogenhet'] or 0) / 1e9:.1f} mdr · avgift {v and v['fast']} % · {fondtyp(f)}")
        return
    d = folj_lista()
    if "--utlandsk" in argv:
        arg = lambda n: argv[argv.index(n) + 1] if n in argv else None
        isin = arg("--utlandsk")
        post = next((x for x in d["fonder"] if x["isin"] == isin), None) or {"isin": isin, "tillagd": datetime.now().strftime("%Y-%m-%d")}
        post["utlandsk"] = True
        for n, k in (("--namn", "namn"), ("--index", "index"), ("--kalla", "kalla"), ("--ersattning", "ersattning"), ("--fondbolag", "fondbolag")):
            if arg(n):
                post[k] = arg(n)
        if arg("--avgift"):
            post["avgift"] = tal(arg("--avgift"))
        if not post.get("namn"):
            print("Ange --namn för den utländska fonden.")
            return
        d["fonder"] = [x for x in d["fonder"] if x["isin"] != isin] + [post]
        spara_folj(d)
        print(f"Följer nu {post['namn']} ({isin}) som utländsk fond.")
    if "--lagg-till" in argv or "--ta-bort" in argv:
        tabort = "--ta-bort" in argv
        args = argv[argv.index("--ta-bort" if tabort else "--lagg-till") + 1:]
        kvartal, nu = ladda(1)[0]
        for a in args:
            f = nu.get(a) or next((x for x in nu.values() if x["namn"].lower() == a.lower()), None)
            if not f:
                print(f"Hittar ingen fond '{a}' i {kvartal}. Sök med --sok.")
                continue
            if tabort:
                d["fonder"] = [x for x in d["fonder"] if x["isin"] != f["isin"]]
                print(f"Följer inte längre {f['namn']}")
            elif not any(x["isin"] == f["isin"] for x in d["fonder"]):
                d["fonder"].append({"isin": f["isin"], "namn": f["namn"], "tillagd": datetime.now().strftime("%Y-%m-%d")})
                print(f"Följer nu {f['namn']} ({f['isin']})")
        spara_folj(d)

    data = ladda(2)
    (kv_nu, nu), (kv_fore, fore) = data[0], (data[1] if len(data) > 1 else (None, {}))
    bolag = bevakade_bolag()
    foljda = [nu[x["isin"]] for x in d["fonder"] if x["isin"] in nu and not x.get("utlandsk")]
    for x in d["fonder"]:
        if x.get("utlandsk"):
            m = MAPP / slug(x["namn"])
            m.mkdir(parents=True, exist_ok=True)
            foljda.append(utlandsk_fond(x, nu, m))
    saknas = [x["namn"] for x in d["fonder"] if x["isin"] not in nu and not x.get("utlandsk")]
    n2i = namn_till_isin(nu)
    for f in foljda:  # koppla innehav utan ISIN till rätt bolag via namnet
        f["innehav"] = [dict(i, isin=i["isin"] or n2i.get(namn_nyckel(i["namn"]), "")) for i in f["innehav"]]
    for f in foljda:
        ut = sammanfatta(f, fore.get(f["isin"]) if f.get("kalla_typ", "FI") == "FI" else None, foljda, bolag)
        mapp = MAPP / slug(f["namn"])
        mapp.mkdir(parents=True, exist_ok=True)
        gammal = mapp / "fond.json"
        extra = {}
        if gammal.exists():  # behåll det Claude har skrivit (klarspråk, panel, prognos)
            g = json.loads(gammal.read_text(encoding="utf-8"))
            extra = {k: v for k, v in g.items() if k in ("enkelt", "panel", "prognos", "avgift_manuell", "anteckning", "tema")}
        gammal.write_text(json.dumps({**ut, **extra}, ensure_ascii=False, indent=1), encoding="utf-8")

    # Fondägare för varje bevakat bolag: alla svenska fonder, inte bara de som följs.
    signaler = []
    floden = {}
    for isin, b in bolag.items():
        agare = []
        for f in nu.values():
            i = next((x for x in f["innehav"] if x["isin"] == isin), None)
            g = fore.get(f["isin"])
            gi = next((x for x in g["innehav"] if x["isin"] == isin), None) if g else None
            if not i and not gi:
                continue
            if f["isin"] not in floden:
                floden[f["isin"]] = flode(f, g)
            fl = floden[f["isin"]]
            agare.append({"fond": f["namn"], "fond_isin": f["isin"], "fondbolag": f["fondbolag"], "typ": fondtyp(f),
                          "andel_av_fonden": round(i["andel"], 2) if i else 0, "antal": i and i["antal"],
                          "antal_fore": gi and gi["antal"], "varde_mkr": round((i["varde"] if i else 0) / 1e6, 1),
                          "status": "ny" if i and not gi else "salt" if gi and not i else
                                    ("okat" if gi["antal"] and i["antal"] and i["antal"] > gi["antal"] * fl * 1.1 else
                                     "minskat" if gi["antal"] and i["antal"] and i["antal"] < gi["antal"] * fl * 0.9 else "oforandrat")})
        agare.sort(key=lambda x: -x["varde_mkr"])
        mapp = ROT / "bolag" / b["slug"]
        ut = {"kvartal": kv_nu, "jamfort_med": kv_fore, "antal_fonder": sum(1 for a in agare if a["status"] != "salt"),
              "antal_fonder_fore": sum(1 for a in agare if a["status"] != "ny"),
              "varde_mkr": round(sum(a["varde_mkr"] for a in agare), 1), "agare": agare[:40]}
        (mapp / "fondagare.json").write_text(json.dumps(ut, ensure_ascii=False, indent=1), encoding="utf-8")
        netto = sum(1 for a in agare if a["status"] in ("ny", "okat")) - sum(1 for a in agare if a["status"] in ("salt", "minskat"))
        signaler.append({"slug": b["slug"], "namn": b["namn"], "antal_fonder": ut["antal_fonder"],
                         "antal_fonder_fore": ut["antal_fonder_fore"], "netto_kopare": netto, "varde_mkr": ut["varde_mkr"],
                         "nya": [a["fond"] for a in agare if a["status"] == "ny"], "salt": [a["fond"] for a in agare if a["status"] == "salt"]})
    MAPP.mkdir(parents=True, exist_ok=True)
    (MAPP / "fondsignaler.json").write_text(json.dumps({"kvartal": kv_nu, "jamfort_med": kv_fore, "bolag": sorted(signaler, key=lambda s: -s["netto_kopare"])}, ensure_ascii=False, indent=1), encoding="utf-8")
    register = sorted(([f["isin"], f["namn"], (vanlig_avgift(f["avgift_klasser"]) or {}).get("fast")] for f in list(nu.values()) + [f for f in foljda if f.get("kalla_typ", "FI") != "FI"]), key=lambda x: x[1])
    (MAPP / "fondregister.json").write_text(json.dumps({"kvartal": kv_nu, "fonder": register}, ensure_ascii=False), encoding="utf-8")
    senast = MAPP / "senaste-kvartal.txt"
    ny = not senast.exists() or senast.read_text().strip() != kv_nu
    senast.write_text(kv_nu)
    print(f"{'NYTT KVARTAL ' if ny else ''}{kv_nu} (jämfört med {kv_fore}): {len(foljda)} fonder följs, fondägare för {len(bolag)} bevakade bolag.")
    for f in foljda:
        if f.get("kalla_typ") == "saknas":
            print(f"Saknar innehav för {f['namn']}: ange --kalla, --ersattning eller skriv innehav-manuellt.json.")
    if saknas:
        print("Finns inte i FI:s data (troligen registrerade utomlands):", ", ".join(saknas))


if __name__ == "__main__":
    main(sys.argv[1:])
