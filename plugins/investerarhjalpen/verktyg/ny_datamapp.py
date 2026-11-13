#!/usr/bin/env python3
"""Skapar en ny datamapp för en användare ur mallen i tillägget.

Kör: python3 -I ny_datamapp.py <mapp> --namn "Anna" [--egna-ord "text"]
Skriver aldrig över filer som redan finns.
"""
import argparse, shutil
from datetime import date
from pathlib import Path

VERKTYG = Path(__file__).resolve().parent.parent
a = argparse.ArgumentParser(); a.add_argument("mapp"); a.add_argument("--namn", required=True); a.add_argument("--egna-ord", default="(Inte ifyllt än. Skriv gärna med egna ord hur du vill investera.)")
arg = a.parse_args()
ut = Path(arg.mapp).expanduser().resolve(); ut.mkdir(parents=True, exist_ok=True)
for d in ["bolag", "radar", "teman", "site", "privat"]:
    (ut / d).mkdir(exist_ok=True)
mall = VERKTYG / "mall"
skapade = []
for f in mall.rglob("*"):
    if f.is_dir(): continue
    mal = ut / f.relative_to(mall)
    if mal.exists(): continue
    mal.parent.mkdir(parents=True, exist_ok=True)
    try:
        t = f.read_text(encoding="utf-8")
        t = t.replace("{NAMN}", arg.namn).replace("{DATUM}", date.today().isoformat()).replace("{EGNA_ORD}", arg.egna_ord)
        mal.write_text(t, encoding="utf-8")
    except UnicodeDecodeError:
        shutil.copy2(f, mal)
    skapade.append(str(mal.relative_to(ut)))
for f, innehall in [("radar/radar.json", "null"), ("radar/triage.json", '{"triage": []}'), ("radar/uteslutna.json", '{"uteslutna": []}')]:
    p = ut / f
    if not p.exists(): p.write_text(innehall + "\n", encoding="utf-8"); skapade.append(f)
print("Datamapp:", ut); print("Skapade:", ", ".join(skapade) or "inget nytt")
