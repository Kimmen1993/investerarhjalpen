#!/usr/bin/env python3
"""Rapportlänkar – gratis, ingen AI.

Letar upp direktlänken till PDF:en för varje rapport (delårsrapport,
bokslutskommuniké, årsredovisning) som nyhetskollen har hittat på MFN.
Sparar i bolag/<namn>/rapporter.json så att webbsidan kan visa dem.
Hämtar bara rapporter som inte redan finns i filen.

Kör:  python3 -I verktyg/rapportlankar.py
"""
import json
import re
import urllib.parse
import urllib.request
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rot import VERKTYG, DATA as ROT  # noqa: E402  (ROT = användarens datamapp)
UA = {"User-Agent": "Mozilla/5.0 (investerarhjalpen rapportlankar)"}
SKIPPA = re.compile(r"inbjudan|invitation|webcast|rättelse|correction|presentation av", re.I)
PDF = re.compile(r'https://[^"\'<> ]+?\.pdf', re.I)
RAPPORT = re.compile(r"delårsrapport|bokslutskommuniké|årsredovisning|kvartalsrapport|interim report|year-end report|annual report|q[1-4] (?:20\d\d )?report|report q[1-4]|quarterly report|financial statement for|reports .{0,60}for q[1-4]|osavuosikatsaus|puolivuosikatsaus|tilinpäätöstiedote|half-year(?:ly)? report|full[- ]year report", re.I)


def typ_av(titel):
    t = titel.lower()
    if "årsredovisning" in t or "annual report" in t:
        return "Årsredovisning"
    if "bokslut" in t or "year-end" in t or "full year" in t or "full-year" in t or "tilinpäätös" in t:
        return "Bokslutskommuniké"
    return "Delårsrapport"


def basta_pdf(lankar):
    def poang(u):
        n = urllib.parse.unquote(u.rsplit("/", 1)[-1]).lower()
        p = 0
        if re.search(r"delårs|delars|bokslut|årsredovisning|arsredovisning", n):
            p += 3
        if re.search(r"interim|annual|year-end|ladda ned|download", n):
            p -= 2
        return p
    return max(lankar, key=poang) if lankar else None


def main():
    for nyfil in sorted(ROT.glob("bolag/*/nyheter.json")):
        mapp = nyfil.parent
        rfil = mapp / "rapporter.json"
        rapporter = json.loads(rfil.read_text(encoding="utf-8")) if rfil.exists() else {"rapporter": []}
        kanda = {r["pm"] for r in rapporter["rapporter"]}
        poster = json.loads(nyfil.read_text(encoding="utf-8"))["poster"]
        nya = 0
        for p in poster:
            if not (p.get("typ") == "rapport" or RAPPORT.search(p["titel"])) or SKIPPA.search(p["titel"]) or p["lank"] in kanda:
                continue
            try:
                req = urllib.request.Request(p["lank"], headers=UA)
                html = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "replace")
                pdf = basta_pdf(sorted(set(PDF.findall(html))))
            except Exception as e:
                print(f"{mapp.name}: kunde inte läsa {p['lank']}: {e}")
                continue
            rapporter["rapporter"].append({"datum": p["datum"], "typ": typ_av(p["titel"]), "titel": p["titel"], "pm": p["lank"], "pdf": pdf})
            nya += 1
        rapporter["rapporter"].sort(key=lambda r: r["datum"], reverse=True)
        rfil.write_text(json.dumps(rapporter, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{mapp.name}: {len(rapporter['rapporter'])} rapporter ({nya} nya)")


if __name__ == "__main__":
    main()
