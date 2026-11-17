#!/usr/bin/env python3
"""Kärnspåret – kvalitet och pris för lönsamma bolag (metod 22). Gratis, ingen AI.

Läser bolag/<namn>/arsdata.json (årssiffror), kurs.json (dagens kurs) och
karna.json (det som skrivs för hand: temahävstången). Räknar fram:
  - nyckeltal år för år (marginaler, avkastning på kapitalet, fritt kassaflöde)
  - kvalitetsbetyget A–D (sex delar, 0–2 poäng var)
  - kvalitetslinserna: Buffett/Munger, Terry Smith, Graham, Lynch, Piotroski och utdelning
  - värderingen nu jämfört med bolagets egen historik
  - temahävstången: hur mycket en snabbväxande nisch kan lyfta hela bolaget

Alla gränser står i metod 22. Ändras en gräns här ska metoden ändras också.
Körs automatiskt av bygg_sida.py för bolag i spåret Kärna. Kan köras för hand:
  python3 -I "$IH/verktyg/karna.py" <bolagsmapp>
"""
import json
import statistics
import sys
from pathlib import Path

# Gränser (samma siffror som i metod 22)
GRANS = {
    "roe_buffett": 15, "roe_andel_ar": 0.7, "roce_smith": 20, "brutto_smith": 40, "fcf_konv_smith": 90,
    "graham_pe": 15, "graham_pe_pb": 22.5, "graham_current": 2.0, "peg_billig": 1.0, "peg_dyr": 2.0,
    "betyg_A": 10, "betyg_B": 7, "betyg_C": 4, "billig": 0.8, "dyr": 1.2,
}


def _d(a, b):
    return None if a is None or b in (None, 0) else a / b


def _pct(a, b):
    v = _d(a, b)
    return None if v is None else round(v * 100, 1)


def _snitt(xs):
    xs = [x for x in xs if x is not None]
    return round(sum(xs) / len(xs), 1) if xs else None


def _median(xs):
    xs = [x for x in xs if x is not None]
    return round(statistics.median(xs), 1) if xs else None


def _cagr(forst, sist, ar):
    if forst is None or sist is None or forst <= 0 or sist <= 0 or ar <= 0:
        return None
    return round(((sist / forst) ** (1 / ar) - 1) * 100, 1)


def per_ar(rader):
    """Nyckeltal år för år."""
    ut = []
    forra = None
    for r in rader:
        capex = r.get("capex")
        fcf = r.get("fritt_kassaflode")
        if fcf is None and r.get("kf_lopande") is not None and capex is not None:
            fcf = r["kf_lopande"] - abs(capex)
        syss = None if r.get("totala_tillgangar") is None or r.get("kortfristiga_skulder") is None else r["totala_tillgangar"] - r["kortfristiga_skulder"]
        ek_snitt = r.get("eget_kapital")
        if forra and forra.get("eget_kapital") is not None and ek_snitt is not None:
            ek_snitt = (ek_snitt + forra["eget_kapital"]) / 2
        skuld = r.get("nettoskuld")
        if skuld is None and r.get("lan") is not None and r.get("kassa") is not None:
            skuld = r["lan"] + (r.get("leasingskulder") or 0) - r["kassa"]
        kurs = r.get("kurs_arsslut") or r.get("kurs_snitt")
        borsvarde = kurs * r["aktier_milj"] if kurs and r.get("aktier_milj") else None
        ev = borsvarde + skuld if borsvarde is not None and skuld is not None else None
        ut.append({
            "ar": r["ar"], "omsattning": r.get("omsattning"), "rorelseresultat": r.get("rorelseresultat"),
            "nettoresultat": r.get("nettoresultat"), "vinst_per_aktie": r.get("vinst_per_aktie"),
            "utdelning_per_aktie": r.get("utdelning_per_aktie"), "fritt_kassaflode": None if fcf is None else round(fcf, 1),
            "bruttomarginal": _pct(r.get("bruttoresultat"), r.get("omsattning")),
            "rorelsemarginal": _pct(r.get("rorelseresultat"), r.get("omsattning")),
            "roe": _pct(r.get("nettoresultat"), ek_snitt),
            "roce": _pct(r.get("rorelseresultat"), syss),
            "fcf_konvertering": _pct(fcf, r.get("nettoresultat")) if (r.get("nettoresultat") or 0) > 0 else None,
            "soliditet": _pct(r.get("eget_kapital"), r.get("totala_tillgangar")),
            "nettoskuld": None if skuld is None else round(skuld, 1),
            "skuld_ggr_resultat": None if skuld is None or not r.get("rorelseresultat") or r["rorelseresultat"] <= 0 else round(skuld / r["rorelseresultat"], 2),
            "current_ratio": None if _d(r.get("omsattningstillgangar"), r.get("kortfristiga_skulder")) is None else round(_d(r["omsattningstillgangar"], r["kortfristiga_skulder"]), 2),
            "aktier_milj": r.get("aktier_milj"), "utdelning_betald": r.get("utdelning_betald"), "aterkop": r.get("aterkop"),
            "kurs": kurs, "pe": None if not kurs or not r.get("vinst_per_aktie") or r["vinst_per_aktie"] <= 0 else round(kurs / r["vinst_per_aktie"], 1),
            "ev_ebit": None if ev is None or not r.get("rorelseresultat") or r["rorelseresultat"] <= 0 else round(ev / r["rorelseresultat"], 1),
            "fcf_avkastning": _pct(fcf, borsvarde) if borsvarde else None,
            "pb": None if not borsvarde or not r.get("eget_kapital") or r["eget_kapital"] <= 0 else round(borsvarde / r["eget_kapital"], 1),
        })
        forra = r
    return ut


