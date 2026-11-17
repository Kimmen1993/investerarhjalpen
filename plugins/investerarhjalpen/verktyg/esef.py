#!/usr/bin/env python3
"""ESEF – gratis årssiffror ur bolagens officiella årsredovisningar (ingen AI).

Börsbolag på EU:s reglerade marknader (till exempel Nasdaq Stockholms och
Köpenhamns huvudlistor) lämnar sedan 2020 sin årsredovisning i ett maskinläsbart
format (ESEF/iXBRL). Det öppna registret filings.xbrl.org samlar filerna och ger
dem som JSON. Det här skriptet hittar bolaget, hämtar alla årsredovisningar och
plockar ut ett fast antal nyckeltal per år i samma form som Börsdata ger
(se arsdata.py, som väljer källa).

Begränsningar:
- Bara bolag på huvudlistan. First North och Spotlight lämnar inte ESEF.
- Ungefär från räkenskapsåret 2019 (jämförelsesiffrorna i 2020 års fil).
- Bara standardbegrepp (ifrs-full). Bolagens egna begrepp läses inte, så till
  exempel låneskulder kan saknas. Saknade värden blir null och kan fyllas i
  för hand under "rattelser" i arsdata.json.

Kör:  python3 -I verktyg/esef.py <sökord>      (visar träffar och LEI-koder)
"""
import json
import sys
import time
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta

BAS = "https://filings.xbrl.org"
UA = {"User-Agent": "Mozilla/5.0 (investerarhjalpen esef)"}

# Fält → ifrs-begrepp i prioritetsordning. Första som finns används.
BEGREPP = {
    "omsattning": ["ifrs-full:Revenue", "ifrs-full:RevenueFromContractsWithCustomers"],
    "bruttoresultat": ["ifrs-full:GrossProfit"],
    "rorelseresultat": ["ifrs-full:ProfitLossFromOperatingActivities"],
    "resultat_fore_skatt": ["ifrs-full:ProfitLossBeforeTax"],
    "nettoresultat": ["ifrs-full:ProfitLossAttributableToOwnersOfParent", "ifrs-full:ProfitLoss", "ifrs-full:ProfitLossFromContinuingOperations"],
    "vinst_per_aktie": ["ifrs-full:BasicEarningsLossPerShare", "ifrs-full:BasicAndDilutedEarningsLossPerShare", "ifrs-full:DilutedEarningsLossPerShare", "ifrs-full:BasicEarningsLossPerShareFromContinuingOperations"],
    # Utdelning för räkenskapsåret (föreslagen till stämman). Den som betalats under året står i utdelning_betald.
    "utdelning_per_aktie": ["ifrs-full:DividendsProposedOrDeclaredBeforeFinancialStatementsAuthorisedForIssueButNotRecognisedAsDistributionToOwnersPerShare"],
    "avskrivningar": ["ifrs-full:DepreciationAndAmortisationExpense", "ifrs-full:DepreciationAmortisationAndImpairmentLossReversalOfImpairmentLossRecognisedInProfitOrLoss"],
    "kf_lopande": ["ifrs-full:CashFlowsFromUsedInOperatingActivities"],
    "kf_invest": ["ifrs-full:CashFlowsFromUsedInInvestingActivities"],
    "kf_finans": ["ifrs-full:CashFlowsFromUsedInFinancingActivities"],
    "utdelning_betald": ["ifrs-full:DividendsPaidClassifiedAsFinancingActivities", "ifrs-full:DividendsPaidToEquityHoldersOfParentClassifiedAsFinancingActivities", "ifrs-full:DividendsPaid", "ifrs-full:DividendsRecognisedAsDistributionsToOwnersOfParent"],
    "aterkop": ["ifrs-full:PaymentsToAcquireOrRedeemEntitysShares", "ifrs-full:PurchaseOfTreasuryShares"],
    "kassa": ["ifrs-full:CashAndCashEquivalents"],
    "eget_kapital": ["ifrs-full:EquityAttributableToOwnersOfParent", "ifrs-full:Equity"],
    "totala_tillgangar": ["ifrs-full:Assets"],
    "omsattningstillgangar": ["ifrs-full:CurrentAssets"],
    "kortfristiga_skulder": ["ifrs-full:CurrentLiabilities"],
    "langfristiga_skulder": ["ifrs-full:NoncurrentLiabilities"],
    "aktier_milj": ["ifrs-full:WeightedAverageShares"],
}
# Investeringar i anläggningar och immateriella tillgångar (summeras; capex)
CAPEX = ["ifrs-full:PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities",
         "ifrs-full:PurchaseOfPropertyPlantAndEquipment",
         "ifrs-full:PurchaseOfIntangibleAssetsClassifiedAsInvestingActivities",
         "ifrs-full:PurchaseOfIntangibleAssets"]
