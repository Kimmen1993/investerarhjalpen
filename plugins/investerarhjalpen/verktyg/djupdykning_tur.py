#!/usr/bin/env python3
"""Vilka bolag står på tur för söndagens djupdykning?

Läser inställningarna under "djupdykning" i installningar.json:
  per_sondag          högst så många bolag en vanlig söndag (standard 5)
  intervall_dagar     ett bolag står på tur när senaste djupdykningen är så här gammal (standard 27)
  extra_nasta_sondag  så många extra bolag nästa körning (nollställs efter körningen)
  onskade             bolag (mappnamn eller namn) som tas med nästa körning oavsett datum (töms efter körningen)

Kör: python3 -I djupdykning_tur.py [--extra N] [--nollstall]
--extra N     lägg till N bolag just den här gången (utöver inställningen)
--nollstall   töm extra_nasta_sondag och onskade (görs när söndagens körning är klar)
"""
import argparse, json, sys
from datetime import date
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from rot import DATA  # noqa: E402

STANDARD = {"per_sondag": 5, "intervall_dagar": 27, "extra_nasta_sondag": 0, "onskade": []}


def installningar():
    f = DATA / "installningar.json"
    d = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
    return f, d, {**STANDARD, **(d.get("djupdykning") or {})}


def main():
    a = argparse.ArgumentParser(); a.add_argument("--extra", type=int, default=0); a.add_argument("--nollstall", action="store_true"); arg = a.parse_args()
    f, d, dj = installningar()
    if arg.nollstall:
        dj["extra_nasta_sondag"] = 0; dj["onskade"] = []; d["djupdykning"] = dj
        f.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"); print("Nollställt: extra och önskade bolag."); return
    idag = date.today(); bolag = []
    for st in sorted(DATA.glob("bolag/*/status.json")):
        s = json.loads(st.read_text(encoding="utf-8"))
        if s.get("beslut") == "Kasta": continue
        sen = s.get("senaste_djupdykning")
        dagar = (idag - date.fromisoformat(sen)).days if sen else 9999
        bolag.append({"mapp": st.parent.name, "namn": s.get("namn", st.parent.name), "dagar": dagar})
    onsk = {str(x).lower() for x in dj["onskade"]}
    valda = [b for b in bolag if b["mapp"].lower() in onsk or b["namn"].lower() in onsk]
    tur = sorted([b for b in bolag if b["dagar"] >= dj["intervall_dagar"] and b not in valda], key=lambda b: -b["dagar"])
    valda += tur[:max(0, dj["per_sondag"] - len(valda))]
    extra = dj["extra_nasta_sondag"] + arg.extra  # extra bolag: de som gått längst utan genomgång, även om de inte är på tur än
    ovriga = sorted([b for b in bolag if b not in valda], key=lambda b: -b["dagar"])
    valda += ovriga[:max(0, extra)]
    print(f"Inställning: högst {dj['per_sondag']} per söndag, var {dj['intervall_dagar']}:e dag. Extra den här gången: {dj['extra_nasta_sondag'] + arg.extra}. Önskade: {', '.join(dj['onskade']) or 'inga'}.")
    print("På tur nu:", ", ".join(f"{b['namn']} ({b['dagar'] if b['dagar'] < 9999 else 'aldrig'} dagar)" for b in valda) or "inga")
    rest = [b for b in tur if b not in valda]
    if rest: print("Väntar till nästa söndag:", ", ".join(b["namn"] for b in rest))
    print(json.dumps([b["mapp"] for b in valda]))


if __name__ == "__main__":
    main()
