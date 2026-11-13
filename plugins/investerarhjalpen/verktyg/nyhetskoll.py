#!/usr/bin/env python3
"""Nyhetskoll – gratis, ingen AI.

Hämtar nya pressmeddelanden (MFN) och insynsaffärer (FI) för varje bolag
som har bolag/<namn>/status.json med "kallor_bevakning". Sparar allt i
bolag/<namn>/nyheter.json och skriver en sammanfattning till
nyhetskoll-senaste.json i projektroten.

Kör:  python3 -I verktyg/nyhetskoll.py   (från projektroten, eller med sökväg)
"""
import csv
import io
import json
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rot import VERKTYG, DATA as ROT  # noqa: E402  (ROT = användarens datamapp)
UA = {"User-Agent": "Mozilla/5.0 (investerarhjalpen nyhetskoll)"}
RAPPORTORD = re.compile(r"delårsrapport|bokslutskommuniké|årsredovisning|kvartalsrapport|interim report|year-end report|annual report|q[1-4] (?:20\d\d )?report|report q[1-4]|quarterly report|financial statement for|reports .{0,60}for q[1-4]|osavuosikatsaus|puolivuosikatsaus|tilinpäätöstiedote|half-year(?:ly)? report|full[- ]year report", re.I)
VIKTIGA_ORD = re.compile(r"order|ramavtal|avtal|emission|förvärv|vinstvarning|framework|contract|rights issue|directed", re.I)


