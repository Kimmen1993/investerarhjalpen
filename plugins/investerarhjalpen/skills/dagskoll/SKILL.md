---
name: dagskoll
description: Morgonkollen av alla bevakade bolag inför börsdagen. Kör den gratis nyhetskollen, sammanfattar nya pressmeddelanden och insynsaffärer på klarspråk, gör en rapportgenomgång när en rapport har kommit och påminner om rapporter samma dag. Bygger och publicerar webbsidan och skickar en notis. Används av den schemalagda uppgiften varje vardag kl. 08.30, eller när användaren skriver "/dagskoll" eller "kör dagskollen".
---

# Dagskoll

> **Var saker ligger.** Verktygsmappen (kallas `$IH` nedan) är två nivåer upp från den här skillens mapp: mappen som innehåller `verktyg/`, `metod/`, `larande/` och `mall/`. Datamappen är användarens egen mapp med `installningar.json` (oftast mappen sessionen är öppnad i; annars den mapp som `installningar.json` pekar ut). Metodfiler (`metod/…`), lektioner (`larande/…`) och skript (`verktyg/…`) läses i verktygsmappen; allt annat (`bolag/`, `radar/`, `teman/`, `journal.md`, `min-strategi.md`, `site/` …) i datamappen. Kör skript från datamappen och ersätt `$IH` med den riktiga sökvägen, till exempel `cd "<datamappen>" && python3 -I "$IH/verktyg/nyhetskoll.py"`. Sidans adress står i `installningar.json` (`sida_url`). Saknas `installningar.json`: be användaren köra `/investerarhjalpen:kom-igang` först.

**Läs först `$IH/REGLER.md`** (gemensamma regler: klarspråk, bevisnivåer, inga köp- eller säljråd, integritet) och `min-strategi.md` i datamappen.

Läs `CLAUDE.md` först, framför allt avsnittet Klarspråk. **Var sparsam:** finns inget nytt ska du stanna så tidigt som möjligt.

## 1. Hämta nytt (gratis)
Kör `python3 -I "$IH/verktyg/nyhetskoll.py"` och `python3 -I "$IH/verktyg/signalradar.py"` (radarn för hela börsen; inget mer görs med den här, triagen sker på söndagen). Kör också `python3 -I "$IH/verktyg/fonder.py"` (gratis; den hämtar bara något när Finansinspektionen har publicerat ett nytt kvartal). Börjar utskriften med **NYTT KVARTAL**: bygg om sidan och nämn i notisen vilka bevakade bolag som fått flest nya fondägare eller tappat flest (`fonder/fondsignaler.json`). Radarn läser fondsignalerna för hela börsen automatiskt, så kör `signalradar.py` igen efter `fonder.py` den dagen. Gör också **fondkollen** (se skillen `fond`, avsnittet Fondkoll) och skriv varningarna i notisen. Läs `nyhetskoll-senaste.json`. Har ett bolag som inte triagerats fått **7 poäng eller mer** på radarn: nämn det på en rad i notisen.
- Kontrollera också `nasta_handelse` i varje `status.json`: står det dagens datum (till exempel en rapport i dag)?
- **Har verktyget uppdaterats?** Kör `python3 -I "$IH/verktyg/behover_ombyggnad.py"`. Svarar den `ja`: bygg sidan (`python3 -I "$IH/verktyg/bygg_sida.py"`) och publicera den till `sida_url` (utelämna `capabilities`), även om inget annat är nytt, så att nya funktioner och rättningar syns. Ingen notis behövs för det.
- Har inget bolag `nya > 0` och inget har en händelse i dag: **avsluta här** utan notis (och utan publicering, om inte verktyget uppdaterades). Svara bara "Inget nytt i dag."
- Har inget bolag `nya > 0` men något har en händelse i dag: skicka bara en påminnelse, till exempel `I dag: Unibap släpper kvartalsrapport. Dagskollen i morgon sammanfattar den.`, och avsluta.

Rapporter publiceras ofta kl. 07–08. Har en rapport väntats i dag men inte kommit än: nämn det i notisen.

## 2. Sammanfatta varje nytt pressmeddelande
För varje bolag med nya poster, gå igenom posterna i `bolag/<namn>/nyheter.json` som har `"ny": true` och vars länk inte redan finns i `handelser.json`.
- **Pressmeddelande:** läs det via länken (WebFetch, bara själva PM:et). Lägg till en händelse överst i `bolag/<namn>/handelser.json`:
  - `datum`
  - `rubrik`: max 6 ord, på svenska
  - `enkelt`: 1–3 korta meningar om vad som hänt och varför det spelar roll. Belopp i kronor.
  - `paverkan`: `starker`, `forsvagar`, `neutral` eller `blandat`, bedömt mot tesen i `tes.md`
  - `viktig`: true för rapport, order eller avtal över ca 1 % av årsomsättningen, emission, ledningsbyte, vinstvarning eller insiderförsäljning
  - `lank`
  - `lardom` (för `viktig: true`): en mening om vad användaren kan lära sig av händelsen, till exempel hur man läser siffran eller varför den spelar roll. Peka gärna på en lektion med `lektion` (id i `larande/lektioner.json`: arsredovisning, kassaflode, marginal, kassa, utspadning, order, vardering, vdord, insyn, noter, efterfragan, psykologi).
