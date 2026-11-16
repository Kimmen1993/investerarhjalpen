#!/usr/bin/env python3
"""Signalradar – gratis, ingen AI. Letar tidiga signaler på hela den svenska börsen.

Källor: MFN (alla nordiska pressmeddelanden), FI:s insynsregister (alla bolag) och fondsignaler
ur FI:s kvartalsdata om fondinnehav (radar/fondsignaler-borsen.json, skrivs av fonder.py).
Signaler poängsätts enligt metod 15 och sparas i radar/signaler.json (rullande 90 dagar).
Topplistan skrivs till radar/radar.json; bolag som redan bevakas, kastats eller
står på uteslutningslistan hoppas över.

Kör: python3 -I verktyg/signalradar.py
"""
import csv
import io
import json
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rot import VERKTYG, DATA as ROT  # noqa: E402  (ROT = användarens datamapp)
RADAR = ROT / "radar"
UA = {"User-Agent": "Mozilla/5.0 (investerarhjalpen signalradar)"}

REGLER = [
    ("genombrott", 3, r"första (order|kontrakt|avtal|kund)|first (order|contract|customer|commercial)|genombrott|breakthrough|design.?win|kvalificering|qualification|pilot(order|projekt|avtal| project| order)|selected by|utvald av|väljs av|väljer .* som (leverantör|partner)|development order|utvecklingsorder|prototype order|prototyporder"),
    ("partnerskap", 3, r"strategiskt samarbete|strategisk partner|strategic (partnership|cooperation|collaboration|partner|alliance)|joins forces|samarbetsavtal|partnership with|partnerskap med|licensavtal|license agreement|distributionsavtal|distribution agreement"),
    ("ramavtal_order", 2, r"ramavtal|framework (agreement|contract)|\border\b|tecknar (avtal|kontrakt)|signs? (an? )?(agreement|contract|deal)|vinner (upphandling|avtal|kontrakt)|wins? (a |an )?(contract|tender|order)|tilldelas|awarded|avrop|call.?off|kontrakt värt|contract (worth|valued)|avtal värt"),
    ("ny_agare", 2, r"riktad (ny)?emission till|directed (share )?issue to|strategisk investerare|strategic investor|cornerstone"),
    ("ny_ledning", 1, r"utser .*(vd|verkställande)|ny (vd|verkställande direktör)|appoints .*(ceo|chief executive)|new ceo|ny styrelseordförande"),
    ("negativ", -3, r"vinstvarning|profit warning|företrädesemission|rights issue|rekonstruktion|reconstruction|likvidation|konkurs|bankruptcy|going concern|kontrollbalansräkning"),
]
AGGREGATORER = {"nyemissionerse", "nyemissioner", "inderes", "redeye", "analysguiden", "borsvarlden"}
RUTIN = r"kallelse|notice of|valberedning|nomination committee|delårsrapport|interim report|bokslutskommuniké|year-end report|årsredovisning|annual report|insynshandel|managers.? transactions|meldepliktig|johdon liiketoimet|antal aktier och röster|number of shares and votes"


def hamta(url, timeout=40):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
        return r.read()


def las_json(p, standard):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else standard


def mfn_signaler():
    data = hamta("https://mfn.se/all/s/nordic.rss?limit=1500")
    ut = []
    for it in ET.fromstring(data).iter("item"):
        scopes = [c.text for c in it if c.tag.endswith("scope")]
        if "SE" not in scopes:
            continue
        titel = (it.findtext("title") or "").strip()
        lank = (it.findtext("link") or "").strip()
        m = re.search(r"mfn\.se/(?:[a-z]+/)?a/([^/]+)/", lank)
        if not m or re.search(RUTIN, titel, re.I) or m.group(1) in AGGREGATORER:
            continue
        if re.search(r"\bin order to\b|\bi syfte\b", titel, re.I):
            titel_test = re.sub(r"in order to", "", titel, flags=re.I)
        else:
            titel_test = titel
        try:
            datum = parsedate_to_datetime(it.findtext("pubDate")).date().isoformat()
        except Exception:
            continue
        for typ, poang, monster in REGLER:
            if re.search(monster, titel_test, re.I):
                ut.append({"bolag": m.group(1), "datum": datum, "typ": typ, "poang": poang,
                           "titel": titel, "lank": lank, "kalla": "MFN"})
                break
    return ut


