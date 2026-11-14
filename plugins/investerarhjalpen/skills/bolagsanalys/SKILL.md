---
name: bolagsanalys
description: Bygg ett nytt investeringscase för ett bolag från grunden: löftesrevision av 2–3 års kommunikation, pussel från många källor (bolaget, kunder/partners, LinkedIn, forum), koppling till omvärld och tema, bevisnivåer (A/B/C/?) och motbevis. Använd när användaren vill analysera ett nytt bolag eller klistrar in en text/tes om ett bolag som saknar mapp under bolag/.
---

# Bolagsanalys

> **Var saker ligger.** Verktygsmappen (kallas `$IH` nedan) är två nivåer upp från den här skillens mapp: mappen som innehåller `verktyg/`, `metod/`, `larande/` och `mall/`. Datamappen är användarens egen mapp med `installningar.json` (oftast mappen sessionen är öppnad i; annars den mapp som `installningar.json` pekar ut). Metodfiler (`metod/…`), lektioner (`larande/…`) och skript (`verktyg/…`) läses i verktygsmappen; allt annat (`bolag/`, `radar/`, `teman/`, `journal.md`, `min-strategi.md`, `site/` …) i datamappen. Kör skript från datamappen och ersätt `$IH` med den riktiga sökvägen, till exempel `cd "<datamappen>" && python3 -I "$IH/verktyg/nyhetskoll.py"`. Sidans adress står i `installningar.json` (`sida_url`). Saknas `installningar.json`: be användaren köra `/investerarhjalpen:kom-igang` först.

**Läs först `$IH/REGLER.md`** (gemensamma regler: klarspråk, bevisnivåer, inga köp- eller säljråd, integritet) och `min-strategi.md` i datamappen.

Argument: bolagsnamn, eventuellt inklistrad text eller tes. Arbeta i den här ordningen. Bolagets historik kommer först och berättelsen sist.

## 1. Förberedelse
- Läs `CLAUDE.md` och alla filer i `metod/`.
- Finns en inklistrad text: dela upp den i påståenden och märk alla som **?**.

## 2. Grunddata (A-nivå, med källa)
- börsvärde och antal aktier
- omsättning, resultat och kassaflöde för de senaste 8–12 kvartalen
- kassa och burn rate
- orderingång eller orderstock
- alla emissioner de senaste 3 åren, med belopp, kurs och utspädning
- större ägare och insynsaffärer de senaste 12 månaderna

Gör en kort sammanfattning **år för år**: vad gick bra, vad gick dåligt och vad förändrades.

## 3. Löftesrevision
Kör hela flödet i `.claude/skills/loftesrevision/SKILL.md` och skriv `loften.md`. Resultatet avgör hur mycket bolagets egna prognoser får väga i resten av analysen.

## 4. Pusslet: många källor
- **Kunder och partners** som nämns i pressmeddelanden och rapporter: vad säger *de* om samarbetet, om volymerna och om framtida planer?
- **LinkedIn** (via Claude in Chrome om användaren är inloggad, enbart läsning): ledningens och nyckelpersoners inlägg, kundernas inlägg och rekryteringar.
- **Forum:** leta efter tips att följa upp och, framför allt, efter **kritik och motbevis**. Allt härifrån är **?** tills det har kontrollerats.
- **Upphandlingar, myndigheter och branschmedia.**
- Koppla ihop bitarna. Varje slutsats får en bevisnivå. Skriv tydligt när flera C-steg följer på varandra.

## 5. Omvärld och tema
- Vilket eller vilka teman är bolaget exponerat mot? Läs eller skapa `teman/<tema>.md` (se `/tema`).
- I vilken fas är temat? Har bolaget **egen** leverans, eller rider det bara på temat?

## 6. Bygg caset
Gör stegen i den här ordningen:
1. **Skriv motbevislistan först.**
2. Ge varje påstående en bevisnivå.
3. Poängsätt turnaround-checklistan.
4. Kontrollera de röda flaggorna.

Skapa sedan `bolag/<namn>/tes.md`, `kallor.md`, `logg.md` och `loften.md` med samma upplägg som `bolag/unibap/`. `tes.md` ska ha avsnitten "Löftesrevision" och "Omvärld/tema". Lägg till bolaget i `bevakning.md`.

## 6b. Linsgenomgång och journal
- Besvara de 10 frågorna i `metod/10-tankebanor.md` under "Linsgenomgång" i `tes.md`. Var särskilt noga med fråga 2 (vad priset redan räknar med), 3 (pre-mortem) och 6 (redovisningens kvalitet: rörelseresultat jämfört med kassaflöde).
- Skriv 3–5 förutsägelser med slutdatum och sannolikhet i `journal.md`.

## 7. Turnaround-steg och jämförelse
- Bestäm steg 1–5 med belägg, milstolpar kvar och bedömd tid. Justera tiden med löftesrevisionens precision. Se `metod/07-beslut-turnaround-jamforelse.md`.
- Jämför med 3–5 liknande bolag i en tabell i `tes.md`, avsnittet "Jämförelse". Besvara frågan: vad betalar marknaden för liknande bolag som redan nått nästa steg?

