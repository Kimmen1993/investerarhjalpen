#!/usr/bin/env python3
"""Årsdata – tio års siffror per bolag i ett gemensamt format (metod 22).

Väljer källa i den här ordningen:
  1. Börsdata, om användaren har slagit på det (borsdata.py, kostar ett eget medlemskap)
  2. ESEF, bolagens officiella maskinläsbara årsredovisningar (esef.py, gratis)
  3. Rapporter som Claude har läst (rader med "kalla": "rapport" behålls alltid
     för år som de andra källorna inte har)
Ovanpå läggs "rattelser" (handinmatade värden med källa), som aldrig skrivs över.
Årsslutskurser och aktiesplittar hämtas gratis från Yahoo, så att värderingen
kan jämföras med bolagets egen historik.

Kör:  python3 -I "$IH/verktyg/arsdata.py" <bolagsmapp> [<bolagsmapp> ...]
      python3 -I "$IH/verktyg/arsdata.py" --karna      (alla bolag i spåret Kärna)
Skriver bolag/<namn>/arsdata.json.
"""
import json
import sys
import urllib.parse
import urllib.request
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rot import DATA as ROT  # noqa: E402
import esef  # noqa: E402
import borsdata  # noqa: E402

UA = {"User-Agent": "Mozilla/5.0 (investerarhjalpen arsdata)"}
FALT = ["omsattning", "bruttoresultat", "rorelseresultat", "resultat_fore_skatt", "nettoresultat", "vinst_per_aktie",
        "utdelning_per_aktie", "avskrivningar", "kf_lopande", "kf_invest", "kf_finans", "capex", "utdelning_betald", "aterkop",
        "kassa", "eget_kapital", "totala_tillgangar", "omsattningstillgangar", "kortfristiga_skulder", "langfristiga_skulder",
        "lan", "leasingskulder", "nettoskuld", "aktier_milj"]
PER_AKTIE = ("vinst_per_aktie", "utdelning_per_aktie")