def hamta(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def mfn(slug):
    data = hamta(f"https://mfn.se/all/a/{slug}.rss")
    root = ET.fromstring(data)
    ut = []
    for it in root.iter("item"):
        titel = (it.findtext("title") or "").strip()
        lank = (it.findtext("link") or "").strip()
        try:
            datum = parsedate_to_datetime(it.findtext("pubDate")).date().isoformat()
        except Exception:
            datum = ""
        typ = "rapport" if RAPPORTORD.search(titel) else ("viktig" if VIKTIGA_ORD.search(titel) else "pm")
        ut.append({"id": lank, "datum": datum, "titel": titel, "lank": lank, "kalla": "MFN", "typ": typ})
    return ut


def insyn(utgivare):
    q = urllib.parse.urlencode({"SearchFunctionType": "Insyn", "Utgivare": utgivare, "button": "export"})
    raw = hamta(f"https://marknadssok.fi.se/publiceringsklient/sv-SE/Search/Search?{q}")
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        text = raw.decode("utf-16")
    elif b"\x00" in raw[:200]:
        text = raw.decode("utf-16-le", "ignore")
    else:
        text = raw.decode("utf-8", "ignore")
    text = text.replace("\x00", "").lstrip("﻿")
    rader = list(csv.reader(io.StringIO(text), delimiter=";"))
    if not rader:
        return []
    idx = {k.strip(): i for i, k in enumerate(rader[0])}
    ut = []
    for r in rader[1:]:
        if len(r) < len(idx) - 1:
            continue
        g = lambda k: r[idx[k]].strip() if k in idx and idx[k] < len(r) else ""
        if g("Status") and g("Status") != "Aktuell":
            continue
        karaktar = g("Karaktär")
        titel = f"{g('Person i ledande ställning')} ({g('Befattning')}): {karaktar} {g('Volym')} {g('Instrumenttyp')} à {g('Pris')} {g('Valuta')}"
        nyckel = "|".join([g("Publiceringsdatum"), g("Person i ledande ställning"), karaktar, g("Volym"), g("Pris"), g("Instrumenttyp")])
        typ = "insyn-salj" if karaktar.lower().startswith("avyttring") and g("Instrumenttyp") == "Aktie" else "insyn"
        ut.append({"id": nyckel, "datum": g("Transaktionsdatum")[:10], "titel": titel,
                   "lank": "https://marknadssok.fi.se/publiceringsklient/sv-SE/Search/Search?" + urllib.parse.urlencode({"SearchFunctionType": "Insyn", "Utgivare": utgivare}),
                   "kalla": "FI Insynsregistret", "typ": typ})
    return ut


def kurs(symbol):
    """Senaste kurs och 3 månaders dagshistorik från Yahoo Finance (gratis, ca 15 min fördröjning)."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(symbol)}?range=3mo&interval=1d"
    d = json.loads(hamta(url))["chart"]["result"][0]
    m, q = d["meta"], d["indicators"]["quote"][0]
    hist = [{"datum": datetime.fromtimestamp(t).date().isoformat(), "stang": round(c, 3), "volym": v}
            for t, c, v in zip(d.get("timestamp", []), q.get("close", []), q.get("volume", [])) if c is not None]
    # regularMarketPrice kan vara gammal för små listor: ta senaste stängning om den är nyare
    pris, tid = m["regularMarketPrice"], m["regularMarketTime"]
    par = [(t, c) for t, c in zip(d.get("timestamp", []), q.get("close", [])) if c is not None]
    if par and par[-1][0] > tid:
        tid, pris = par[-1]
    m = {**m, "regularMarketPrice": pris, "regularMarketTime": tid}
    return {"symbol": symbol, "kurs": round(m["regularMarketPrice"], 4), "valuta": m.get("currency"),
            "tid": datetime.fromtimestamp(m["regularMarketTime"]).strftime("%Y-%m-%d %H:%M"),
            "kalla": "Yahoo Finance (ca 15 min fördröjning)", "historik": hist}


def uppdatera_kurs(mapp, symbol, fel):
    try:
        k = kurs(symbol)
    except Exception as e:
        fel.append(f"Kurs: {e}")
        return None
    (mapp / "kurs.json").write_text(json.dumps(k, ensure_ascii=False, indent=1), encoding="utf-8")
    vfil = mapp / "vardering.json"
    if vfil.exists():
        v = json.loads(vfil.read_text(encoding="utf-8"))
        v["kurs"], v["kurs_datum"], v["kurs_kalla"] = k["kurs"], k["tid"], k["kalla"]
        vfil.write_text(json.dumps(v, ensure_ascii=False, indent=1), encoding="utf-8")
    return k


def main():
    sammanfattning = {"kord": datetime.now(timezone.utc).isoformat(timespec="seconds"), "bolag": []}
    for status_fil in sorted(ROT.glob("bolag/*/status.json")):
        status = json.loads(status_fil.read_text(encoding="utf-8"))
        kb = status.get("kallor_bevakning") or {}
        if status.get("beslut") == "Kasta":
            continue
        mapp = status_fil.parent
        nyfil = mapp / "nyheter.json"
        gamla = json.loads(nyfil.read_text(encoding="utf-8")) if nyfil.exists() else {"poster": []}
        sedda = {p["id"] for p in gamla["poster"]}
        kanda_kallor = {p["kalla"] for p in gamla["poster"]}
        poster, fel = [], []
        if kb.get("mfn_slug"):
            try:
                poster += mfn(kb["mfn_slug"])
            except Exception as e:
                fel.append(f"MFN: {e}")
        if kb.get("fi_utgivare"):
            try:
                poster += insyn(kb["fi_utgivare"])
            except Exception as e:
                fel.append(f"FI: {e}")
        k = uppdatera_kurs(mapp, kb["yahoo"], fel) if kb.get("yahoo") else None
        nya = [p for p in poster if p["id"] not in sedda]
        idag = datetime.now().date().isoformat()
        for p in nya:
            p["hittad"] = idag
            # Första körningen för en källa = historik, inte nyheter.
            p["ny"] = p["kalla"] in kanda_kallor
        alla = sorted(gamla["poster"] + nya, key=lambda p: p["datum"], reverse=True)
        nyfil.write_text(json.dumps({"poster": alla}, ensure_ascii=False, indent=1), encoding="utf-8")
        riktigt_nya = [p for p in nya if p["ny"]]
        sammanfattning["bolag"].append({
            "mapp": mapp.name,
            "namn": status.get("namn"),
            "nya": len(riktigt_nya),
            "rapport": any(p["typ"] == "rapport" for p in riktigt_nya),
            "insyn_salj": any(p["typ"] == "insyn-salj" for p in riktigt_nya),
            "behover_analys": any(p["typ"] in ("rapport", "viktig", "insyn-salj") for p in riktigt_nya),
            "rubriker": [f"{p['datum']} {p['titel']}" for p in riktigt_nya][:15],
            "kurs": {"kurs": k["kurs"], "tid": k["tid"],
                     "forandring_1d_pct": round((k["historik"][-1]["stang"] / k["historik"][-2]["stang"] - 1) * 100, 1) if len(k["historik"]) > 1 else None}
                    if k else None,
            "fel": fel,
        })
    try:  # direktlänkar till rapporternas PDF:er (gratis)
        import importlib.util
        spec = importlib.util.spec_from_file_location("rapportlankar", VERKTYG / "verktyg" / "rapportlankar.py")
        rl = importlib.util.module_from_spec(spec); spec.loader.exec_module(rl); rl.main()
    except Exception as e:
        print(f"Rapportlänkar: {e}")
    (ROT / "nyhetskoll-senaste.json").write_text(json.dumps(sammanfattning, ensure_ascii=False, indent=1), encoding="utf-8")
    for b in sammanfattning["bolag"]:
        flagga = " RAPPORT" if b["rapport"] else ""
        flagga += " INSIDER-SÄLJ" if b["insyn_salj"] else ""
        kk = f" | kurs {b['kurs']['kurs']} ({b['kurs']['tid']})" if b.get("kurs") else ""
        print(f"{b['namn']}{kk}: {b['nya']} nya{flagga}{' (behöver analys)' if b['behover_analys'] else ''}{' FEL: ' + '; '.join(b['fel']) if b['fel'] else ''}")
        for r in b["rubriker"]:
            print("   -", r)


if __name__ == "__main__":
    sys.exit(main())