def insyn_signaler(dagar=14):
    fran = (datetime.now() - timedelta(days=dagar)).date().isoformat()
    q = urllib.parse.urlencode({"SearchFunctionType": "Insyn", "Publiceringsdatum.From": fran,
                                "Publiceringsdatum.To": datetime.now().date().isoformat(), "button": "export"})
    raw = hamta(f"https://marknadssok.fi.se/publiceringsklient/sv-SE/Search/Search?{q}")
    text = raw.decode("utf-16-le", "ignore").replace("\x00", "").lstrip("﻿")
    rader = list(csv.reader(io.StringIO(text), delimiter=";"))
    if not rader:
        return []
    idx = {k.strip(): i for i, k in enumerate(rader[0])}
    g = lambda r, k: r[idx[k]].strip() if k in idx and idx[k] < len(r) else ""
    per_bolag = {}
    for r in rader[1:]:
        if len(r) < 10 or g(r, "Status") not in ("", "Aktuell") or g(r, "Instrumenttyp") != "Aktie":
            continue
        kar = g(r, "Karaktär")
        try:
            varde = float(g(r, "Volym").replace(",", ".")) * float(g(r, "Pris").replace(",", "."))
        except ValueError:
            varde = 0
        b = per_bolag.setdefault(g(r, "Emittent"), {"kop_personer": set(), "kop_varde": 0.0, "salj_personer": set(), "salj_varde": 0.0, "datum": ""})
        if kar.startswith("Förvärv"):
            b["kop_personer"].add(g(r, "Person i ledande ställning"))
            b["kop_varde"] += varde
        elif kar.startswith("Avyttring"):
            b["salj_personer"].add(g(r, "Person i ledande ställning"))
            b["salj_varde"] += varde
        b["datum"] = max(b["datum"], g(r, "Publiceringsdatum")[:10])
    ut = []
    lank = "https://marknadssok.fi.se/publiceringsklient/sv-SE/Search/Search?SearchFunctionType=Insyn&Utgivare="
    for namn, b in per_bolag.items():
        if len(b["kop_personer"]) >= 2 or b["kop_varde"] >= 500_000:
            ut.append({"bolag": namn, "datum": b["datum"], "typ": "insiderkop", "poang": 3,
                       "titel": f"Insiderköp: {len(b['kop_personer'])} personer för ca {b['kop_varde']/1e6:.1f} MSEK (14 dagar)",
                       "lank": lank + urllib.parse.quote(namn), "kalla": "FI"})
        if len(b["salj_personer"]) >= 2 or b["salj_varde"] >= 1_000_000:
            ut.append({"bolag": namn, "datum": b["datum"], "typ": "insidersalj", "poang": -3,
                       "titel": f"Insiderförsäljning: {len(b['salj_personer'])} personer för ca {b['salj_varde']/1e6:.1f} MSEK (14 dagar)",
                       "lank": lank + urllib.parse.quote(namn), "kalla": "FI"})
    return ut


def fond_signaler():
    """Läser fondsignalerna som fonder.py räknat fram för hela börsen (gratis, ingen nedladdning här)."""
    return las_json(RADAR / "fondsignaler-borsen.json", {"signaler": []})["signaler"]


def normalisera(namn):
    n = namn.lower()
    n = re.sub(r"\b(ab|asa|oyj|a/s|publ|group|holding|\(publ\))\b", "", n)
    return re.sub(r"[^a-z0-9åäö]+", "-", n).strip("-")


