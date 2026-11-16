---
name: bolagsanalys
description: Bygg ett nytt investeringscase för ett bolag från grunden: löftesrevision av 2–3 års kommunikation, pussel från många källor (bolaget, kunder/partners, LinkedIn, forum), koppling till omvärld och tema, bevisnivåer (A/B/C/?) och motbevis. Föreslår spår (Vändning eller Kärna) och tar fram investerarpanelen, pelarna, jämförelsen och kalendern. Använd när användaren skriver "analysera X", "/bolagsanalys X", vill analysera ett nytt bolag eller klistrar in en text eller tes om ett bolag som saknar mapp under bolag/.
---

# Bolagsanalys

> **Var saker ligger.** Verktygsmappen (kallas `$IH` nedan) är två nivåer upp från den här skillens mapp: mappen som innehåller `verktyg/`, `metod/`, `larande/` och `mall/`. Datamappen är användarens egen mapp med `installningar.json` (oftast mappen sessionen är öppnad i; annars den mapp som `installningar.json` pekar ut). Metodfiler (`metod/…`), lektioner (`larande/…`) och skript (`verktyg/…`) läses i verktygsmappen; allt annat (`bolag/`, `radar/`, `teman/`, `journal.md`, `min-strategi.md`, `site/` …) i datamappen. Kör skript från datamappen och ersätt `$IH` med den riktiga sökvägen, till exempel `cd "<datamappen>" && python3 -I "$IH/verktyg/nyhetskoll.py"`. Sidans adress står i `installningar.json` (`sida_url`). Saknas `installningar.json`: be användaren köra `/investerarhjalpen:kom-igang` först.

**Läs först `$IH/REGLER.md`** (gemensamma regler: klarspråk, bevisnivåer, inga köp- eller säljråd, integritet) och `min-strategi.md` i datamappen.

Argument: bolagsnamn, eventuellt inklistrad text eller tes. Arbeta i den här ordningen. Bolagets historik kommer först och berättelsen sist.

**Mallar:** tomma mallar för alla filer finns i `$IH/mall-bolag/` (se `LASMIG.md` där). Har användaren redan ett väl ifyllt bolag i `bolag/` får du också titta på det som exempel.

**Stort material?** En full analys kräver många sökningar och PDF:er. Hinner du inte allt: gör en **startanalys** (steg 1–6, 11 och 12) och skriv det som återstår under "Att göra vid första djupdykningen" i `tes.md` och `"forsta_djupdykning": "<i dag>"` i `status.json`. Söndagens djupdykning tar resten. Säg vad som är gjort och vad som återstår.

## 1. Förberedelse
- Läs `$IH/metod/01-pusselmetoden.md`, `02-turnaround-och-tenbagger.md`, `04-varningsflaggor.md`, `05-loftesrevision.md`, `07-beslut-turnaround-jamforelse.md` och `18-spar-och-investerarpanelen.md`. De övriga metoderna läser du när steget nedan hänvisar till dem.
- Finns en inklistrad text: dela upp den i påståenden och märk alla som **?**.
- Skapa mappen `bolag/<namn>/` (gemener, utan å/ä/ö och mellanslag, till exempel `bolag/unibap/`).

## 2. Grunddata (A-nivå, med källa)
- börsvärde och antal aktier
- omsättning, resultat och kassaflöde för de senaste 8–12 kvartalen
- kassa och burn rate
- orderingång eller orderstock
- alla emissioner de senaste 3 åren, med belopp, kurs och utspädning
- större ägare och insynsaffärer de senaste 12 månaderna

Gör en kort sammanfattning **år för år**: vad gick bra, vad gick dåligt och vad förändrades.

## 3. Löftesrevision
Följ skillen `loftesrevision` och skriv `loften.md`. Resultatet avgör hur mycket bolagets egna prognoser får väga i resten av analysen.

## 4. Pusslet: många källor
- **Kunder och partners** som nämns i pressmeddelanden och rapporter: vad säger *de* om samarbetet, om volymerna och om framtida planer?
- **LinkedIn** (via Claude in Chrome om användaren är inloggad, enbart läsning, regler i metod 08): ledningens och nyckelpersoners inlägg, kundernas inlägg och rekryteringar.
- **Forum:** leta efter tips att följa upp och, framför allt, efter **kritik och motbevis**. Allt härifrån är **?** tills det har kontrollerats.
- **Upphandlingar, myndigheter och branschmedia.**
- Koppla ihop bitarna. Varje slutsats får en bevisnivå. Skriv tydligt när flera C-steg följer på varandra.

## 5. Omvärld, tema och efterfrågan
- Vilket eller vilka teman är bolaget exponerat mot? Läs eller skapa `teman/<tema>.md` (skillen `tema`).
- I vilken fas är temat? Har bolaget **egen** leverans, eller rider det bara på temat?
- **Efterfrågan (metod 16):** besvara de sju frågorna: marknadens riktning, vad som driver köpet, om det lönar sig för köparen, politiken land för land, partnernas volymer (räkneexempel kalibrerat mot kända ordrar), antal länder och kundgrupper, och vad som talar emot. Fyll i efterfrågekartan i `tes.md` och gör gemene man-testet.

