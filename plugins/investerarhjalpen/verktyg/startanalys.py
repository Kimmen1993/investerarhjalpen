#!/usr/bin/env python3
"""Skriver en startanalys för ett bolag ur en JSON-spec (från Claude).

Kör: python3 -I verktyg/startanalys.py <spec.json>
Spec: {slug, status:{...fält som slås ihop med status.json}, tes_md, kallor:[[datum, url, vad]],
       handelser:[{datum, rubrik, enkelt, paverkan, viktig, lank, lardom?, lektion?}],
       nyckeltal:{enhet, kalla, kvartal:[{period, omsattning, rorelseresultat, orderingang, kassa, kf_lopande, kf_invest, aktier_milj}]}}
"""
import json, sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rot import VERKTYG, DATA as ROT  # noqa: E402  (ROT = användarens datamapp)
spec = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
m = ROT / "bolag" / spec["slug"]; m.mkdir(parents=True, exist_ok=True)
st = json.loads((m / "status.json").read_text(encoding="utf-8")) if (m / "status.json").exists() else {}
st.update(spec["status"]); st.setdefault("senast_uppdaterad", date.today().isoformat())
(m / "status.json").write_text(json.dumps(st, ensure_ascii=False, indent=2), encoding="utf-8")
if spec.get("tes_md"):
    (m / "tes.md").write_text(spec["tes_md"].strip() + "\n", encoding="utf-8")
if spec.get("kallor"):
    rader = ["# Källor – " + st.get("namn", spec["slug"]), "", "| # | Datum | Källa | Vad den visar |", "|---|---|---|---|"]
    rader += [f"| K{i+1} | {d} | {u} | {v} |" for i, (d, u, v) in enumerate(spec["kallor"])]
    (m / "kallor.md").write_text("\n".join(rader) + "\n", encoding="utf-8")
if spec.get("handelser"):
    (m / "handelser.json").write_text(json.dumps({"handelser": spec["handelser"]}, ensure_ascii=False, indent=1), encoding="utf-8")
if spec.get("nyckeltal"):
    nt = spec["nyckeltal"]; nt.setdefault("uppdaterad", date.today().isoformat())
    (m / "nyckeltal.json").write_text(json.dumps(nt, ensure_ascii=False, indent=1), encoding="utf-8")
logg = m / "logg.md"
post = f"## {date.today().isoformat()} – Startanalys\n{spec.get('logg', 'Startanalys gjord: grunddata, tes, motbevis och händelser.')}\n"
logg.write_text((f"# Logg – {st.get('namn', spec['slug'])}\n\n" + post + ("\n" + logg.read_text(encoding='utf-8').split('\n', 2)[-1] if logg.exists() else "")), encoding="utf-8")
print("skrev", spec["slug"], "->", ", ".join(p.name for p in sorted(m.iterdir())))