## 6b2. Efterfrågan (metod 16)
Besvara de sju frågorna: marknadens riktning, vad som driver köpet, om det lönar sig för köparen, politiken land för land, partnernas volymer (räkneexempel kalibrerat mot kända ordrar), antal länder och kundgrupper, och vad som talar emot. Fyll i efterfrågekartan i `tes.md` och gör gemene man-testet. Partnervolymerna förs in i `mojligheter.json`.

## 6c. Marknaden uppifrån (huvudbedömningen)
Följ `metod/13-marknad-uppifran.md`:
- temafil med marknadens storlek i fysiska enheter, regioner, tillgång och konkurrenter
- `marknadsmodell.json` med kalibrering mot dagens försäljning, andel per region och scenario, tratt, framåtmultipel och "måste vara sant"

Det här är **huvudbedömningen** av vart bolaget kan gå. Pipelinen (7a) är kontrollen nerifrån.

## 7a. Pipelinen (före värderingen)
Skapa `mojligheter.json` enligt `metod/12-pipeline-och-framtid.md` (mall: `bolag/unibap/mojligheter.json`):
- löpande affär
- signerat (bara det bindande)
- varje möjlig affär med signaler, intäktsspann (enheter × pris), år, sannolikhet och om den är inprisad
- `okand_framtid`

Värderingen räknas sedan på pipelinen. Fråga alltid: **hur stor del av pipelinen räknar marknaden redan med?**

## 7b. Värdering i scenarier
Följ `metod/11-vardering-scenarier.md` och skapa `vardering.json` (mall: `bolag/unibap/vardering.json`):
- aktuell kurs, med datum och källa
- omvänd värdering
- tre scenarier med egen multipel, nettokassa, antal aktier (inklusive utspädning) och sannolikhet
- jämförelse med direkta konkurrenter och med bolag som gjort en liknande resa

Det är räkneexempel, inte riktkurser.

## 8. Beslut och publicering
- Välj **Bevaka**, **Avvakta** eller **Kasta** enligt kriterierna i metod 07.
  - **Kasta:** lägg en rad i `kastade.md`, skapa en kort `status.json` med `"beslut": "Kasta"` och en kort `tes.md`. Ingen full akt behövs.
  - **Bevaka eller Avvakta:** fyll i `status.json` med alla fält (mall: `bolag/unibap/status.json`), **inklusive `enkelt`-blocket på klarspråk** (se CLAUDE.md, avsnittet Klarspråk), samt lägg till nya facktermer i `metod/ordlista.md`, inklusive `kallor_bevakning` (MFN-slug från mfn.se/all/a/<slug> och utgivarnamn i FI:s insynsregister), och `ir_sida` (bolagets sida för investerare, länkad från hemsidan). Kör sedan `python3 -I "$IH/verktyg/rapportlankar.py"` så att rapporternas PDF:er syns på sidan.
  - Sätt även `trafikljus`, `lage_mening` och `senaste_djupdykning` (dagens datum).
  - **Spår och Lynchkategori** (metod 18): föreslå `spar` (`vandning` eller `karna`), `lynch` och `lynch_skal`, och sätt `"spar_bekraftad": false`. Säg i svaret vilket spår som föreslås och varför, och be användaren bekräfta. För Kärna: hoppa över turnaround-steget och redo-poängen, och lägg i stället vikt vid kvalitet (avkastning på kapitalet, marginaler, kassaflöde) och värdering mot bolagets egen historik.
  - **Investerarpanelen:** skriv `panel.json` enligt skillen `panel` (metod 18).
  - Skapa `nyckeltal.json` med minst de senaste 8 kvartalen ur rapporterna (mall: `bolag/unibap/nyckeltal.json`).
  - Skapa `kundregister.md`: alla kända kunder som en tidslinje genom bolagets säljmodell, plus konverteringsgraden (mall: `bolag/unibap/kundregister.md`, metod 09).
  - Skapa `natverk.md` med upp till 10 yrkesroller hos bolaget och kunderna (mall: `bolag/unibap/natverk.md`).
  - Skapa `handelser.json` med de 5–8 viktigaste händelserna det senaste halvåret, på klarspråk (mall: `bolag/unibap/handelser.json`). De viktigaste får `lardom` och `lektion` (se CLAUDE.md, Lärande).
- Kör `python3 -I "$IH/verktyg/nyhetskoll.py"`. Första körningen sparar historiken.
- Kör `python3 -I "$IH/verktyg/bygg_sida.py"` och publicera `site/index.html` (URL i CLAUDE.md).

## 9. Svar till användaren
Lägg till beslutet och motiveringen först i svaret.
Svara kort i chatten med:
- tesen i en mening
- måtten från löftesrevisionen
- de 3 starkaste A-påståendena
- de 3 viktigaste osäkerheterna
- temat och dess fas
- checklistepoäng
- röda flaggor
- vad som ska bevakas

Förklara facktermer för en nybörjare. Ge inga köp- eller säljråd.

Om materialet är stort, till exempel många PDF:er: säg vad som är läst och vad som återstår, och fortsätt i nästa omgång.
