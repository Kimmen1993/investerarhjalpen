---
name: fond
description: Fondverktyget. Följ, sluta följa, sök och jämför svenska fonder med Finansinspektionens kvartalsdata (innehav, avgift, risk, aktiv risk, köpt och sålt, överlapp), och se vilka fonder som äger ett bevakat bolag. Används när användaren skriver "följ fonden X", "sök fonder", "jämför fonderna X och Y", "vilka fonder äger X?", "/fond" eller frågar om en fond.
---

# Fonder

> **Var saker ligger.** Verktygsmappen (kallas `$IH` nedan) är två nivåer upp från den här skillens mapp: mappen som innehåller `verktyg/`, `metod/`, `larande/` och `mall/`. Datamappen är användarens egen mapp med `installningar.json`. Kör skript från datamappen. Sidans adress står i `installningar.json` (`sida_url`).

**Läs först `$IH/REGLER.md`.** Ge aldrig köp- eller säljråd om fonder, och rekommendera ingen fond. Visa fakta: avgift, vad fonden äger, risk och överlapp.

## Datan
- Källa: Finansinspektionens kvartalsfiler med alla **svenskregistrerade** värdepappersfonders innehav, förvaltningsavgift per andelsklass, jämförelseindex, aktiv risk och standardavvikelse. Fonder som är registrerade i Luxemburg eller Irland finns inte med. Se avsnittet Utländska fonder.
- FI publicerar med några månaders fördröjning. Säg alltid vilket kvartal siffrorna gäller.
- `python3 -I "$IH/verktyg/fonder.py"` är gratis och utan AI. Den hämtar ett nytt kvartal när det finns (ca 6 MB) och skriver `fonder/<fond>/fond.json`, `fonder/fondsignaler.json` och `bolag/<namn>/fondagare.json`.

## Kommandon
- **Sök:** `python3 -I "$IH/verktyg/fonder.py" --sok "<del av namn>"`. Visa de bästa träffarna med avgift, storlek och typ.
- **Följ:** `python3 -I "$IH/verktyg/fonder.py" --lagg-till <ISIN> [<ISIN> …]`. Skriv sedan en mening på klarspråk i `fond.json` under `"enkelt": {"i_en_mening": "…"}` utifrån innehaven (vad fonden köper, hur många bolag, land, index eller aktiv). Bygg och publicera sidan.
- **Sluta följa:** `--ta-bort <ISIN>`. Ta sedan bort mappen `fonder/<fond>/` först efter att ha sagt vilken mapp det är.
- **Vilka fonder äger X?** Läs `bolag/<namn>/fondagare.json`. Finns bolaget inte bland de bevakade: sök i senaste kvartalsfilen med ett kort Python-skript (läs zipfilen i `fonder/_fi/` direkt) på bolagets ISIN.
- **Kolla mina fonder:** se Fondkoll ovan.
- **Jämför fonder:** ställ dem bredvid varandra: avgift, vad avgiften kostar på 10 år, typ, risk, aktiv risk, de 10 största innehaven, länder, branscher och överlapp (`overlapp` i `fond.json`).

## Utländska fonder (finns inte i FI:s data)
Många fonder hos Avanza är registrerade i Luxemburg eller Irland, bland annat de flesta ETF:er. Följ dem så här, i den här ordningen:

1. **Grunddata.** Ta reda på ISIN, fullständigt namn, fondbolag, index (för indexfonder) och årlig avgift från faktabladet eller fondbolagets sida. Högst ca 3 sökningar.
2. **Fondbolagets innehavsfil (bäst).** Leta efter en direkt länk till en Excel- (xlsx) eller CSV-fil med alla innehav på fondbolagets produktsida (ofta "Holdings", "Portfolio", "Download holdings" eller "Innehav"). Testa länken med `curl -sSL -o /dev/null -w "%{http_code} %{content_type}\n" "<url>"`: den ska ge en fil, inte `text/html`. Exempel som fungerar: Xtrackers `https://etf.dws.com/etfdata/export/GBR/ENG/excel/product/constituent/<ISIN>/` och SPDR `https://www.ssga.com/library-content/products/fund-data/etfs/emea/holdings-daily-emea-en-<ticker>-gy.xlsx`. Kör sedan:
   `python3 -I "$IH/verktyg/fonder.py" --utlandsk <ISIN> --namn "<namn>" --fondbolag "<bolag>" --index "<index>" --avgift <procent> --kalla "<url>"`
   Filen hämtas sedan automatiskt ungefär en gång i månaden, gratis.
