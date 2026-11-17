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
import karna  # noqa: E402  (kärnspåret: kvalitetsbetyg och pris mot egen historik, metod 22)



def trenddata():
    """Trendradarn (metod 21): trenderna och historiebiblioteket, med mätarna som serier att rita."""
    import trendmatare
    mapp = ROT / "trender"
    if not mapp.exists():
        return [], []
    bas = mapp / "_baslinje.json"
    trendmatare.BAS.update(json.loads(bas.read_text(encoding="utf-8")) if bas.exists() else {})
    sista = datetime.now().year - 1

    def forbered(p):
        t = json.loads(p.read_text(encoding="utf-8"))
        t.setdefault("slug", p.stem)
        visning = []
        for m in t.get("matare", []):
            s = trendmatare.relativ(m, trendmatare.fulla_ar(t.get("serier", {}).get(m["id"], {}).get("ar", {}), sista))
            if s:
                ar = sorted(s)
                auto = {"openalex": f'Forskning: {m.get("fraga")}', "kliniska": f'Kliniska prövningar: {m.get("fraga")}',
                        "wikipedia": f'Läsning: {str(m.get("fraga", "")).replace("_", " ")}',
                        "owid": f'{m.get("fraga", "").replace("-", " ")} ({m.get("entitet", "World")})'}.get(m.get("kalla"), m.get("fraga"))
                visning.append({"id": m["id"], "typ": m.get("typ"), "kalla": m.get("kalla"), "fraga": m.get("fraga"), "enhet": m.get("enhet"), "namn": m.get("namn") or auto,
                                "relativ": m.get("kalla") in ("openalex", "wikipedia"), "ar": ar, "v": [s[a] for a in ar]})
        t["visning"] = visning
        t.pop("serier", None)
        return t
    trender = [forbered(p) for p in sorted(mapp.glob("*.json")) if not p.name.startswith("_")]
    historia = [forbered(p) for p in sorted((mapp / "historia").glob("*.json"))]
    return trender, historia

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
        karna_res = None
        if status.get("spar") == "karna":
            arsd = json.loads(las(mapp / "arsdata.json") or "null")
            karna_res = karna.rakna(arsd, kurs, json.loads(las(mapp / "karna.json") or "null"), status.get("lynch")) if arsd else {"ok": False, "skal": "Årssiffrorna är inte hämtade än."}
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
                      "marknadsmodell": marknadsmodell, "panel": panel, "fondagare": fondagare, "karna": karna_res,
                      "djup_datum": [d["datum"] for d in djup]})
    ordning = {"Bevaka": 0, "Avvakta": 1, "Kasta": 2}
    bolag.sort(key=lambda b: (ordning.get(b["status"].get("beslut"), 3), -(b["status"].get("poang") or 0)))

    teman = [{"titel": titel_ur_md(las(p), p.stem), "md": las(p)} for p in sorted(ROT.glob("teman/*.md"), reverse=True)]
    trender, trendhistoria = trenddata()
    tb = ROT / "trender" / "_bank-sammanfattning.json"
    trendbank = json.loads(tb.read_text(encoding="utf-8")) if tb.exists() else None
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
    # Noteringsdatum från facit (Yahoo), så att nynoterade bolag kan märkas på radarn
    fr = ROT / "facit" / "resultat.json"
    if radar and fr.exists():
        from signalradar import normalisera
        noterad = {}
        for h in json.loads(fr.read_text(encoding="utf-8")).get("handelser", []):
            if (h.get("utfall") or {}).get("noterad"):
                noterad[normalisera(h.get("namn") or "")] = h["utfall"]["noterad"]
        for b in radar.get("bolag", []):
            b["noterad"] = noterad.get(normalisera(b["bolag"]))
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
    data = {"byggd": datetime.now().strftime("%Y-%m-%d %H:%M"), "bolag": bolag, "teman": teman, "trender": trender, "trendhistoria": trendhistoria, "trendbank": trendbank, "radar": radar, "fonder": fonder, "fondsignaler": fondsignaler, "fondregister": fondregister, "kalender_makro": (json.loads(las(ROT / "kalender.json") or "null") or {}).get("handelser", []), "andringar": logg[:250], "nyhetskoll_kord": nyhetskoll, "fondsignaler_borsen": fondsignaler_borsen,
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
