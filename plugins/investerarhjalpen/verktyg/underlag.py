#!/usr/bin/env python3
"""Snabbunderlag för en startanalys: PM-rubriker (6 mån, utan dubbletter), insynsaffärer, kurs och rapportlista.
Kör: python3 -I verktyg/underlag.py <bolag-mapp> [manader=6]"""
import json, sys
from datetime import date, timedelta
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from rot import VERKTYG, DATA as ROT  # noqa: E402  (ROT = användarens datamapp)
m = ROT / "bolag" / sys.argv[1]; man = int(sys.argv[2]) if len(sys.argv) > 2 else 6
fran = (date.today() - timedelta(days=30 * man)).isoformat()
ny = json.loads((m / "nyheter.json").read_text())["poster"]; sett = set()
print("== PM och insyn sedan", fran)
for p in ny:
    if p["datum"] < fran: continue
    k = (p["datum"], p["titel"][:40].lower())
    if k in sett: continue
    sett.add(k); print(p["datum"], p["typ"][:6], p["titel"][:120])
k = json.loads((m / "kurs.json").read_text()) if (m / "kurs.json").exists() else None
if k: h = k["historik"]; print("== kurs", k["kurs"], k.get("valuta"), "3 mån:", round((h[-1]["stang"] / h[0]["stang"] - 1) * 100), "%")
r = json.loads((m / "rapporter.json").read_text())["rapporter"] if (m / "rapporter.json").exists() else []
print("== rapporter:", [(x["datum"], x["typ"], bool(x.get("pdf"))) for x in r[:5]])
