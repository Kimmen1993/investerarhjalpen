#!/usr/bin/env python3
"""Bygger webbsidan site/index.html från alla filer i projektet.

Kör:  python3 -I verktyg/bygg_sida.py
Publicera sedan site/index.html med Artifact-verktyget (URL står i CLAUDE.md).
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rot import VERKTYG, DATA as ROT, verktygsversion  # noqa: E402  (ROT = användarens datamapp)
import pipeline  # noqa: E402  (räknar prognosen ur mojligheter.json)
import marknad  # noqa: E402  (marknadsmodell uppifrån + tratt, vägs ihop med pipelinen)
import andringar  # noqa: E402  (rutan "Nytt sedan sist")


def las(p):
    return p.read_text(encoding="utf-8") if p.exists() else ""


def titel_ur_md(text, reserv):
    m = re.search(r"^#\s+(.+)$", text, re.M)
    return m.group(1).strip() if m else reserv


def main():
    bolag = []
    for status_fil in sorted(ROT.glob("bolag/*/status.json")):
        mapp = status_fil.parent
        status = json.loads(las(status_fil))
        docs = {k: las(mapp / f"{k}.md") for k in ("tes", "kundregister", "loften", "logg", "kallor")}
        nyheter = json.loads(las(mapp / "nyheter.json") or '{"poster": []}')["poster"]
        handelser = json.loads(las(mapp / "handelser.json") or '{"handelser": []}')["handelser"]
        nyckeltal = json.loads(las(mapp / "nyckeltal.json") or "null")
        vardering = json.loads(las(mapp / "vardering.json") or "null")
        kurs = json.loads(las(mapp / "kurs.json") or "null")
        rapporter = json.loads(las(mapp / "rapporter.json") or '{"rapporter": []}')["rapporter"]
        panel = json.loads(las(mapp / "panel.json") or "null")
        fondagare = json.loads(las(mapp / "fondagare.json") or "null")
        mojl_fil = mapp / "mojligheter.json"
        mojligheter = None
        if mojl_fil.exists():
            mojligheter = json.loads(las(mojl_fil))
            mojligheter["resultat"] = pipeline.rakna(mojligheter)
            mojl_fil.write_text(json.dumps(mojligheter, ensure_ascii=False, indent=1), encoding="utf-8")
        mm_fil = mapp / "marknadsmodell.json"
        marknadsmodell = None
        if mm_fil.exists():
            marknadsmodell = json.loads(las(mm_fil))
            marknadsmodell["resultat"] = marknad.rakna(marknadsmodell, mojligheter)
            mm_fil.write_text(json.dumps(marknadsmodell, ensure_ascii=False, indent=1), encoding="utf-8")
        djup = [{"datum": p.stem, "md": las(p)} for p in sorted((mapp / "djupdykningar").glob("*.md"), reverse=True)]
        if djup:
            docs["djup"] = "\n\n---\n\n".join(d["md"] for d in djup)
        bolag.append({"slug": re.sub(r"[^a-z0-9-]", "-", mapp.name.lower()), "status": status,
                      "docs": {k: v for k, v in docs.items() if v}, "nyheter": nyheter,
                      "handelser": sorted(handelser, key=lambda h: h["datum"], reverse=True), "nyckeltal": nyckeltal,
                      "vardering": vardering, "kurs": kurs, "rapporter": rapporter, "mojligheter": mojligheter,
                      "marknadsmodell": marknadsmodell, "panel": panel, "fondagare": fondagare,
                      "djup_datum": [d["datum"] for d in djup]})
    ordning = {"Bevaka": 0, "Avvakta": 1, "Kasta": 2}
    bolag.sort(key=lambda b: (ordning.get(b["status"].get("beslut"), 3), -(b["status"].get("poang") or 0)))

    teman = [{"titel": titel_ur_md(las(p), p.stem), "md": las(p)} for p in sorted(ROT.glob("teman/*.md"), reverse=True)]
    metod = [{"titel": titel_ur_md(las(p), p.stem), "md": las(p), "id": p.stem.split("-")[0]} for p in sorted(VERKTYG.glob("metod/*.md"))]
    if (ROT / "min-strategi.md").exists():  # användarens egen strategi ligger i datamappen
        metod.append({"titel": titel_ur_md(las(ROT / "min-strategi.md"), "Min strategi"), "md": las(ROT / "min-strategi.md"), "id": "strategi"})

    ordlista = []
    for rad in las(VERKTYG / "metod" / "ordlista.md").splitlines():
        m = re.match(r"^\s*-\s+\*\*(.+?):?\*\*:?\s*(.+)$", rad)
        if not m:
            continue
        namn, forklaring = m.group(1).rstrip(":"), m.group(2).strip()
        alias = [a.strip() for a in re.split(r"\s+/\s+", namn) if a.strip()]
        ordlista.append({"ord": alias, "def": forklaring, "rubrik": alias[0]})

    radar = json.loads(las(ROT / "radar" / "radar.json") or "null")
    fonder = []
    for f in sorted(ROT.glob("fonder/*/fond.json")):
        fd = json.loads(las(f))
        fd["slug"] = f.parent.name
        fonder.append(fd)
    fonder.sort(key=lambda f: -(f.get("formogenhet_mdr") or 0))
    fondsignaler = json.loads(las(ROT / "fonder" / "fondsignaler.json") or "null")
    triage = (json.loads(las(ROT / "radar" / "triage.json") or "null") or {}).get("bolag", {})
    logg = andringar.uppdatera(ROT, bolag, radar, triage, (fondsignaler or {}).get("kvartal"))
    nyhetskoll = (json.loads(las(ROT / "nyhetskoll-senaste.json") or "null") or {}).get("kord")
    fondregister = (json.loads(las(ROT / "fonder" / "fondregister.json") or "null") or {}).get("fonder", [])
    fondsignaler_borsen = json.loads(las(ROT / "radar" / "fondsignaler-borsen.json") or "null")
    if fondsignaler_borsen:
        fondsignaler_borsen.pop("signaler", None)
        fondsignaler_borsen["tabell"] = [r for r in fondsignaler_borsen.get("tabell", []) if r["typ"] == "fondkop"][:60] + [r for r in fondsignaler_borsen.get("tabell", []) if r["typ"] == "fondflykt"][:20]
    data = {"byggd": datetime.now().strftime("%Y-%m-%d %H:%M"), "bolag": bolag, "teman": teman, "radar": radar, "fonder": fonder, "fondsignaler": fondsignaler, "fondregister": fondregister, "kalender_makro": (json.loads(las(ROT / "kalender.json") or "null") or {}).get("handelser", []), "andringar": logg[:250], "nyhetskoll_kord": nyhetskoll, "fondsignaler_borsen": fondsignaler_borsen,
            "metod": metod, "kastade": las(ROT / "kastade.md"), "ordlista": ordlista,
            "journal": las(ROT / "journal.md"),
            "guide": las(VERKTYG / "larande" / "guide.md"),
            "djupdykning": {"per_sondag": 5, "intervall_dagar": 27, **((json.loads(las(ROT / "installningar.json") or "{}").get("djupdykning")) or {})},
            "larande": json.loads(las(VERKTYG / "larande" / "lektioner.json") or '{"lektioner": []}')["lektioner"]}
    js = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    mall = las(VERKTYG / "verktyg" / "sida-mall.html")
    ut = ROT / "site" / "index.html"
    ut.parent.mkdir(exist_ok=True)
    mall = mall.replace("/*__PORTFOLJ__*/", las(VERKTYG / "verktyg" / "delar" / "portfolj.js"))
    ut.write_text(mall.replace("/*__DATA__*/null", js), encoding="utf-8")
    (ut.parent / ".verktyg-version").write_text(verktygsversion(), encoding="utf-8")
    print(f"Byggd: {ut} ({ut.stat().st_size // 1024} kB, {len(bolag)} bolag, {len(teman)} teman)")


if __name__ == "__main__":
    main()
