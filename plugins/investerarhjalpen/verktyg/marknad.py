#!/usr/bin/env python3
"""Marknadsmodell uppifrån: marknadens storlek × bolagets andel, plus tratten för nya kunder.
Vägs ihop med pipelinen (nerifrån) till fyra banor och ett värde år X.

Resultatet sparas i bolag/<namn>/marknadsmodell.json under "resultat".
Kör: python3 -I verktyg/marknad.py   (anropas också av bygg_sida.py)
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rot import VERKTYG, DATA as ROT  # noqa: E402  (ROT = användarens datamapp)
BANOR = ["svag", "forvantad", "stark", "drom"]
NIVA = {"svag": "lag", "forvantad": "mitt", "stark": "hog", "drom": "hog"}


def interp(v0, v1, a, a0, a1):
    return v0 + (v1 - v0) * (a - a0) / (a1 - a0)


def rakna(m, pipeline=None):
    ar = m["ar"]
    a1 = ar[-1]
    nu = m["nuvarande"]
    a_nu = nu["ar"]
    mk = m["marknad"]
    alla = [a_nu] + ar
    marknad = {}
    for niva in ("lag", "mitt", "hog"):
        andel = mk["andel_med_edge"][niva]
        marknad[niva] = {str(a): mk["satelliter_per_ar"][str(a)] * interp(andel[str(a_nu)], andel[str(a1)], a, a_nu, a1)
                         * mk["varde_per_satellit_msek"][niva] for a in alla}
    nu_andel = nu["forsaljning_msek"] / marknad["mitt"][str(a_nu)]
    per_bana = m.get("marknad_per_bana", NIVA)

    # Uppifrån: marknad × andel. Andelen går linjärt från dagens andel till scenariots andel år a1
    uppifran = {}
    slutandel = {}
    for b in BANOR:
        niva = per_bana[b]
        slutandel[b] = sum(r["andel_av_marknad"] * m["andel_scenarier"][b][r["namn"]] for r in m["regioner"])
        uppifran[b] = {str(a): marknad[niva][str(a)] * interp(nu_andel, slutandel[b], a, a_nu, a1) for a in ar}

    # Tratten: nya kundrelationer från 2027 → konverterade efter fördröjning → intäkt i N år
    t = m["tratt"]
    tratt = {}
    for b in BANOR:
        tratt[b] = {str(a): 0.0 for a in ar}
        for i, kohort in enumerate(ar):
            nya = t["nya_kundrelationer_2026"] * (1 + t["tillvaxt_nya_per_ar"][b]) ** (i + 1)
            konv = nya * t["konvertering"][b]
            start = kohort + t["fordrojning_ar"]
            for a in ar:
                if start <= a < start + t["livslangd_ar"]:
                    tratt[b][str(a)] += konv * t["intakt_per_konverterad_msek_per_ar"][b]

    # Nerifrån: pipelinen (utan dess egen post för okänd framtid; den ersätts av tratten)
    nerifran = {}
    if pipeline and "resultat" in pipeline:
        okand = pipeline["resultat"].get("okand_per_ar_forvantad", {})
        okand_def = pipeline.get("okand_framtid", {}).get("okning_msek_per_ar", {})
        for b in BANOR:
            pb = pipeline["resultat"]["banor"].get(b, {})
            nerifran[b] = {}
            for a in ar:
                steg = max(0, a - pipeline.get("okand_framtid", {}).get("fran_ar", 9999) + 1)
                nerifran[b][str(a)] = pb.get(str(a), 0) - okand_def.get(b, 0) * steg
    pipe_plus_tratt = {b: {str(a): nerifran.get(b, {}).get(str(a), 0) + tratt[b][str(a)] for a in ar} for b in BANOR}

    # Alla linser
    linser = {"uppifran": uppifran, "pipeline_tratt": pipe_plus_tratt}
    if nerifran:
        linser["pipeline"] = nerifran
    for met in m.get("metoder", []):
        if met["id"] == "mal" and "tillvaxt" in met:
            linser["mal"] = {b: {str(a): nu["forsaljning_msek"] * (1 + met["tillvaxt"][b]) ** (a - a_nu) for a in ar} for b in BANOR}
        if met["id"] in ("analoga", "analytiker") and "banor" in met:
            linser[met["id"]] = met["banor"]

    # Samlad bedömning: viktat medel av de linser som har vikt > 0 och data
    vikter = {met["id"]: met["vikt"] for met in m.get("metoder", []) if met.get("vikt", 0) > 0 and met["id"] in linser}
    if not vikter:
        vikter = {"uppifran": 0.5, "pipeline_tratt": 0.5}
    vsum = sum(vikter.values())
    samman = {b: {str(a): sum(linser[i][b][str(a)] * w for i, w in vikter.items()) / vsum for a in ar} for b in BANOR}
    spridning = {b: {str(a): [min(linser[i][b][str(a)] for i in vikter), max(linser[i][b][str(a)] for i in vikter)] for a in ar} for b in BANOR}

    # Värde år X = försäljning år Y × framåtmultipel + nettokassa, delat med antal aktier
    vy = m["vardering_forsaljning_ar"]
    vardering = {}
    for b in BANOR:
        oms = samman[b][vy]
        borsvarde = oms * m["framatmultipel"][b] + m["nettokassa_msek"][b]
        vardering[b] = {"forsaljning": round(oms, 0), "borsvarde_msek": round(borsvarde, 0),
                        "kr_per_aktie": round(borsvarde / m["aktier_milj"][b], 1)}
    vagt = sum(vardering[b]["kr_per_aktie"] * m["sannolikhet"][b] for b in BANOR)

    r1 = lambda d: {k: round(v, 0) for k, v in d.items()}
    return {
        "marknad_msek": {n: r1(v) for n, v in marknad.items()},
        "nuvarande_andel": round(nu_andel, 3),
        "slutandel": {b: round(v, 3) for b, v in slutandel.items()},
        "uppifran": {b: r1(v) for b, v in uppifran.items()},
        "tratt": {b: r1(v) for b, v in tratt.items()},
        "nerifran_pipeline": {b: r1(v) for b, v in nerifran.items()},
        "pipeline_plus_tratt": {b: r1(v) for b, v in pipe_plus_tratt.items()},
        "sammanvagd": {b: r1(v) for b, v in samman.items()},
        "linser": {i: {b: r1(v) for b, v in l.items()} for i, l in linser.items()},
        "vikter_anvanda": {i: round(w / vsum, 3) for i, w in vikter.items()},
        "spridning": {b: {a: [round(x[0]), round(x[1])] for a, x in s.items()} for b, s in spridning.items()},
        "vardering": vardering,
        "vagt_kr_per_aktie": round(vagt, 1),
    }


def main():
    for fil in sorted(ROT.glob("bolag/*/marknadsmodell.json")):
        m = json.loads(fil.read_text(encoding="utf-8"))
        pf = fil.parent / "mojligheter.json"
        pipe = json.loads(pf.read_text(encoding="utf-8")) if pf.exists() else None
        m["resultat"] = rakna(m, pipe)
        fil.write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")
        r = m["resultat"]
        print(fil.parent.name)
        for nyckel in ("marknad_msek", "uppifran", "tratt", "pipeline_plus_tratt", "sammanvagd"):
            print(" ", nyckel)
            for b, vals in r[nyckel].items():
                print(f"    {b:10s} " + "  ".join(f"{a}:{v:6.0f}" for a, v in vals.items()))
        print("  värdering", r["vardering"], "vägt", r["vagt_kr_per_aktie"])


if __name__ == "__main__":
    main()