def _t(v):
    """Tal med svenskt decimaltecken i förklaringstexterna."""
    return "?" if v is None else str(v).replace(".", ",")


def _punkt(namn, varde, uppfylld, forklaring, enhet=""):
    return {"namn": namn, "varde": varde, "enhet": enhet, "uppfylld": uppfylld, "forklaring": forklaring}


def piotroski(a, b):
    """Piotroskis F-poäng (0–9): senaste året (a) mot året innan (b)."""
    if not a or not b:
        return None
    def roa(x):
        return _d(x.get("nettoresultat"), x.get("totala_tillgangar"))
    def lev(x):
        return _d(x.get("langfristiga_skulder"), x.get("totala_tillgangar"))
    def cur(x):
        return _d(x.get("omsattningstillgangar"), x.get("kortfristiga_skulder"))
    def brutto(x):
        return _d(x.get("bruttoresultat"), x.get("omsattning"))
    def oms_tillg(x):
        return _d(x.get("omsattning"), x.get("totala_tillgangar"))
    def jmf(f, storre=True):
        x, y = f(a), f(b)
        if x is None or y is None:
            return None
        return x > y if storre else x < y
    tester = [
        ("Vinst (avkastning på tillgångarna över noll)", None if roa(a) is None else roa(a) > 0),
        ("Positivt kassaflöde från verksamheten", None if a.get("kf_lopande") is None else a["kf_lopande"] > 0),
        ("Avkastningen på tillgångarna ökade", jmf(roa)),
        ("Kassaflödet större än vinsten", None if a.get("kf_lopande") is None or a.get("nettoresultat") is None else a["kf_lopande"] > a["nettoresultat"]),
        ("Lägre långfristig skuld i förhållande till tillgångarna", jmf(lev, False)),
        ("Bättre betalningsförmåga på kort sikt", jmf(cur)),
        ("Inga nya aktier", None if a.get("aktier_milj") is None or b.get("aktier_milj") is None else a["aktier_milj"] <= b["aktier_milj"] * 1.005),
        ("Högre bruttomarginal (eller rörelsemarginal)", jmf(brutto) if brutto(a) is not None else jmf(lambda x: _d(x.get("rorelseresultat"), x.get("omsattning")))),
        ("Mer försäljning per krona i tillgångar", jmf(oms_tillg)),
    ]
    kanda = [t for t in tester if t[1] is not None]
    return {"poang": sum(1 for t in kanda if t[1]), "av": len(kanda), "ar": a["ar"],
            "tester": [{"namn": n, "uppfylld": v} for n, v in tester]}


