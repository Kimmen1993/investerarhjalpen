"""Ändringslogg för rutan "Nytt sedan sist" på Läget nu.

Varje gång sidan byggs jämförs datan med förra bygget (site/.forra-bygget.json). Det som är nytt
skrivs till site/andringar.json med tidpunkten för bygget. Sidan visar sedan bara det som har
kommit sedan användarens förra besök. Gratis, ingen AI.
"""
import json
from datetime import datetime, timedelta

TRAFIKLJUS = {"gron": "grönt", "gul": "gult", "rod": "rött"}


def _las(p, standard):
    try:
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else standard
    except (OSError, ValueError):
        return standard


def ogonblick(bolag, radar, triage, fond_kvartal):
    """Det som jämförs mellan två byggen."""
    return {
        "bolag": {b["slug"]: {
            "namn": b["status"].get("namn", b["slug"]),
            "beslut": b["status"].get("beslut"),
            "trafikljus": b["status"].get("trafikljus"),
            "spar": b["status"].get("spar"),
            "handelser": [f'{h.get("datum")}|{h.get("rubrik")}' for h in b.get("handelser") or []],
            "rapporter": [f'{r.get("datum")}|{r.get("typ")}' for r in b.get("rapporter") or []],
            "djup": sorted(b.get("djup_datum") or []),
            "panel": (b.get("panel") or {}).get("datum"),
        } for b in bolag},
        "radar": {r["nyckel"]: {"bolag": r["bolag"], "poang": r["poang"]} for r in (radar or {}).get("bolag", [])},
        "triage": {k: v.get("beslut") for k, v in (triage or {}).items()},
        "fond_kvartal": fond_kvartal,
    }


def jamfor(fore, nu, bolag, radar, triage, tid):
    ut = []
    per_slug = {b["slug"]: b for b in bolag}

    def lagg(typ, text, slug=None, namn=None, paverkan=None, lank=None):
        ut.append({"tid": tid, "typ": typ, "slug": slug, "namn": namn, "text": text, "paverkan": paverkan, "lank": lank})

    for slug, n in nu["bolag"].items():
        f = fore["bolag"].get(slug)
        namn = n["namn"]
        if not f:
            lagg("nytt_bolag", f"Nytt bevakat bolag ({n['beslut'] or 'Bevaka'})", slug, namn)
            continue
        if n["beslut"] != f["beslut"]:
            lagg("beslut", f"Beslutet ändrat: {f['beslut']} → {n['beslut']}", slug, namn, "forsvagar" if n["beslut"] == "Kasta" else None)
        if n["trafikljus"] != f["trafikljus"] and n["trafikljus"]:
            lagg("trafikljus", f"Trafikljuset ändrat: {TRAFIKLJUS.get(f['trafikljus'], 'ej bedömt')} → {TRAFIKLJUS.get(n['trafikljus'], n['trafikljus'])}", slug, namn,
                 "starker" if n["trafikljus"] == "gron" else "forsvagar")
        if n["spar"] != f["spar"] and n["spar"] and f["spar"]:
            lagg("spar", "Bytt spår", slug, namn)
        gamla = set(f["handelser"])
        for h in per_slug[slug].get("handelser") or []:
            if f'{h.get("datum")}|{h.get("rubrik")}' not in gamla:
                lagg("handelse", h.get("rubrik") or "Ny händelse", slug, namn, h.get("paverkan"), h.get("lank"))
        gamla_r = set(f["rapporter"])
        for r in per_slug[slug].get("rapporter") or []:
            if f'{r.get("datum")}|{r.get("typ")}' not in gamla_r:
                lagg("rapport", f"Ny rapport: {r.get('typ')} ({r.get('datum')})", slug, namn, None, r.get("pdf") or r.get("pm"))
        if n["djup"] and n["djup"] != f["djup"]:
            lagg("djupdykning", "Ny djupdykning", slug, namn)
        if n["panel"] and n["panel"] != f["panel"]:
            lagg("panel", "Investerarpanelen uppdaterad", slug, namn)
    for slug, f in fore["bolag"].items():
        if slug not in nu["bolag"]:
            lagg("bort", "Följs inte längre", slug, f["namn"])

    for k, r in nu["radar"].items():
        if k not in fore["radar"]:
            lagg("radar", f"Ny på radarn ({r['poang']:g} poäng)", None, r["bolag"])
    for k, beslut in nu["triage"].items():
        if fore["triage"].get(k) != beslut and beslut:
            namn = next((r["bolag"] for rk, r in nu["radar"].items() if rk == k), k)
            lagg("triage", f"Triagerad: {beslut}", None, namn, "starker" if beslut in ("Analysera", "Bevaka") else None)
    if nu["fond_kvartal"] and fore.get("fond_kvartal") and nu["fond_kvartal"] != fore["fond_kvartal"]:
        lagg("fonder", f"Nya fonddata från Finansinspektionen ({nu['fond_kvartal']})")
    return ut


def uppdatera(ROT, bolag, radar, triage, fond_kvartal):
    """Jämför med förra bygget, sparar nya ändringar och returnerar hela loggen (60 dagar)."""
    site = ROT / "site"
    site.mkdir(exist_ok=True)
    forra_fil, logg_fil = site / ".forra-bygget.json", site / "andringar.json"
    nu = ogonblick(bolag, radar, triage, fond_kvartal)
    tid = datetime.now().strftime("%Y-%m-%d %H:%M")
    logg = _las(logg_fil, {"andringar": []})["andringar"]
    fore = _las(forra_fil, None)
    if fore is None:
        # Första gången: börja med händelserna från de senaste 3 dagarna, så att rutan inte är tom.
        grans = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
        for b in bolag:
            for h in b.get("handelser") or []:
                if (h.get("datum") or "") >= grans:
                    logg.append({"tid": f'{h["datum"]} 08:00', "typ": "handelse", "slug": b["slug"], "namn": b["status"].get("namn"),
                                 "text": h.get("rubrik"), "paverkan": h.get("paverkan"), "lank": h.get("lank")})
        radarnamn = {r["nyckel"]: r["bolag"] for r in (radar or {}).get("bolag", [])}
        for k, v in (triage or {}).items():
            if (v.get("datum") or "") >= grans and v.get("beslut"):
                logg.append({"tid": f'{v["datum"]} 17:00', "typ": "triage", "slug": None, "namn": radarnamn.get(k, k),
                             "text": f'Triagerad: {v["beslut"]}', "paverkan": "starker" if v["beslut"] in ("Analysera", "Bevaka") else None, "lank": None})
    else:
        logg += jamfor(fore, nu, bolag, radar, triage, tid)
    grans = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")
    logg = sorted((x for x in logg if x["tid"] >= grans), key=lambda x: x["tid"], reverse=True)[:400]
    logg_fil.write_text(json.dumps({"andringar": logg}, ensure_ascii=False, indent=1), encoding="utf-8")
    forra_fil.write_text(json.dumps(nu, ensure_ascii=False), encoding="utf-8")
    return logg