def yahoo_historik(symbol):
    """Månadskurser (justerade för split) och splittar från Yahoo. Gratis men inofficiellt."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(symbol)}?range=max&interval=1mo&events=split"
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
        d = json.loads(r.read())["chart"]["result"][0]
    stang = d["indicators"]["quote"][0].get("close", [])
    arsslut = {}
    for t, c in zip(d.get("timestamp", []), stang):
        if c is not None:
            arsslut[datetime.fromtimestamp(t).year] = round(c, 3)  # sista månaden som finns för året
    splittar = [{"datum": datetime.fromtimestamp(s["date"]).date().isoformat(), "faktor": s["numerator"] / s["denominator"]}
                for s in (d.get("events", {}).get("splits") or {}).values()]
    return arsslut, sorted(splittar, key=lambda s: s["datum"]), d["meta"].get("currency")


def justera_split(rad, splittar):
    """ESEF-rader ur filer från före en split räknas om till dagens antal aktier."""
    fil = rad.get("kalla_fil")
    if not fil:
        return
    faktor = 1.0
    for s in splittar:
        if fil < s["datum"]:
            faktor *= s["faktor"]
    if faktor != 1.0:
        for k in PER_AKTIE:
            if rad.get(k) is not None:
                rad[k] = round(rad[k] / faktor, 4)
        if rad.get("aktier_milj") is not None:
            rad["aktier_milj"] = round(rad["aktier_milj"] * faktor, 3)
        rad["split_justerad"] = faktor


def hitta_lei(status):
    kb = status.get("kallor_bevakning") or {}
    if kb.get("lei"):
        return kb["lei"]
    import re
    rensa = lambda s: re.sub(r"\b(ab|a/s|asa|oyj|abp|plc|s\.?a\.?|n\.?v\.?|se|ag|publ|group|holding)\b|[().,]", " ", s.lower()).split()
    namn = status.get("namn", "")
    for sokord in (namn, namn.split()[0] if namn else ""):
        if not sokord:
            continue
        traffar = esef.sok(sokord)
        exakta = [t for t in traffar if rensa(t[1]) == rensa(namn)]
        if len(exakta) == 1:
            return exakta[0][0]
        borjar = [t for t in traffar if " ".join(rensa(t[1])).startswith(" ".join(rensa(namn)))]
        if len(borjar) == 1:
            return borjar[0][0]
    return None  # osäkert: skriv in "lei" i kallor_bevakning för hand (python3 -I esef.py <namn> visar koderna)


def uppdatera(mapp, logg=print):
    status_fil = mapp / "status.json"
    status = json.loads(status_fil.read_text(encoding="utf-8"))
    kb = status.get("kallor_bevakning") or {}
    fil = mapp / "arsdata.json"
    gammal = json.loads(fil.read_text(encoding="utf-8")) if fil.exists() else {}
    rattelser = gammal.get("rattelser", {})
    rapport_rader = {r["ar"]: r for r in gammal.get("ar", []) if r.get("kalla") == "rapport"}

    kalla, data, anm = None, None, []
    if borsdata.aktiv():
        try:
            data, kalla = borsdata.arsdata(yahoo=kb.get("yahoo"), isin=status.get("isin")), "borsdata"
        except Exception as e:
            anm.append(f"Börsdata gick inte att använda ({e}). Gratis källor används i stället.")
    if data is None:
        lei = hitta_lei(status)
        if lei:
            if kb.get("lei") != lei:
                status.setdefault("kallor_bevakning", {})["lei"] = lei
                status_fil.write_text(json.dumps(status, ensure_ascii=False, indent=1), encoding="utf-8")
            data, kalla = esef.arsdata(lei, logg), "esef"
            if not data["ar"]:
                anm.append("Bolaget finns i ESEF-registret men inga årsredovisningar kunde läsas.")
        else:
            anm.append("Bolaget finns inte i ESEF-registret (gäller till exempel First North). Årssiffrorna får läsas ur årsredovisningarna och sparas med \"kalla\": \"rapport\".")
            data = {"valuta": gammal.get("valuta"), "ar": []}

    rader = {r["ar"]: r for r in data["ar"] if r.get("ar")}
    for ar, r in rapport_rader.items():
        if ar not in rader:
            rader[ar] = r
    valuta = data.get("valuta") or gammal.get("valuta")

    arsslut, splittar, kursvaluta = {}, [], None
    if kb.get("yahoo"):
        try:
            arsslut, splittar, kursvaluta = yahoo_historik(kb["yahoo"])
        except Exception as e:
            anm.append(f"Årsslutskurser från Yahoo saknas ({e}).")
    if kursvaluta and valuta and kursvaluta != valuta:
        anm.append(f"Kursen är i {kursvaluta} men rapporterna i {valuta}. Värderingen mot historiken räknas inte.")
        arsslut = {}

    ut = []
    for ar in sorted(rader):
        r = {k: rader[ar].get(k) for k in ["ar", "slutdatum", *FALT, "kurs_snitt", "kalla", "kalla_fil", "niva"] if k in rader[ar] or k in FALT}
        if r.get("kalla") == "esef":
            justera_split(r, splittar)
        for k, v in (rattelser.get(str(ar)) or {}).items():
            if k in FALT:
                r[k] = v
                r.setdefault("rattat", []).append(k)
        if r.get("kurs_arsslut") is None and ar in arsslut:
            r["kurs_arsslut"] = arsslut[ar]
        r["niva"] = r.get("niva") or "A"
        ut.append(r)

    res = {"bolag": status.get("namn"), "valuta": valuta, "enhet": "miljoner", "uppdaterad": date.today().isoformat(),
           "kalla": {"borsdata": "Börsdata (eget medlemskap)", "esef": "Bolagets årsredovisningar i ESEF-format via filings.xbrl.org (gratis, officiellt)"}.get(kalla, "Årsredovisningar lästa av Claude"),
           "kurser": "Årsslutskurser från Yahoo Finance, justerade för aktiesplittar" if arsslut else None,
           "splittar": splittar, "anmarkningar": anm, "ar": ut, "rattelser": rattelser,
           "rattelser_hjalp": "Handinmatade värden per år, t.ex. {\"2024\": {\"lan\": 145.0}}. Skrivs aldrig över. Skriv källan i kallor.md."}
    fil.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    logg(f"{mapp.name}: {len(ut)} år ({ut[0]['ar'] if ut else '–'}–{ut[-1]['ar'] if ut else '–'}), källa {kalla or 'rapport'}" + (f". OBS: {' '.join(anm)}" if anm else ""))
    return res


def main():
    arg = sys.argv[1:]
    if not arg:
        print(__doc__)
        sys.exit(1)
    if arg == ["--karna"]:
        mappar = [p.parent for p in sorted(ROT.glob("bolag/*/status.json"))
                  if json.loads(p.read_text(encoding="utf-8")).get("spar") == "karna"]
    else:
        mappar = [ROT / "bolag" / a if not Path(a).is_dir() else Path(a) for a in arg]
    for m in mappar:
        try:
            uppdatera(m)
        except Exception as e:
            print(f"{m.name}: FEL {e}")


if __name__ == "__main__":
    main()
