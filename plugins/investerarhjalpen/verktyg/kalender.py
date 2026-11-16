#!/usr/bin/env python3
"""Kalendern: kommande händelser för de bevakade bolagen (status.json → "kalender") och kalender.json (makro).

Gratis, ingen AI. Kör från datamappen:
  python3 -I kalender.py            de närmaste 14 dagarna
  python3 -I kalender.py --vecka    de närmaste 7 dagarna (till söndagens veckoöversikt)
  python3 -I kalender.py --imorgon  i dag och i morgon (morgonkollen: förhandsvisning inför rapporter)
  python3 -I kalender.py --ungefar  händelser som bara har en månad, de närmaste 3 månaderna (datum att ta reda på)
"""
import json
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rot import DATA as ROT  # noqa: E402


def handelser():
    ut = []
    for p in sorted(ROT.glob("bolag/*/status.json")):
        s = json.loads(p.read_text(encoding="utf-8"))
        if s.get("beslut") == "Kasta":
            continue
        for k in s.get("kalender") or []:
            ut.append({**k, "bolag": s.get("namn", p.parent.name), "slug": p.parent.name,
                       "har_forhandsvisning": bool((s.get("forhandsvisning") or {}).get("datum") == k.get("datum"))})
    mk = ROT / "kalender.json"
    if mk.exists():
        for k in json.loads(mk.read_text(encoding="utf-8")).get("handelser", []):
            ut.append({**k, "bolag": None, "slug": None})
    return sorted((k for k in ut if k.get("datum")), key=lambda k: k["datum"])


def main(argv):
    idag = date.today()
    alla = handelser()
    exakt = [k for k in alla if not k.get("ungefar") and len(k["datum"]) == 10]
    if "--ungefar" in argv:
        grans = (idag + timedelta(days=92)).isoformat()[:7]
        rader = [k for k in alla if (k.get("ungefar") or len(k["datum"]) == 7) and idag.isoformat()[:7] <= k["datum"][:7] <= grans]
    else:
        dagar = 1 if "--imorgon" in argv else 7 if "--vecka" in argv else 14
        slut = (idag + timedelta(days=dagar)).isoformat()
        rader = [k for k in exakt if idag.isoformat() <= k["datum"] <= slut]
    if not rader:
        print("Inga händelser.")
        return
    for k in rader:
        exakt_datum = not k.get("ungefar") and len(k["datum"]) == 10
        extra = "" if not (exakt_datum and k.get("typ") == "rapport") else (" [förhandsvisning finns]" if k.get("har_forhandsvisning") else " [förhandsvisning saknas]")
        print(f"{k['datum']}  {k.get('typ', 'ovrigt'):12s} {(k['bolag'] or 'Makro'):28s} {k['text']}{extra}  ({k['slug'] or ''})")


if __name__ == "__main__":
    main(sys.argv[1:])
