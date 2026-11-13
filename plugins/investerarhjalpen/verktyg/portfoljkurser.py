#!/usr/bin/env python3
"""Portföljkurser – gratis, ingen AI.

Läser en nedladdad kopia av användarens privata portfölj (JSON från sidans databas),
räknar ut vilka värdepapper som ägs, hämtar senaste kurs från Yahoo Finance
(ISIN → symbol, cachas i privat/yahoo-symboler.json) och skriver en
uppdateringsfil {"kurser": {...}} som Claude sedan skriver tillbaka privat
med ArtifactData. Inget av detta byggs in i den publicerade sidan.

Kör:  python3 -I "$IH/verktyg/portfoljkurser.py" <portfolj.json> <utfil.json>
"""
import json
import sys
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rot import VERKTYG, DATA as ROT  # noqa: E402  (ROT = användarens datamapp)
CACHE = ROT / "privat" / "yahoo-symboler.json"
UA = {"User-Agent": "Mozilla/5.0"}


def hamta(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20) as r:
        return json.loads(r.read())


def symbol_for(isin, namn, cache):
    if isin in cache:
        return cache[isin]
    sym = None
    for q in (isin, namn):
        try:
            res = hamta("https://query1.finance.yahoo.com/v1/finance/search?" + urllib.parse.urlencode({"q": q, "quotesCount": 8, "newsCount": 0}))
        except Exception:
            continue
        quotes = [x for x in res.get("quotes", []) if x.get("symbol")]
        st = [x["symbol"] for x in quotes if x["symbol"].endswith(".ST")]
        if st or quotes:
            sym = (st or [quotes[0]["symbol"]])[0]
            break
    cache[isin] = sym
    return sym


def senaste(sym):
    """Senaste stängningskurs ur dagsserien (regularMarketPrice kan vara gammal för små listor)."""
    r = hamta(f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(sym)}?range=5d&interval=1d")["chart"]["result"][0]
    m = r["meta"]; ts = r.get("timestamp") or []; cl = (r.get("indicators", {}).get("quote") or [{}])[0].get("close") or []
    par = [(t, c) for t, c in zip(ts, cl) if c is not None]
    pris, tid = (par[-1][1], par[-1][0]) if par else (m.get("regularMarketPrice"), m.get("regularMarketTime"))
    if m.get("regularMarketTime") and par and m["regularMarketTime"] > par[-1][0] and m.get("regularMarketPrice") is not None:
        pris, tid = m["regularMarketPrice"], m["regularMarketTime"]
    return pris, (m.get("currency") or "SEK"), (date.fromtimestamp(tid).isoformat() if tid else None)


def kurs_sek(sym, fx):
    pris, valuta, tid = senaste(sym)
    if pris is None:
        return None, None
    if valuta.upper() != "SEK":
        if valuta not in fx:
            fx[valuta] = senaste(f"{valuta.upper()}SEK=X")[0]
        pris = pris * fx[valuta]
    return round(pris, 4), tid


def main():
    doc = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    antal, namn = defaultdict(float), {}
    for t in doc.get("transaktioner", []):
        i = t.get("isin")
        if not i or t["typ"] == "utdelning":
            continue
        a = t.get("antal") or 0
        antal[i] += a if t["typ"] in ("köp", "händelse") else -a if t["typ"] == "sälj" else 0
        if t.get("namn") and not t["namn"].upper().startswith(("ÖVERFÖRING", "OTILLÅTET")):
            namn.setdefault(i, t["namn"])
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    fx, kurser, saknas = {}, {}, []
    for i, a in antal.items():
        if a <= 1e-6 or (doc.get("dolda") or {}).get(i):
            continue
        sym = symbol_for(i, namn.get(i, ""), cache)
        try:
            pris, tid = kurs_sek(sym, fx) if sym else (None, None)
        except Exception:
            pris, tid = None, None
        gammal = (doc.get("kurser") or {}).get(i) or {}
        if gammal.get("kurs") is not None and not str(gammal.get("kalla", "")).startswith("Yahoo") and pris is not None and str(gammal.get("datum", "")) >= str(tid):
            continue  # bankens egen kurs från samma dag är exaktare än Yahoo
        if pris is None:
            saknas.append(namn.get(i, i))
            kurser[i] = {"ingen_kurs": True, "datum": date.today().isoformat(), "kalla": "Yahoo hittar ingen handel"}
            continue
        kurser[i] = {"kurs": pris, "datum": tid, "kalla": f"Yahoo ({sym})"}
    CACHE.parent.mkdir(exist_ok=True)
    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
    Path(sys.argv[2]).write_text(json.dumps({"kurser": kurser}, ensure_ascii=False), encoding="utf-8")
    for i, k in kurser.items():
        if k.get("ingen_kurs"):
            continue
        print(f"{namn.get(i, i)[:28]:28} {k['kurs']:>10} kr  {k['datum']}  {k['kalla']}")
    if saknas:
        print("Ingen kurs:", ", ".join(saknas))


if __name__ == "__main__":
    main()
