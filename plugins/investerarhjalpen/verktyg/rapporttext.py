#!/usr/bin/env python3
"""Hämtar ett bolags senaste rapport-PDF (ur rapporter.json) och skriver ut texten.

Kör:  python3 -I verktyg/rapporttext.py <bolag-mapp> [index=0] [maxtecken=60000]
Sparar PDF och text i /tmp-mappen som anges av miljövariabeln RAPPORT_TMP (annars ./.rapport-tmp).
"""
import json, os, subprocess, sys, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rot import VERKTYG, DATA as ROT  # noqa: E402  (ROT = användarens datamapp)
slug = sys.argv[1]; idx = int(sys.argv[2]) if len(sys.argv) > 2 else 0; mx = int(sys.argv[3]) if len(sys.argv) > 3 else 60000
r = json.loads((ROT / "bolag" / slug / "rapporter.json").read_text())["rapporter"]
r = [x for x in r if x.get("pdf")]
x = r[idx]
tmp = Path(os.environ.get("RAPPORT_TMP", ROT / ".rapport-tmp")); tmp.mkdir(parents=True, exist_ok=True)
pdf = tmp / f"{slug}-{idx}.pdf"
if not pdf.exists():
    pdf.write_bytes(urllib.request.urlopen(urllib.request.Request(x["pdf"], headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read())
txt = subprocess.run(["swift", str(VERKTYG / "verktyg" / "pdftext.swift"), str(pdf)], capture_output=True, text=True).stdout
print(f"### {x['datum']} {x['typ']}: {x['titel']}\n### {x['pdf']}\n")
print(txt[:mx])