# Räntebärande skulder: lån (lång + kort) och leasingskulder. Summeras om alla delar finns.
LAN_LANG = ["ifrs-full:NoncurrentPortionOfNoncurrentBorrowings", "ifrs-full:LongtermBorrowings", "ifrs-full:NoncurrentBorrowings"]
LAN_KORT = ["ifrs-full:CurrentBorrowingsAndCurrentPortionOfNoncurrentBorrowings", "ifrs-full:ShorttermBorrowings", "ifrs-full:CurrentPortionOfNoncurrentBorrowings"]
LAN_TOTAL = ["ifrs-full:Borrowings"]
LEASING = [["ifrs-full:LeaseLiabilities"], ["ifrs-full:NoncurrentLeaseLiabilities"], ["ifrs-full:CurrentLeaseLiabilities"]]
PER_AKTIE = {"vinst_per_aktie", "utdelning_per_aktie"}
ANTAL = {"aktier_milj"}
TILLATNA_DIM = {"concept", "entity", "period", "unit", "language"}


def hamta(url, timeout=60, forsok=3):
    for i in range(forsok):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
                return json.loads(r.read())
        except Exception:
            if i == forsok - 1:
                raise
            time.sleep(2 * (i + 1))


def filter_url(vag, filt, storlek=100):
    return f"{BAS}/api/{vag}?" + urllib.parse.urlencode({"filter": json.dumps(filt), "page[size]": storlek})


def sok(namn):
    """Bolag i registret vars namn innehåller sökordet: [(lei, namn)]."""
    d = hamta(filter_url("entities", [{"name": "name", "op": "ilike", "val": f"%{namn}%"}], 20))
    return [(e["attributes"]["identifier"], e["attributes"]["name"]) for e in d.get("data", [])]


def filer(lei):
    d = hamta(filter_url("filings", [{"name": "entity.identifier", "op": "eq", "val": lei}]))
    ut = [f["attributes"] for f in d.get("data", []) if f["attributes"].get("json_url")]
    return sorted(ut, key=lambda a: a["period_end"])


def _datum(s):
    return datetime.fromisoformat(s[:19]).date()


def _period(p):
    """('varaktighet', start, slut) eller ('punkt', None, dag). Slutet i xBRL-JSON är exklusivt."""
    if "/" in p:
        a, b = p.split("/")
        return "varaktighet", _datum(a), _datum(b) - timedelta(days=1)
    return "punkt", None, _datum(p) - timedelta(days=1)


def _skala(falt, enhet, v):
    if falt in PER_AKTIE:
        return round(v, 4)
    if falt in ANTAL:
        return round(v / 1e6, 4) if v > 0 else None
    return round(v / 1e6, 3) if enhet.startswith("iso4217:") else None