3. **Ingen fil, men en indexfond:** lägg till `--ersattning auto`. Då lånas innehaven från en svensk indexfond med liknande index (MSCI World och ACWI, USA och S&P 500, Europa, Norden, Sverige, globala småbolag). Sidan visar tydligt att det är en uppskattning. Finns ingen liknande svensk fond (till exempel tillväxtmarknader eller Japan): gå vidare till steg 4.
4. **Aktiv fond utan fil:** läs fondbolagets senaste månadsrapport eller faktablad (PDF; spara den i en ny mapp i scratchpad och läs den med `swift "$IH/verktyg/pdftext.swift"`). Skriv `fonder/<fond>/innehav-manuellt.json`:
   ```json
   {"datum": "ÅÅÅÅ-MM-DD", "kalla": "<url till rapporten>",
    "innehav": [{"namn": "Microsoft", "isin": "US5949181045", "andel": 7.1, "land": "US", "sektor": "IT"}],
    "sektorer": {"IT": 31.0, "Finans": 14.2}, "lander": {"US": 62.0, "JP": 6.1}}
   ```
   och kör `--utlandsk <ISIN> --namn "<namn>" …` utan `--kalla`. ISIN kan saknas; skriptet kopplar ihop bolagen via namnet. Uppdatera filen ungefär en gång i kvartalet (söndagsgenomgången).
5. Skriv en mening på klarspråk i `fond.json` (`enkelt.i_en_mening`), bygg och publicera sidan. Säg till användaren vilken källa som används.

"Hämta innehaven för X" betyder att göra steg 2–4 för en fond som visar "Innehav saknas".

## Fondkoll (användarens egna fonder)
Sidan gör kollen själv i webbläsaren under Min portfölj och Fonder: överlapp mellan fonder som användaren äger (över 50 %), bolag som användaren äger via flera fonder och direkt (tillsammans över 10 % av portföljen), och fonder som inte följs eller saknas i FI:s data. Det syns bara för den inloggade användaren.

För notisen (vid nytt kvartal i morgonkollen, eller när användaren skriver "kolla mina fonder"):
1. Läs portföljen med ArtifactData från `sida_url` (collection `data/users/me`, dokument `portfolj`). Spara den som JSON i scratchpad. Går det inte att läsa: hoppa över och säg det kort.
2. Kör `python3 -I "$IH/verktyg/fonder.py" --kontroll <filen>`. Utskriften listar fonderna användaren äger, `foljs_inte_isin`, `utanfor_fi` och `overlapp`.
3. Fonder i `foljs_inte_isin`: lägg till dem med `--lagg-till` och skriv en mening i `fond.json`, så att de kan kontrolleras. Fonder i `utanfor_fi`: följ dem enligt avsnittet Utländska fonder. Skriv aldrig på sidan att användaren äger dem.
4. Notis: en rad per överlapp ("X och Y äger till 76 % samma sak") och om nya fonder började följas. Inga råd om att sälja eller byta, bara fakta så att användaren kan ta ställning.
5. Bygg och publicera sidan om något ändrades.

## Så förklarar du (användarna är nybörjare på fonder)
- **Avgiften är den enda säkra siffran.** Räkna gärna ut vad den kostar på 100 000 kr över 10 år.
- **Indexfond eller aktiv:** aktiv risk under ca 1 % betyder att fonden följer sitt index. En aktiv fond med låg aktiv risk och hög avgift kan i praktiken vara en dyr indexfond.
- **Risk:** standardavvikelsen visar hur mycket fonden har svängt per år de senaste två åren.
- **Överlapp:** över ca 50 % betyder att två fonder gör ungefär samma jobb.
- **Köpt och sålt:** in- och utflöden är borträknade (medianförändringen av antalet aktier). För indexfonder beror ändringar oftast på att indexet ändrats.
- **Avgift hos Avanza:** samma förvaltningsavgift som hos fondbolaget, men den kan skilja mellan andelsklasser. Andelsklassen syns på ISIN-numret där man köper.

## Senare (inte byggt än)
Förväntad avkastning i scenarier (byggklossmetoden), fondpanel och koppling till temasidan.
