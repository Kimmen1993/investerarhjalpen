#!/usr/bin/env python3
"""Räknar fram prognosen och signalindexet ur bolag/<namn>/mojligheter.json.

Resultatet sparas i samma fil under "resultat". Webbsidan och värderingen läser det därifrån.
Kör:  python3 -I verktyg/pipeline.py            (alla bolag)
      python3 -I verktyg/pipeline.py unibap     (ett bolag)
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rot import VERKTYG, DATA as ROT  # noqa: E402  (ROT = användarens datamapp)
NIVAVIKT = {"A": 3, "B": 2, "C": 1, "?": 0.5}


def per_ar(belopp, ar, alla_ar):
    """Fördelar ett belopp jämnt över åren i [start, slut] och returnerar beloppet per prognosår."""
    start, slut = ar
    n = slut - start + 1
    return {a: (belopp / n if start <= a <= slut else 0.0) for a in alla_ar}


def kvartal(datum):
    m = re.match(r"(\d{4})(?:-(Q\d|\d{2}))?", str(datum))
    if not m:
        return None
    ar, rest = m.group(1), m.group(2)
    if not rest:
        return f"{ar}"
    if rest.startswith("Q"):
        return f"{ar} {rest}"
    return f"{ar} Q{(int(rest) - 1) // 3 + 1}"


def rakna(data):
    alla_ar = data["prognos_ar"]
    lop = data["lopande_affar"]
    banor = {"svag": {}, "forvantad": {}, "stark": {}, "drom": {}}
    lop["tillvaxt"].setdefault("drom", lop["tillvaxt"]["stark"])
    for i, a in enumerate(alla_ar, start=1):
        for bana in banor:
            banor[bana][a] = lop["msek_per_ar"] * (1 + lop["tillvaxt"][bana]) ** i

    signerat = {a: 0.0 for a in alla_ar}
    for s in data.get("signerat", []):
        for a, v in per_ar(s["intakt_msek"], s["ar"], alla_ar).items():
            signerat[a] += v
    for bana in banor:
        for a in alla_ar:
            banor[bana][a] += signerat[a]

    per_mojlighet = []
    for m in data.get("mojligheter", []):
        lag, hog = m["intakt_msek"]
        mitt = (lag + hog) / 2
        p = m["sannolikhet"]
        forv = per_ar(p * mitt, m["ar"], alla_ar)
        stark = per_ar(min(1.0, p * 1.6) * (mitt + hog) / 2, m["ar"], alla_ar)
        drom = per_ar(hog, m["ar"], alla_ar)
        for a in alla_ar:
            banor["forvantad"][a] += forv[a]
            banor["stark"][a] += stark[a]
            banor["drom"][a] += drom[a]
        per_mojlighet.append({"namn": m["namn"], "vantevarde_msek": round(p * mitt, 1),
                              "per_ar": {str(a): round(forv[a], 1) for a in alla_ar}})

    # Affärer som inte syns än: växer med ett fast belopp per år från ett visst år
    okand = data.get("okand_framtid")
    okand_per_ar = {a: 0.0 for a in alla_ar}
    if okand:
        for a in alla_ar:
            steg = a - okand["fran_ar"] + 1
            if steg > 0:
                for bana in banor:
                    v = okand["okning_msek_per_ar"].get(bana, 0) * steg
                    banor[bana][a] += v
                    if bana == "forvantad":
                        okand_per_ar[a] = v

    # Signalindex per kvartal (viktat efter bevisnivå)
    index = {}
    for m in data.get("mojligheter", []):
        for s in m.get("signaler", []):
            k = kvartal(s["datum"])
            if k and " " in k:
                index[k] = index.get(k, 0) + NIVAVIKT.get(s.get("niva", "?"), 0.5)
    index = dict(sorted(index.items()))

    return {
        "banor": {b: {str(a): round(v, 1) for a, v in vals.items()} for b, vals in banor.items()},
        "signerat_per_ar": {str(a): round(v, 1) for a, v in signerat.items()},
        "okand_per_ar_forvantad": {str(a): round(v, 1) for a, v in okand_per_ar.items()},
        "per_mojlighet": sorted(per_mojlighet, key=lambda x: -x["vantevarde_msek"]),
        "pipeline_vantevarde_msek": round(sum(x["vantevarde_msek"] for x in per_mojlighet), 1),
        "signalindex": index,
    }


def main():
    mal = sys.argv[1:] or None
    for fil in sorted(ROT.glob("bolag/*/mojligheter.json")):
        if mal and fil.parent.name not in mal:
            continue
        data = json.loads(fil.read_text(encoding="utf-8"))
        data["resultat"] = rakna(data)
        fil.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        r = data["resultat"]
        print(f"{fil.parent.name}: pipeline (sannolikhetsvägd) {r['pipeline_vantevarde_msek']} MSEK")
        for bana, vals in r["banor"].items():
            print(f"  {bana:10s} " + "  ".join(f"{a}:{v:6.0f}" for a, v in vals.items()))
        print("  signalindex:", r["signalindex"])


if __name__ == "__main__":
    main()
