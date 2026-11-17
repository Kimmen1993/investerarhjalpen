#!/usr/bin/env python3
"""Börsdata – förberedd koppling (avstängd tills användaren har en egen API-nyckel).

Börsdata ger nyckeltal, rapporter och kurser för alla nordiska bolag via ett
officiellt API. Det kräver ett eget medlemskap (Pro för nordiska bolag enligt
Börsdatas sida, kontrollera före köp) och en personlig API-nyckel.

Villkor (Börsdata, 2026): data får bara användas för egen analys. Den får inte
delas med andra eller visas på webbsidor för andra. Varje användare av
Investerarhjälpen behöver därför ett eget konto och en egen nyckel, och sidan
ska bara visas för användaren själv.

Så slås kopplingen på (användaren gör det själv, Claude skriver aldrig in nyckeln):
1. Skaffa nyckeln under "API" på Min sida hos Börsdata.
2. Spara den i datamappen i filen privat/borsdata.json:  {"api_nyckel": "..."}
   eller i miljövariabeln BORSDATA_API_KEY.
3. Sätt "datakallor": {"borsdata": true} i installningar.json.
4. Testa:  python3 -I verktyg/borsdata.py --testa NOVO-B.CO
   Testet visar fältnamnen i Börsdatas svar, så att översättningen nedan kan
   kontrolleras. Den är skriven efter Börsdatas dokumentation och har inte
   kunnat provas utan nyckel.

Allt som hämtas här skrivs i samma format som de gratis källorna
(arsdata.json, nyckeltal.json, kurs.json). Resten av verktyget märker ingen skillnad,
förutom att "kalla" blir "borsdata".
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rot import DATA as ROT  # noqa: E402

BAS = "https://apiservice.borsdata.se/v1"
UA = {"User-Agent": "Mozilla/5.0 (investerarhjalpen borsdata)"}
CACHE = ROT / "privat" / "borsdata-instrument.json"
PAUS = 0.12  # Börsdata tillåter ca 100 anrop per 10 sekunder

# Börsdatas rapportfält → verktygets fält. Belopp i miljoner i rapportvalutan.
ARSFALT = {
    "omsattning": ["revenues", "net_Sales"],
    "bruttoresultat": ["gross_Income"],
    "rorelseresultat": ["operating_Income"],
    "resultat_fore_skatt": ["profit_Before_Tax"],
    "nettoresultat": ["profit_To_Equity_Holders"],
    "vinst_per_aktie": ["earnings_Per_Share"],
    "utdelning_per_aktie": ["dividend"],
    "kf_lopande": ["cash_Flow_From_Operating_Activities"],
    "kf_invest": ["cash_Flow_From_Investing_Activities"],
    "kf_finans": ["cash_Flow_From_Financing_Activities"],
    "fritt_kassaflode": ["free_Cash_Flow"],
    "kassa": ["cash_And_Equivalents"],
    "eget_kapital": ["total_Equity"],
    "totala_tillgangar": ["total_Assets"],
    "omsattningstillgangar": ["current_Assets"],
    "kortfristiga_skulder": ["current_Liabilities"],
    "langfristiga_skulder": ["non_Current_Liabilities"],
    "nettoskuld": ["net_Debt"],
    "aktier_milj": ["number_Of_Shares"],
    "kurs_snitt": ["stock_Price_Average"],
}


def aktiv():
    """Sant om användaren har slagit på Börsdata och har en nyckel."""
    inst = ROT / "installningar.json"
    try:
        pa = bool((json.loads(inst.read_text(encoding="utf-8")).get("datakallor") or {}).get("borsdata"))
    except Exception:
        pa = False
    return pa and bool(nyckel())


def nyckel():
    if os.environ.get("BORSDATA_API_KEY"):
        return os.environ["BORSDATA_API_KEY"].strip()
    f = ROT / "privat" / "borsdata.json"
    if f.exists():
        try:
            return (json.loads(f.read_text(encoding="utf-8")).get("api_nyckel") or "").strip() or None
        except Exception:
            return None
    return None


def hamta(vag, **param):
    k = nyckel()
    if not k:
        raise RuntimeError("Ingen Börsdata-nyckel. Se instruktionen överst i verktyg/borsdata.py.")
    url = f"{BAS}/{vag}?" + urllib.parse.urlencode({"authKey": k, **param})
    for forsok in range(4):
        try:
            time.sleep(PAUS)
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 429 and forsok < 3:
                time.sleep(3 * (forsok + 1))
                continue
            if e.code in (401, 403):
                raise RuntimeError("Börsdata nekade nyckeln. Kontrollera nyckeln och att medlemskapet ger API-åtkomst.") from None
            raise


def instrument(yahoo=None, isin=None):
    """Börsdatas instrument-id för ett bolag. Listan cachas i privat/ (den är bara till för användaren)."""
    lista = None
    if CACHE.exists() and CACHE.stat().st_mtime > time.time() - 7 * 86400:
        lista = json.loads(CACHE.read_text(encoding="utf-8"))
    if lista is None:
        lista = hamta("instruments").get("instruments", [])
        try:  # globala bolag kräver Pro+; saknas åtkomst används bara de nordiska
            lista += hamta("instruments/global").get("instruments", [])
        except Exception:
            pass
        CACHE.parent.mkdir(exist_ok=True)
        CACHE.write_text(json.dumps(lista, ensure_ascii=False), encoding="utf-8")
    for i in lista:
        if isin and (i.get("isin") or "").upper() == isin.upper():
            return i
        if yahoo and (i.get("yahoo") or "").upper() == yahoo.upper():
            return i
    return None


def _falt(rad, nycklar):
    for k in nycklar:
        if rad.get(k) is not None:
            return rad[k]
    return None


def arsdata(yahoo=None, isin=None, antal=20):
    """Årssiffror i samma form som esef.arsdata()."""
    ins = instrument(yahoo, isin)
    if not ins:
        raise RuntimeError(f"Hittade inte bolaget hos Börsdata (yahoo={yahoo}, isin={isin}).")
    d = hamta(f"instruments/{ins['insId']}/reports/year", maxCount=antal, original=1)
    ut = []
    for r in d.get("reports", []):
        rad = {"ar": r.get("year"), "slutdatum": (r.get("report_End_Date") or "")[:10] or None}
        for falt, nycklar in ARSFALT.items():
            rad[falt] = _falt(r, nycklar)
        if rad.get("kf_lopande") is not None and rad.get("fritt_kassaflode") is not None:
            rad["capex"] = round(rad["kf_lopande"] - rad["fritt_kassaflode"], 3)
        rad["kalla"] = "borsdata"
        ut.append(rad)
    valuta = (d.get("reports") or [{}])[0].get("currency") if d.get("reports") else None
    return {"valuta": valuta, "ar": sorted(ut, key=lambda x: x["ar"] or 0)}


def kvartal(yahoo=None, isin=None, antal=12):
    """Kvartalssiffror i samma form som nyckeltal.json (orderingång finns inte hos Börsdata)."""
    ins = instrument(yahoo, isin)
    if not ins:
        return []
    d = hamta(f"instruments/{ins['insId']}/reports/quarter", maxCount=antal, original=1)
    ut = []
    for r in d.get("reports", []):
        ut.append({"period": f"{r.get('year')} Q{r.get('period')}",
                   "omsattning": _falt(r, ["revenues", "net_Sales"]), "rorelseresultat": r.get("operating_Income"),
                   "kassa": r.get("cash_And_Equivalents"), "kf_lopande": r.get("cash_Flow_From_Operating_Activities"),
                   "kf_invest": r.get("cash_Flow_From_Investing_Activities"), "aktier_milj": r.get("number_Of_Shares")})
    return sorted(ut, key=lambda x: x["period"])


def kurs(yahoo=None, isin=None, dagar=95):
    """Senaste kurs och dagshistorik i samma form som nyhetskoll.kurs()."""
    ins = instrument(yahoo, isin)
    if not ins:
        raise RuntimeError("Bolaget finns inte hos Börsdata.")
    fran = (date.today() - timedelta(days=dagar)).isoformat()
    d = hamta(f"instruments/{ins['insId']}/stockprices", **{"from": fran})
    lista = sorted(d.get("stockPricesList", []), key=lambda p: p["d"])
    if not lista:
        raise RuntimeError("Inga kurser från Börsdata.")
    return {"symbol": yahoo or isin, "kurs": lista[-1]["c"], "valuta": None, "tid": lista[-1]["d"][:10],
            "kalla": "Börsdata (dagens stängning)",
            "historik": [{"datum": p["d"][:10], "stang": p["c"], "volym": p.get("v")} for p in lista]}


def testa(symbol):
    print("Nyckel hittad:", bool(nyckel()), "| påslagen i installningar.json:", aktiv())
    ins = instrument(yahoo=symbol) or instrument(isin=symbol)
    print("Instrument:", ins and {k: ins.get(k) for k in ("insId", "name", "ticker", "yahoo", "isin")})
    if not ins:
        return
    d = hamta(f"instruments/{ins['insId']}/reports/year", maxCount=2, original=1)
    r = (d.get("reports") or [{}])[0]
    print("Fält i årsrapporten:", sorted(r))
    saknas = [f for f, n in ARSFALT.items() if not any(k in r for k in n)]
    print("Fält som översättningen inte hittar:", saknas or "inga")
    print("Senaste året, översatt:", arsdata(yahoo=ins.get("yahoo"), isin=ins.get("isin"), antal=1)["ar"][-1:])


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "--testa":
        try:
            testa(sys.argv[2])
        except RuntimeError as e:
            print(e)
            sys.exit(1)
    else:
        print(__doc__)