def rakna(arsdata, kurs=None, manuell=None):
    rader = [r for r in (arsdata or {}).get("ar", []) if r.get("ar")]
    if len(rader) < 3:
        return {"ok": False, "skal": "Färre än tre år med siffror. Kör arsdata.py, eller läs in årsredovisningarna (metod 22)."}
    rader = sorted(rader, key=lambda r: r["ar"])[-10:]
    ar = per_ar(rader)
    sist, forst = ar[-1], ar[0]
    n_ar = sist["ar"] - forst["ar"]
    G = GRANS

    roce_snitt = _snitt(a["roce"] for a in ar)
    roe_lista = [a["roe"] for a in ar if a["roe"] is not None]
    fcf_konv = _snitt(a["fcf_konvertering"] for a in ar)
    brutto = _snitt(a["bruttomarginal"] for a in ar)
    oms_cagr = _cagr(forst["omsattning"], sist["omsattning"], n_ar)
    eps_alla = [a for a in ar if a["vinst_per_aktie"] is not None]
    forsta_pos = next((i for i, a in enumerate(eps_alla) if a["vinst_per_aktie"] > 0), len(eps_alla))
    eps_lista = eps_alla[forsta_pos:]  # tillväxten räknas från första året med vinst
    eps_cagr = _cagr(eps_lista[0]["vinst_per_aktie"], eps_lista[-1]["vinst_per_aktie"], eps_lista[-1]["ar"] - eps_lista[0]["ar"]) if len(eps_lista) >= 3 else None
    vinst_alla = all((a["nettoresultat"] or 0) > 0 for a in ar if a["nettoresultat"] is not None)
    fall = sum(1 for x, y in zip(ar, ar[1:]) if x["rorelseresultat"] and y["rorelseresultat"] is not None and y["rorelseresultat"] < x["rorelseresultat"] * 0.9)
    aktier = [a["aktier_milj"] for a in ar if a["aktier_milj"]]
    utspadning = round((aktier[-1] / aktier[0] - 1) * 100, 1) if len(aktier) >= 2 else None
    utd_ar = [a for a in ar if a["utdelning_betald"] is not None or a["utdelning_per_aktie"] is not None]
    utd_alla = bool(utd_ar) and all((a["utdelning_betald"] or a["utdelning_per_aktie"] or 0) > 0 for a in ar[1:])

    # Kvalitetsbetyget: sex delar, 0–2 poäng var
    def steg(v, hog, lag):
        return None if v is None else (2 if v >= hog else 1 if v >= lag else 0)
    if sist["skuld_ggr_resultat"] is not None or (sist["nettoskuld"] is not None and sist["nettoskuld"] <= 0):
        skuld_v = sist["skuld_ggr_resultat"] if sist["nettoskuld"] > 0 else 0
        balans = 2 if skuld_v < 1 else 1 if skuld_v < 3 else 0
        balans_txt = "nettokassa" if sist["nettoskuld"] <= 0 else f"nettoskulden är {_t(skuld_v)} gånger rörelseresultatet"
    elif sist["soliditet"] is not None:
        balans = steg(sist["soliditet"], 40, 25)
        balans_txt = f"soliditet {_t(sist['soliditet'])} % (låneskulderna saknas i källan)"
    else:
        balans, balans_txt = None, "saknas"
    agare, varje_ar = None, False
    if utspadning is not None:
        varje_ar = all((a["utdelning_betald"] or 0) > 0 or (a["aterkop"] or 0) > 0 or (a["utdelning_per_aktie"] or 0) > 0 for a in ar[1:])
        agare = (1 if utspadning <= 2 else 0) + (1 if varje_ar else 0)
    delar = [
        {"namn": "Lönsamhet", "fraga": "Tjänar bolaget mycket på pengarna som är insatta i verksamheten?", "poang": steg(roce_snitt, 20, 12),
         "skal": f"Avkastning på sysselsatt kapital i snitt {_t(roce_snitt)} % ({forst['ar']}–{sist['ar']}). 2 poäng från 20 %, 1 poäng från 12 %." if roce_snitt is not None else "Saknas."},
        {"namn": "Stabilitet", "fraga": "Går det med vinst varje år, utan stora ras?", "poang": (0 if not vinst_alla else 2 if fall <= 1 else 1),
         "skal": f"{'Vinst alla år' if vinst_alla else 'Förlust något år'}, {fall} år då rörelseresultatet föll mer än 10 %."},
        {"namn": "Kassaflöde", "fraga": "Blir vinsten riktiga pengar på kontot?", "poang": steg(fcf_konv, 90, 60),
         "skal": f"I snitt blev {_t(fcf_konv)} % av vinsten fritt kassaflöde. 2 poäng från 90 %, 1 poäng från 60 %." if fcf_konv is not None else "Investeringarna saknas i källan."},
        {"namn": "Balans", "fraga": "Klarar bolaget en kris utan att låna eller ge ut aktier?", "poang": balans, "skal": f"Senaste året: {balans_txt}."},
        {"namn": "Tillväxt", "fraga": "Växer försäljningen?", "poang": steg(oms_cagr, 10, 4),
         "skal": f"Försäljningen växte i snitt {_t(oms_cagr)} % per år. 2 poäng från 10 %, 1 poäng från 4 %." if oms_cagr is not None else "Saknas."},
        {"namn": "Ägarvänlighet", "fraga": "Får ägarna del av pengarna utan att spädas ut?", "poang": agare,
         "skal": (f"Antalet aktier ändrades {'+' if utspadning > 0 else ''}{_t(utspadning)} %. " if utspadning is not None else "") + ("Utdelning eller återköp varje år." if agare is not None and varje_ar else "Inte utdelning eller återköp varje år.")},
    ]
    kanda = [d for d in delar if d["poang"] is not None]
    summa = sum(d["poang"] for d in kanda)
    if len(kanda) < 4:
        betyg = "?"
    else:
        skalad = summa * 6 / len(kanda)
        betyg = "A" if skalad >= G["betyg_A"] else "B" if skalad >= G["betyg_B"] else "C" if skalad >= G["betyg_C"] else "D"

    # Pris nu
    pris = (kurs or {}).get("kurs")
    pris_valuta = (kurs or {}).get("valuta")
    if pris_valuta and arsdata.get("valuta") and pris_valuta != arsdata["valuta"]:
        pris = None
    nu = {}
    if pris:
        eps = sist["vinst_per_aktie"]
        bv = pris * sist["aktier_milj"] if sist["aktier_milj"] else None
        nu = {"kurs": pris, "kurs_datum": (kurs or {}).get("tid"), "baserat_pa_ar": sist["ar"],
              "pe": round(pris / eps, 1) if eps and eps > 0 else None,
              "ev_ebit": round((bv + sist["nettoskuld"]) / sist["rorelseresultat"], 1) if bv and sist["nettoskuld"] is not None and (sist["rorelseresultat"] or 0) > 0 else None,
              "fcf_avkastning": _pct(sist["fritt_kassaflode"], bv) if bv and sist["fritt_kassaflode"] is not None else None,
              "direktavkastning": _pct(sist["utdelning_per_aktie"], pris) if sist["utdelning_per_aktie"] else None,
              "pb": round(bv / rader[-1]["eget_kapital"], 1) if bv and (rader[-1].get("eget_kapital") or 0) > 0 else None,
              "borsvarde": round(bv) if bv else None}

    def jamfor(namn, nyckel, lagre_billigare=True):
        hist = [a[nyckel] for a in ar if a[nyckel] is not None]
        if not nu.get(nyckel) or len(hist) < 3:
            return None
        med = _median(hist)
        kvot = nu[nyckel] / med if med else None
        if kvot is None:
            return None
        if not lagre_billigare:
            kvot = 1 / kvot if kvot else None
        lage = "billigare än vanligt" if kvot < G["billig"] else "dyrare än vanligt" if kvot > G["dyr"] else "ungefär som vanligt"
        return {"namn": namn, "nu": nu[nyckel], "median": med, "min": min(hist), "max": max(hist), "lage": lage, "ar": f"{ar[0]['ar']}–{ar[-1]['ar']}"}
    historik = [x for x in [jamfor("P/E-tal", "pe"), jamfor("EV/EBIT", "ev_ebit"), jamfor("Fritt kassaflöde i % av börsvärdet", "fcf_avkastning", False)] if x]
    lagen = [h["lage"] for h in historik]
    vard_sammanfattning = None
    if lagen:
        vard_sammanfattning = max(set(lagen), key=lagen.count) if len(set(lagen)) < len(lagen) or len(lagen) == 1 else "spretigt: måtten pekar åt olika håll"

    # Linserna
    roe_ok = sum(1 for x in roe_lista if x >= G["roe_buffett"])
    pe_snitt3 = None
    if pris and len(eps_lista) >= 3:
        s3 = sum(a["vinst_per_aktie"] for a in eps_lista[-3:]) / 3
        pe_snitt3 = round(pris / s3, 1) if s3 > 0 else None
    peg = round(nu["pe"] / eps_cagr, 2) if nu.get("pe") and eps_cagr and eps_cagr > 0 else None
    linser = [
        {"id": "buffett", "namn": "Buffett och Munger", "fraga": "Hög avkastning år efter år, låg skuld och växande vinst per aktie?", "punkter": [
            _punkt("Avkastning på eget kapital över 15 %", f"{roe_ok} av {len(roe_lista)} år", roe_lista and roe_ok >= G["roe_andel_ar"] * len(roe_lista), "Buffett vill se hög avkastning i många år, inte bara ett bra år."),
            _punkt("Vinsten per aktie växer", eps_cagr, None if eps_cagr is None else eps_cagr > 0, "Snittökning per år över perioden.", "% per år"),
            _punkt("Låg skuld", sist["skuld_ggr_resultat"] if sist["nettoskuld"] is None or sist["nettoskuld"] > 0 else "nettokassa", None if sist["nettoskuld"] is None else (sist["nettoskuld"] <= 0 or (sist["skuld_ggr_resultat"] or 9) < 2), "Nettoskulden under 2 gånger rörelseresultatet."),
            _punkt("Inga stora emissioner", utspadning, None if utspadning is None else utspadning <= 5, "Antalet aktier har inte ökat mer än 5 % över perioden.", "%")]},
        {"id": "smith", "namn": "Terry Smith", "fraga": "Hög avkastning på kapitalet, hög marginal och vinst som blir pengar?", "punkter": [
            _punkt("Avkastning på sysselsatt kapital över 20 %", roce_snitt, None if roce_snitt is None else roce_snitt >= G["roce_smith"], "Snitt över perioden.", "%"),
            _punkt("Hög bruttomarginal", brutto, None if brutto is None else brutto >= G["brutto_smith"], "Över ca 40 % tyder på prissättningsmakt. Saknas när bolaget inte redovisar bruttoresultat.", "%"),
            _punkt("Vinsten blir fritt kassaflöde", fcf_konv, None if fcf_konv is None else fcf_konv >= G["fcf_konv_smith"], "Helst över 90 %.", "%"),
            _punkt("Fritt kassaflöde i % av börsvärdet", nu.get("fcf_avkastning"), None, "Jämför med räntan: lägre än räntan betyder att man betalar för framtida tillväxt.", "%")]},
        {"id": "graham", "namn": "Benjamin Graham", "fraga": "Tryggt och billigt, med säkerhetsmarginal?", "punkter": [
            _punkt("Vinst varje år", f"{len(ar)} år", vinst_alla, "Graham ville ha vinst varje år i ca 10 år."),
            _punkt("Utdelning varje år", None, utd_alla if utd_ar else None, "Utdelning utan avbrott."),
            _punkt("P/E under 15 på snittvinsten för tre år", pe_snitt3, None if pe_snitt3 is None else pe_snitt3 < G["graham_pe"], "Snittvinsten jämnar ut ett enskilt bra eller dåligt år."),
            _punkt("P/E × P/B under 22,5", round(nu["pe"] * nu["pb"], 1) if nu.get("pe") and nu.get("pb") else None, None if not (nu.get("pe") and nu.get("pb")) else nu["pe"] * nu["pb"] < G["graham_pe_pb"], "Grahams tumregel för pris mot både vinst och eget kapital."),
            _punkt("Omsättningstillgångar minst dubbla kortfristiga skulder", sist["current_ratio"], None if sist["current_ratio"] is None else sist["current_ratio"] >= G["graham_current"], "Betalningsförmåga på kort sikt.", "gånger")]},
        {"id": "lynch", "namn": "Peter Lynch", "fraga": "Är tillväxten billig?", "punkter": [
            _punkt("PEG-tal (P/E delat med vinsttillväxten)", peg, None if peg is None else peg < G["peg_dyr"], "Under 1 är billigt, över 2 är dyrt. Bygger på historisk tillväxt, inte framtida."),
            _punkt("Försäljningen växer", oms_cagr, None if oms_cagr is None else oms_cagr > 0, "Snitt per år.", "% per år"),
            _punkt("Nettokassa eller låg skuld", sist["nettoskuld"], None if sist["nettoskuld"] is None else sist["nettoskuld"] <= 0 or (sist["skuld_ggr_resultat"] or 9) < 1, "Lynch gillade bolag som inte behöver låna.", arsdata.get("valuta") and f"milj. {arsdata['valuta']}" or "")]},
    ]
    p = piotroski(rader[-1], rader[-2] if len(rader) >= 2 else None)
    utd = {"ar_med_utdelning": sum(1 for a in ar if (a["utdelning_betald"] or 0) > 0), "av_ar": len(ar),
           "utdelningsandel": _pct(rader[-1].get("utdelning_betald"), rader[-1].get("nettoresultat")),
           "direktavkastning": nu.get("direktavkastning"),
           "hojd_ar_i_rad": None}
    serie = [a["utdelning_betald"] for a in ar if a["utdelning_betald"] is not None]
    if serie:
        i = 0
        for x, y in zip(reversed(serie[:-1]), reversed(serie)):
            if y >= x > 0:
                i += 1
            else:
                break
        utd["hojd_ar_i_rad"] = i

    # Temahävstången (metod 22): skrivs för hand i karna.json
    th = (manuell or {}).get("temahavstang")
    if th and th.get("andel_nu_pct") is not None and th.get("tillvaxt_nisch_pct") is not None:
        a0 = th["andel_nu_pct"] / 100
        gn, go = th["tillvaxt_nisch_pct"] / 100, (th.get("tillvaxt_ovrigt_pct") or 0) / 100
        ar_n = th.get("ar") or 5
        nisch, ovr = a0 * (1 + gn) ** ar_n, (1 - a0) * (1 + go) ** ar_n
        th = {**th, "resultat": {"andel_efter_pct": round(nisch / (nisch + ovr) * 100, 1),
                                 "total_tillvaxt_pct": round(((nisch + ovr) ** (1 / ar_n) - 1) * 100, 1),
                                 "utan_nisch_pct": round(go * 100, 1),
                                 "lyft_pp": round((((nisch + ovr) ** (1 / ar_n) - 1) - go) * 100, 1)}}

    return {"ok": True, "valuta": arsdata.get("valuta"), "kalla": arsdata.get("kalla"), "period": f"{forst['ar']}–{sist['ar']}",
            "betyg": betyg, "poang": summa, "poang_max": 2 * len(kanda), "delar": delar,
            "linser": linser, "piotroski": p, "utdelning": utd,
            "nu": nu, "historik": historik, "vardering_lage": vard_sammanfattning,
            "nyckeltal": {"oms_cagr": oms_cagr, "eps_cagr": eps_cagr, "roce_snitt": roce_snitt, "fcf_konv_snitt": fcf_konv, "utspadning_pct": utspadning},
            "temahavstang": th, "ar": ar, "anmarkningar": arsdata.get("anmarkningar") or []}


def main():
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from rot import DATA as ROT
    for a in sys.argv[1:]:
        m = Path(a) if Path(a).is_dir() else ROT / "bolag" / a
        las = lambda n: json.loads((m / n).read_text(encoding="utf-8")) if (m / n).exists() else None
        r = rakna(las("arsdata.json"), las("kurs.json"), las("karna.json"))
        print(json.dumps({k: r.get(k) for k in ("betyg", "poang", "poang_max", "period", "vardering_lage", "nyckeltal", "nu")}, ensure_ascii=False, indent=1))
        for d in r.get("delar", []):
            print(f"  {d['namn']}: {d['poang']} – {d['skal']}")
        for h in r.get("historik", []):
            print(f"  {h['namn']}: nu {h['nu']}, median {h['median']} ({h['lage']})")


if __name__ == "__main__":
    main()