def las_fil(attr):
    """Årsvärden ur en ESEF-fil: {slutdatum: {fält: värde}}, plus valuta och om det är en årsredovisning."""
    d = hamta(BAS + attr["json_url"], timeout=120)
    ar_slut = {}
    valuta = None
    per_begrepp = {}
    for f in d.get("facts", {}).values():
        dim = f.get("dimensions", {})
        if set(dim) - TILLATNA_DIM or "unit" not in dim:
            continue
        try:
            v = float(f["value"])
        except (TypeError, ValueError):
            continue
        typ, start, slut = _period(dim["period"])
        if typ == "varaktighet" and not (350 <= (slut - start).days <= 380):
            continue  # bara helår; kvartal och halvår hoppas över
        per_begrepp.setdefault(dim["concept"], {})[slut] = (v, dim["unit"])
        if dim["unit"].startswith("iso4217:") and "/" not in dim["unit"]:
            valuta = dim["unit"].split(":")[1]
    if not any(k in per_begrepp for k in BEGREPP["omsattning"] + BEGREPP["nettoresultat"]):
        return {}, valuta
    slutdagar = set()
    for k in BEGREPP["nettoresultat"] + BEGREPP["omsattning"]:
        slutdagar |= set(per_begrepp.get(k, {}))

    def forsta(begrepp, slut, falt=None):
        for k in begrepp:
            if slut in per_begrepp.get(k, {}):
                v, enhet = per_begrepp[k][slut]
                return _skala(falt or "belopp", enhet, v)
        return None

    for slut in slutdagar:
        rad = {falt: forsta(bg, slut, falt) for falt, bg in BEGREPP.items()}
        delar = [forsta([k], slut) for k in CAPEX]
        ppe = next((x for x in delar[:2] if x is not None), None)
        imm = next((x for x in delar[2:] if x is not None), None)
        rad["capex"] = None if ppe is None and imm is None else round(abs(ppe or 0) + abs(imm or 0), 3)
        lan = forsta(LAN_TOTAL, slut)
        if lan is None:
            lang, kort = forsta(LAN_LANG, slut), forsta(LAN_KORT, slut)
            lan = None if lang is None and kort is None else round((lang or 0) + (kort or 0), 3)
        leas = forsta(LEASING[0], slut)
        if leas is None:
            ll, lk = forsta(LEASING[1], slut), forsta(LEASING[2], slut)
            leas = None if ll is None and lk is None else round((ll or 0) + (lk or 0), 3)
        if rad["aktier_milj"] is None and rad["vinst_per_aktie"] and rad["nettoresultat"]:
            rad["aktier_milj"] = round(rad["nettoresultat"] / rad["vinst_per_aktie"], 2)  # beräknat: vinst / vinst per aktie
        rad["lan"] = lan
        rad["leasingskulder"] = leas
        for k in ("utdelning_betald", "aterkop"):
            if rad[k] is not None:
                rad[k] = abs(rad[k])
        ar_slut[slut] = rad
    return ar_slut, valuta


def arsdata(lei, logg=print):
    """Alla år ur alla filer. Nyare filer skriver över äldre (rättade jämförelsesiffror).
    Returnerar {"valuta", "ar": [{ar, ...fält, kalla_fil}]}."""
    alla = {}
    valuta = None
    for attr in filer(lei):
        try:
            rader, val = las_fil(attr)
        except Exception as e:
            logg(f"  ESEF {attr['period_end']}: kunde inte läsas ({e})")
            continue
        if not rader:
            continue  # delårsrapport
        valuta = val or valuta
        for slut, rad in rader.items():
            gammal = alla.get(slut, {})
            ny = {k: v for k, v in rad.items() if v is not None}
            alla[slut] = {**gammal, **ny, "_fil": attr["period_end"]}
        logg(f"  ESEF {attr['period_end']}: {len(rader)} år lästa")
    ut = []
    for slut in sorted(alla):
        rad = alla[slut]
        ut.append({"ar": slut.year if slut.month >= 6 else slut.year - 1, "slutdatum": slut.isoformat(), **{k: rad.get(k) for k in list(BEGREPP) + ["capex", "lan", "leasingskulder"]},
                   "kalla": "esef", "kalla_fil": rad["_fil"]})
    return {"valuta": valuta, "ar": ut}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    for lei, namn in sok(" ".join(sys.argv[1:])):
        print(lei, namn)