def main():
    RADAR.mkdir(exist_ok=True)
    sigfil = RADAR / "signaler.json"
    alla = las_json(sigfil, {"signaler": []})["signaler"]
    sedda = {(s["bolag"], s["titel"], s["datum"]) for s in alla}
    fel = []
    nya = []
    for kalla in (mfn_signaler, insyn_signaler, fond_signaler):
        try:
            for s in kalla():
                s["nyckel"] = normalisera(s["bolag"])
                if (s["bolag"], s["titel"], s["datum"]) not in sedda:
                    nya.append(s)
        except Exception as e:
            fel.append(f"{kalla.__name__}: {e}")
    grans = (datetime.now() - timedelta(days=90)).date().isoformat()
    alla = [s for s in alla + nya if s["datum"] >= grans]
    sigfil.write_text(json.dumps({"signaler": alla}, ensure_ascii=False, indent=1), encoding="utf-8")

    # Uteslut bevakade, kastade och storbolag
    utesl = las_json(RADAR / "uteslutna.json", {"bolag": []})["bolag"]
    bevakade, bevakade_isin = [], set()
    for st in ROT.glob("bolag/*/status.json"):
        s = json.loads(st.read_text(encoding="utf-8"))
        bevakade += [normalisera(s.get("namn", "")), st.parent.name, (s.get("kallor_bevakning") or {}).get("mfn_slug", "")]
        if s.get("isin"):
            bevakade_isin.add(s["isin"])
    utesl_n = {normalisera(x) for x in utesl + bevakade if x}

    idag = datetime.now().date()
    per = {}
    unika = set()
    for s in alla:
        # Samma bolag, dag och typ räknas en gång (svensk och engelsk version av samma PM)
        if (s["nyckel"], s["datum"], s["typ"]) in unika:
            continue
        unika.add((s["nyckel"], s["datum"], s["typ"]))
        if s["nyckel"] in utesl_n or s["bolag"] in utesl_n or s.get("isin") in bevakade_isin:
            continue
        alder = (idag - datetime.fromisoformat(s["datum"]).date()).days
        vikt = 1.0 if alder <= 30 else 0.6 if alder <= 60 else 0.3
        p = per.setdefault(s["nyckel"], {"bolag": s["bolag"], "poang": 0.0, "signaler": [], "typer": set()})
        p["poang"] += s["poang"] * vikt
        p["signaler"].append(s)
        p["typer"].add(s["typ"])
    # Bonus för flera olika typer av positiva signaler (oberoende källor)
    for p in per.values():
        positiva = {t for t in p["typer"] if t not in ("negativ", "insidersalj", "fondflykt")}
        if len(positiva) >= 2:
            p["poang"] += 2
    # Bonus för bolag som finns i en hypotes eller trend (metod 21): omvärlden pekar åt samma håll.
    teman = {}
    for tf in sorted((ROT / "trender").glob("*.json")) if (ROT / "trender").exists() else []:
        if tf.name.startswith("_"):
            continue
        tr = las_json(tf, {})
        if tr.get("status") in ("avfardad", "historisk"):
            continue
        for b in tr.get("bolag", []) + (tr.get("hypotes") or {}).get("bolag", []):
            if b.get("namn"):
                teman.setdefault(normalisera(b["namn"]), []).append(tr.get("namn", tf.stem))
    for k, p in per.items():
        if k in teman:
            p["poang"] += 2
            p["typer"].add("tema")
            p["teman"] = sorted(set(teman[k]))
    triage = las_json(RADAR / "triage.json", {"bolag": {}})["bolag"]
    lista = sorted(per.values(), key=lambda p: -p["poang"])
    topp = [{"nyckel": k, "bolag": p["bolag"], "poang": round(p["poang"], 1), "typer": sorted(p["typer"]),
             "antal": len(p["signaler"]), "senaste": max(s["datum"] for s in p["signaler"]),
             "triage": triage.get(k), "teman": p.get("teman", []), "signaler": sorted(p["signaler"], key=lambda s: s["datum"], reverse=True)[:6]}
            for k, p in ((normalisera(p["bolag"]), p) for p in lista) if p["poang"] >= 3][:40]
    (RADAR / "radar.json").write_text(json.dumps({"uppdaterad": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                                  "bolag": topp, "fel": fel}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Nya signaler: {len(nya)}. Bolag på radarn (≥3 poäng): {len(topp)}. Fel: {fel or 'inga'}")
    for t in topp[:15]:
        print(f"  {t['poang']:5.1f}  {t['bolag'][:40]:40s} {','.join(t['typer'])}  {'[' + t['triage']['beslut'] + ']' if t['triage'] else ''}")


if __name__ == "__main__":
    sys.exit(main())