- **Insynsaffärer:** slå ihop samma person och dag till en händelse. Köp av aktier räknas som `starker`, försäljning av aktier som `forsvagar` och `viktig`. Tilldelning av optioner är `neutral`.
- Rutin-PM som valberedning eller kallelse: en kort händelse, `neutral`, `viktig: false`.

## 2b. Pipelinen
Rör en ny händelse en möjlig affär i `bolag/<namn>/mojligheter.json`?
- Lägg till signalen (datum, signal, källa, bevisnivå).
- Justera `sannolikhet` enligt tabellen i `metod/12-pipeline-och-framtid.md`, och skriv skälet i `logg.md`.
- Har affären blivit signerad? Flytta den till `signerat` (bara det som är bindande) och ta bort den som möjlighet.
- Är det en helt ny möjlighet med minst en signal? Lägg till den.

Sidan räknar om prognosen automatiskt när den byggs.

## 3. Rapport? Gör en rapportgenomgång
Har det kommit en kvartalsrapport, ett bokslut eller en årsredovisning:
1. Hämta PDF:en. Länken finns i pressmeddelandet eller på bolagets rapportsida. Spara den i en ny mapp i scratchpad och läs den med `swift "$IH/verktyg/pdftext.swift"`, eller `swift "$IH/verktyg/ocr.swift"` om den är inskannad.
2. Lägg till kvartalet i `nyckeltal.json`: omsättning, rörelseresultat, orderingång, kassa, kassaflöde från den löpande verksamheten, kassaflöde från investeringar och antal aktier i miljoner. Har bolaget rättat äldre siffror: rätta dem också.
3. Följ upp öppna löften i `loften.md` och lägg till nya mätbara löften från vd-ordet.
4. Uppdatera `tes.md` (siffror och "Vad skulle fälla tesen?") och `logg.md`.

## 4. Uppdatera läget
För varje bolag som hade något nytt, uppdatera i `status.json`:
- `lage_mening`: en mening på klarspråk om hur tesen står sig just nu
- `trafikljus`:
  - `gron`: tesen håller
  - `gul`: något viktigt försvagar eller är oklart, till exempel en missad milstolpe, en svag rapport eller en mindre insiderförsäljning
  - `rod`: en punkt på "Vad skulle fälla tesen?" har inträffat, till exempel en emission med stor rabatt, en förlorad nyckelkund, en vinstvarning eller en stor insiderförsäljning
- `enkelt`-blocket om något har ändrats
- `nasta_handelse` och `senast_uppdaterad`
- `beslut`: om trafikljuset blir rött, föreslå i notisen att användaren tar ställning. Ändra inte beslutet själv.

## 4b. Journalen
Avgör en ny händelse en förutsägelse i `journal.md`, till exempel en ny order eller en emission? Fyll i utfallet och nämn det i notisen.

## 5. Djupdykning ingår inte här
Djupdykningar görs av söndagsuppgiften (`.claude/skills/djupdykning/SKILL.md`). Dagskollen ska vara snabb.

## 6. Publicera
Kör `python3 -I "$IH/verktyg/bygg_sida.py"` och publicera `site/index.html` med Artifact-verktyget med `url` = `sida_url` i `installningar.json`. Läs artifacten först om verktyget kräver det.

## 6b. Kursen
Nyhetskollen hämtar kursen automatiskt (`kurs` i `nyhetskoll-senaste.json`). Har ett bolag rört sig **mer än 5 % sedan föregående dag** utan något nytt pressmeddelande: nämn det i notisen och leta snabbt efter en förklaring, till exempel en nyhetsartikel, en sektorrörelse eller blankning. Kursrörelser utan nyheter kan vara en tidig signal.

## 7. Notis (användaren vill ha notis om allt nytt)
Skicka **en** PushNotification per körning, under 200 tecken och utan markdown. Exempel:
`Unibap: ny order från Leonardo ca 30 mkr (stärker). Mildef: kvartalsrapport, förlust minskar (blandat). Mer på sidan.`
Är det fler än tre händelser: skriv de viktigaste och "+N till".

## 8. Svar
Kort lista per bolag: vad som är nytt (en rad var), trafikljuset och om något kräver användarens beslut. Ge inga köp- eller säljråd.