## 6. Bygg caset
Gör stegen i den här ordningen:
1. **Skriv motbevislistan först** ("Vad skulle fälla tesen?").
2. Ge varje påstående en bevisnivå.
3. Kontrollera de röda flaggorna (metod 04).
4. **Spår och Lynchkategori (metod 18):** föreslå `spar` (`vandning` eller `karna`), `lynch` och `lynch_skal`, med `"spar_bekraftad": false`.
   - **Vändning:** poängsätt turnaround-checklistan (metod 02), bestäm steg 1–5 med belägg, milstolpar kvar och bedömd tid (justerad med löftesrevisionens precision, metod 07), och sätt redo-poängen (metod 15).
   - **Kärna:** hoppa över turnaround-steget och redo-poängen. Lägg i stället vikt vid kvalitet (avkastning på kapitalet, marginaler, kassaflöde) och värdering mot bolagets egen historik.

Skapa `tes.md`, `kallor.md`, `logg.md` och `loften.md` (mallar i `$IH/mall-bolag/`). `tes.md` ska ha avsnitten "Löftesrevision", "Omvärld/tema" och "Vad skulle fälla tesen?". Lägg till bolaget i `bevakning.md`.

## 7. Linsgenomgång och journal
- Besvara de 10 frågorna i `metod/10-tankebanor.md` under "Linsgenomgång" i `tes.md`. Var särskilt noga med fråga 2 (vad priset redan räknar med), 3 (pre-mortem) och 6 (redovisningens kvalitet: rörelseresultat jämfört med kassaflöde).
- Skriv 3–5 förutsägelser med slutdatum och sannolikhet i `journal.md`.

## 8. Marknaden uppifrån (huvudbedömningen)
Följ `metod/13-marknad-uppifran.md`:
- temafil med marknadens storlek i fysiska enheter, regioner, tillgång och konkurrenter
- `marknadsmodell.json` med kalibrering mot dagens försäljning, andel per region och scenario, tratt, framåtmultipel och "måste vara sant"

Det här är **huvudbedömningen** av vart bolaget kan gå. Pipelinen (steg 9) är kontrollen nerifrån.

## 9. Pipelinen (före värderingen)
Skapa `mojligheter.json` enligt `metod/12-pipeline-och-framtid.md`:
- löpande affär
- signerat (bara det bindande)
- varje möjlig affär med signaler, intäktsspann (enheter × pris), år, sannolikhet och om den är inprisad; partnervolymerna från steg 5 förs in här
- `okand_framtid`

Fråga alltid: **hur stor del av pipelinen räknar marknaden redan med?**

## 10. Värdering och jämförelse
- Följ `metod/11-vardering-scenarier.md` och skapa `vardering.json`: aktuell kurs med datum och källa, omvänd värdering, tre scenarier med egen multipel, nettokassa, antal aktier (inklusive utspädning) och sannolikhet. Det är räkneexempel, inte riktkurser.
- **Jämförelse (metod 20):** 3–5 liknande bolag i `jamforelse` i `status.json`, gärna ett som redan har nått nästa steg. Besvara frågan: vad betalar marknaden för liknande bolag som har kommit längre? Siffror som inte gick att kontrollera blir `null` med `niva: "?"`.

## 11. Beslut och filerna
Välj **Bevaka**, **Avvakta** eller **Kasta** enligt kriterierna i metod 07.
- **Kasta:** lägg en rad i `kastade.md`, skapa en kort `status.json` med `"beslut": "Kasta"` och en kort `tes.md`. Ingen full akt behövs.
- **Bevaka eller Avvakta:** fyll i `status.json` med alla fält i mallen, bland annat:
  - `enkelt`-blocket på klarspråk (REGLER.md, avsnittet Klarspråk), `trafikljus`, `lage_mening` och `senaste_djupdykning` (i dag)
  - `kallor_bevakning`: `mfn_slug` (från mfn.se/all/a/<slug>), `fi_utgivare` (utgivarnamnet i FI:s insynsregister) och `yahoo` (kurssymbolen, till exempel `UNIBAP.ST`); `ir_sida` och `isin`
  - spåret från steg 6 och `kalender` med kommande rapporter, stämmor och andra viktiga datum (format i skillen `dagskoll`, avsnitt 4c)
  - `pelare` och `overtygelse` (metod 20)
- Skapa också:
  - `nyckeltal.json` med minst de senaste 8 kvartalen ur rapporterna
  - `kundregister.md`: alla kända kunder som en tidslinje genom bolagets säljmodell, plus konverteringsgraden (metod 09)
  - `natverk.md` med upp till 10 yrkesroller hos bolaget och kunderna
  - `handelser.json` med de 5–8 viktigaste händelserna det senaste halvåret, på klarspråk. De viktigaste får `lardom` och `lektion` (REGLER.md, avsnittet Lärande).
  - `panel.json` enligt skillen `panel`
- Lägg till nya facktermer i `$IH/metod/ordlista.md` bara om du arbetar i verktygets egen mapp; annars förklara dem direkt i texten.

## 12. Publicera
- Kör `python3 -I "$IH/verktyg/nyhetskoll.py"` (första körningen sparar historiken) och `python3 -I "$IH/verktyg/rapportlankar.py"` (rapporternas PDF:er).
- Kör `python3 -I "$IH/verktyg/bygg_sida.py"` och publicera `site/index.html` till `sida_url` i `installningar.json` (utelämna `capabilities`).

## 13. Svar till användaren
Börja med beslutet och motiveringen. Svara sedan kort med:
- tesen i en mening
- föreslaget spår och varför, och be användaren bekräfta (`ja till spåret för <bolag>`)
- måtten från löftesrevisionen
- de 3 starkaste A-påståendena
- de 3 viktigaste osäkerheterna
- temat och dess fas
- checklistepoäng (Vändning) eller kvalitetsbilden (Kärna)
- röda flaggor
- vad som ska bevakas, och vad som återstår till första djupdykningen

Förklara facktermer för en nybörjare. Ge inga köp- eller säljråd.
