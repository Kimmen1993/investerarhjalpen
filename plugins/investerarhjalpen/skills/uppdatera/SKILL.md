---
name: uppdatera
description: Uppdatera bolagscase. Med bolagsnamn uppdateras det bolaget. Utan argument körs veckouppföljningen, där den gratis nyhetskollen väljer ut vilka bolag som behöver analyseras. Använd när användaren säger "uppdatera mig om X", "vad är nytt", "uppdatera bevakningslistan" eller "/uppdatera".
---

# Uppdatera

> **Var saker ligger.** Verktygsmappen (kallas `$IH` nedan) är två nivåer upp från den här skillens mapp: mappen som innehåller `verktyg/`, `metod/`, `larande/` och `mall/`. Datamappen är användarens egen mapp med `installningar.json` (oftast mappen sessionen är öppnad i; annars den mapp som `installningar.json` pekar ut). Metodfiler (`metod/…`), lektioner (`larande/…`) och skript (`verktyg/…`) läses i verktygsmappen; allt annat (`bolag/`, `radar/`, `teman/`, `journal.md`, `min-strategi.md`, `site/` …) i datamappen. Kör skript från datamappen och ersätt `$IH` med den riktiga sökvägen, till exempel `cd "<datamappen>" && python3 -I "$IH/verktyg/nyhetskoll.py"`. Sidans adress står i `installningar.json` (`sida_url`). Saknas `installningar.json`: be användaren köra `/investerarhjalpen:kom-igang` först.

**Läs först `$IH/REGLER.md`** (gemensamma regler: klarspråk, bevisnivåer, inga köp- eller säljråd, integritet) och `min-strategi.md` i datamappen.

## Utan argument (veckouppföljning, sparsam)
1. Kör `python3 -I "$IH/verktyg/nyhetskoll.py"` och läs `nyhetskoll-senaste.json`.
2. Gör en full uppdatering (nedan) **bara** för bolag med `behover_analys: true`.
   - Bolag med nya, mindre viktiga PM: skriv en rad i `logg.md`, utan webbsökning.
   - Bolag utan nyheter: rör dem inte.
3. Kontrollera `nasta_handelse` i varje `status.json`. Har datumet passerat utan att något hänt? Gör då en full uppdatering av det bolaget.
4. Bygg sidan (`python3 -I "$IH/verktyg/bygg_sida.py"`) och publicera `site/index.html` till `sida_url` i `installningar.json` (utelämna `capabilities`).
5. Svara med en kort lista per bolag: nytt / inget nytt / behöver beslut.

## Med bolagsnamn (full uppdatering)
1. Läs `bolag/<namn>/tes.md`, `kallor.md`, `status.json`, `nyheter.json` och den senaste posten i `logg.md`.
2. Läs de nya posterna i `nyheter.json`, som redan har länkar. Kompletterande sökningar:
   - kunder, partners och media enligt `kallor.md`
   - LinkedIn bara vid behov
   - när en rapport har kommit: läs PDF:en med `swift "$IH/verktyg/pdftext.swift"` (eller `ocr.swift` om den är inskannad), lägg till kvartalet i `nyckeltal.json` och följ upp löftena i `loften.md`. Är det en årsredovisning för ett kärnbolag: kör `python3 -I "$IH/verktyg/arsdata.py" <bolagsmapp>` (metod 22)
3. Gå igenom alla påståenden som är C eller ?, och listan "Vad skulle fälla tesen?".
4. Uppdatera:
   - `tes.md` och `kallor.md`
   - `logg.md` med en ny post överst
   - `handelser.json`: rapporten som händelse med `lardom` (vad användaren kan lära sig av just den här rapporten) och `lektion` (id i `larande/lektioner.json`)
   - `status.json`: steg, poäng, milstolpar, nästa händelse, `senast_uppdaterad` och **`enkelt`-blocket** (REGLER.md, avsnittet Klarspråk), `trafikljus`, `lage_mening`, `pelare` (metod 20) och nya datum i `kalender`
   - beslutet, om det har ändrats (till exempel Bevaka → Kasta), med motivering
5. Bygg och publicera sidan.
6. Svara kort:
   - **Nytt** (med datum och källa)
   - **Stärker tesen**
   - **Försvagar tesen**
   - **Ändrat beslut eller steg**
   - **Nästa att bevaka**
   
   Ge inga köp- eller säljråd.
