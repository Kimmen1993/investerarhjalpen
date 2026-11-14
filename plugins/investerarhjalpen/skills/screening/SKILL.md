---
name: screening
description: Bolagsjakt: kör signalradarn för hela börsen och gör en kort triage av de mest intressanta nya bolagen (följ, analysera eller ta bort). Används av söndagsuppgiften (högst 5 bolag), eller när användaren skriver "/screening", "hitta nya bolag" eller "vad finns på radarn". Kan få ett tema eller en bransch som argument.
---

# Screening och triage (metod 15)

> **Var saker ligger.** Verktygsmappen (kallas `$IH` nedan) är två nivåer upp från den här skillens mapp: mappen som innehåller `verktyg/`, `metod/`, `larande/` och `mall/`. Datamappen är användarens egen mapp med `installningar.json` (oftast mappen sessionen är öppnad i; annars den mapp som `installningar.json` pekar ut). Metodfiler (`metod/…`), lektioner (`larande/…`) och skript (`verktyg/…`) läses i verktygsmappen; allt annat (`bolag/`, `radar/`, `teman/`, `journal.md`, `min-strategi.md`, `site/` …) i datamappen. Kör skript från datamappen och ersätt `$IH` med den riktiga sökvägen, till exempel `cd "<datamappen>" && python3 -I "$IH/verktyg/nyhetskoll.py"`. Sidans adress står i `installningar.json` (`sida_url`). Saknas `installningar.json`: be användaren köra `/investerarhjalpen:kom-igang` först.

**Läs först `$IH/REGLER.md`** (gemensamma regler: klarspråk, bevisnivåer, inga köp- eller säljråd, integritet) och `min-strategi.md` i datamappen.

1. Läs `metod/15-bolagsjakt.md`, `metod/02-turnaround-och-tenbagger.md` och `metod/04-varningsflaggor.md`.
2. Kör `python3 -I "$IH/verktyg/signalradar.py"` och läs `radar/radar.json`.
3. Välj **högst 5** bolag som inte är triagerade, med högst poäng. Prioritera bolag som har **flera olika typer** av positiva signaler, till exempel både order och insiderköp, eller fondköp tillsammans med en annan signal. Fondköp ensamt betyder att proffsen redan har hittat bolaget: titta då extra på om priset redan räknar med det. Vilka fonder som köpt står i `radar/fondsignaler-borsen.json`, och fonder som är kända för att leta småbolag tidigt (till exempel mikrobolagsfonder) väger tyngre än breda Sverigefonder. Har användaren angett ett tema: välj bolag som passar temat.
4. **Triage, ca 10 minuter per bolag** (bara några få sökningar):
   - storlek (börsvärde) och lista
   - vad bolaget säljer och till vem, i en mening
   - kassa och om pengarna räcker
   - de senaste 3–4 pressmeddelandena
   - röda flaggor: emissioner, units, vinstvarningar
   - koppling till ett tema i `teman/`
5. Bestäm:
   - **Analysera:** värt en full `/bolagsanalys`. Säg det till användaren i svaret och notisen.
   - **Radar:** intressant men tidigt. Följ passivt och låt signalerna samlas.
   - **Bort:** fel storlek, en röd flagga eller ointressant affär. Lägg till namnet i `radar/uteslutna.json` om bolaget aldrig ska komma tillbaka (till exempel ett storbolag); annars bara i triagen.
6. Skriv i `radar/triage.json` under `bolag.<nyckel>` (nyckeln står i `radar.json`): `{"beslut": "Analysera|Radar|Bort", "datum": "...", "kommentar": "en mening", "borsvarde_msek": ..., "tema": "..."}`.
7. Bygg och publicera sidan. Svara kort i en tabell: bolag, beslut, varför. Ge inga köp- eller säljråd.

**Ungefär en gång per kvartal:** gå igenom bolagen märkta Radar. Har signalerna blivit fler? Är något värt att uppgradera till Analysera? Gå också igenom `kastade.md`: hade vi rätt att kasta dem?
