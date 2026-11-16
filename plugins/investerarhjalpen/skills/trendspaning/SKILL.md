---
name: trendspaning
description: Trendradarn. Pusslar fram djärva hypoteser om vad som kan hända innan det syns i statistiken (möjligheter och sådant som kan spricka, med tidiga tecken och vad som fäller dem), spanar brett i hela världen efter stora skiften (beslutade pengar, fallande kostnader, flaskhalsar, regler, geopolitik, demografi och hälsa, tekniska genombrott), mäter dem över flera år med gratis data, jämför med historiska vinnare och hypefällor, och letar upp bolag i båda spåren, även onoterade och vägar in i dem. Används av söndagsuppgiften första söndagen i månaden, eller när användaren skriver "kör trendspaningen", "vad blir nästa stora trend", "/trendspaning", eller frågar om en framtidsfråga som "kommer elflyg att slå igenom?".
---

# Trendspaning

> **Var saker ligger.** Verktygsmappen (kallas `$IH` nedan) är två nivåer upp från den här skillens mapp: mappen som innehåller `verktyg/`, `metod/`, `larande/` och `mall/`. Datamappen är användarens egen mapp med `installningar.json` (oftast mappen sessionen är öppnad i; annars den mapp som `installningar.json` pekar ut). Metodfiler (`metod/…`), lektioner (`larande/…`) och skript (`verktyg/…`) läses i verktygsmappen; allt annat (`bolag/`, `radar/`, `teman/`, `journal.md`, `min-strategi.md`, `site/` …) i datamappen. Kör skript från datamappen och ersätt `$IH` med den riktiga sökvägen, till exempel `cd "<datamappen>" && python3 -I "$IH/verktyg/nyhetskoll.py"`. Sidans adress står i `installningar.json` (`sida_url`). Saknas `installningar.json`: be användaren köra `/investerarhjalpen:kom-igang` först.

**Läs först `$IH/REGLER.md`** (gemensamma regler: klarspråk, bevisnivåer, inga köp- eller säljråd, integritet), `min-strategi.md` i datamappen och `$IH/metod/21-trendradarn.md`.

Trendradarn följer stora skiften i **hela världen** under lång tid och letar sedan upp bolag, helst svenska och nordiska, som kan rida på vågen. Du samlar bevis och presenterar dem. Användaren tar ställning. Gör aldrig förutsägelser som om de vore säkra, och ge inga köp- eller säljråd.

Det mesta sker **i bakgrunden**: du samlar, sparar och följer upp. Användaren ska bara behöva läsa det som har ändrats.

## Vilket läge?
- **Månadsspaningen** (söndagsuppgiften första söndagen i månaden, eller "kör trendspaningen"): gör steg 1–6.
- **En fråga från användaren** ("kommer elflyg att slå igenom?", "vad händer om Kina inte får fler barn?"): sök, spara det du hittar i banken (steg 2) och gör steg 3–5 för just den frågan. Finns trenden redan: uppdatera den.
- **"Vilka trender följer vi?"**: läs `trender/*.json` och `trender/_bank-sammanfattning.json` och svara kort.

## 1. Mät och läs läget
Kör från datamappen:
- `python3 -I "$IH/verktyg/trendmatare.py"`: mätarna för alla trender.
- `python3 -I "$IH/verktyg/trendbank.py"`: banken. Den listar områden utan observationer, **tidsplaner som har passerat** och **möjliga nya trender** (ämnen som återkommer utan att höra till någon trend).

## 2. Svep brett över alla 16 områden och spara i banken
Gå igenom **alla** områden i `DOMANER` i `trendbank.py`, inte bara de som användaren har nämnt eller som redan har trender. Listan är ett golv, inte ett tak: passar något inte in, spara det under det närmaste området och ge det bra taggar. Cirka 1–2 sökningar per område, högst ca 30 totalt. Börja med områden som har få observationer. Sök på engelska och i hela världen.

Leta efter **det som rör sig men inte står på förstasidorna**, främst:
- **beslut och pengar:** budgetar, program, upphandlingar och storbolagens investeringsplaner (A-nivå)
- **tidsplaner:** någon lovar att något ska hända ett visst år. Spara alltid dem, även när de känns orealistiska.
- **milstolpar, förseningar och bakslag** för tidsplaner som redan finns i banken
- **siffror:** försäljning, användning och kostnader
- **regler med datum**, och **genombrott** i forskning och studier

Skriv observationerna som en JSON-lista i en fil i scratchpad och kör `python3 -I "$IH/verktyg/trendbank.py" --lagg-till <filen>`. Formatet står överst i `trendbank.py`. Viktigt:
- **taggar** på engelska eller svenska, korta och återanvända (till exempel `mars`, `rymdmat`, `drönare`). Det är taggarna som gör att nya trender växer fram.
- **trender**: koppla till befintliga trender (filnamnet) när det passar, annars tom lista.
- **aktor_typ** alltid, så att källfacit kan räknas.
- En uppföljning av en tidsplan har `galler` (tidsplanens id), och `nytt_datum` vid en försening eller `utfall` (`klar` eller `struken`). Id står i utskriften från `trendbank.py` och med `--trend` eller `--tagg`.
- Spara hellre för mycket än för lite. Det som inte verkar viktigt i dag kan bli det om två år.

## 2b. Följ upp tidsplaner som har passerat
För varje rad "Följ upp" i utskriften: sök kort efter vad som hände och spara en uppföljning (försening med nytt datum, klar eller struken). Släpp aldrig en tidsplan bara för att den är sen.

## 2c. Pussla fram djärva hypoteser (det viktigaste steget)
Användarens strategi är att **kliva på tidigt, följa med uppåt och kliva av innan toppen** (metod 21, avsnitt A–C, och spelplanen i `min-strategi.md`). När något syns i statistiken är det ofta redan i priset. Här ska du ta in mycket, lägga pussel om världen och våga gissa, i **vilken bransch som helst**. Lås dig inte vid hård data, och inte vid exempel som användaren har nämnt.

Leta efter **ingredienserna** till något som kan växa kraftigt:
- dit forskare, ingenjörer, nya bolag och riskkapital flyttar
- en kostnad eller teknik som närmar sig en tröskel, ett nytt sätt att utvinna eller använda något
- **stora problem som måste lösas**, särskilt i stora länder som Kina, Indien och USA, eller i hela världen
- regler, budgetar och kriser som öppnar ett fönster
- små bolag som får sina första riktiga kunder
- andra och tredje ledet: om något händer, vem behöver vad sedan?
- tråkiga områden och källor som få läser (läs 2–3 sådana på riktigt varje månad)

**Vikta efter genomslag.** Ge varje hypotes `vikt` med genomslag, tvång, tillväxtutrymme och tidighet, 1–5 var, och en motivering. Ett krav från ett litet land väger lite. En kris i Kina eller Indien som måste lösas väger mycket. **Mogna eller krympande marknader** (tillväxtutrymme 1–2) får bara ett litet öga: spara observationerna i banken, men skriv sällan hypoteser om dem.

Skriv **1–3 nya hypoteser** i månaden som egna filer `trender/<hypotes>.json` med `"status": "hypotes"` och blocken `hypotes`, `vikt` och `cykel` enligt `$IH/mall-trend.json`. Varje hypotes måste ha mekanism, var de flesta kan ha fel, pusselbitar med källor och nivåer, **tidiga tecken**, **vad som fäller den** och **en sannolikhet i procent**. De flesta ska handla om **möjligheter** (det som kan gå upp). En risk (något som kan spricka) tas med när den är tydlig, och ska då också säga vilka bevakade bolag som kan drabbas. Till minst en hypotes per kvartal ska väljas från ett område som inte har haft någon hypotes på ett halvår.

**Varje månad, för befintliga hypoteser och trender:**
- Kontrollera de tidiga tecknen (`sett`, `datum`, `kalla`) och ändra sannolikheten med motivering i `sannolikhet_historik`.
- **Cykeln:** sätt `cykel.fas` (1–5) med motivering och bocka av **euforitecken** som har synts, med datum och källa. Står ett tema i fas 4, eller har minst 3 euforitecken synts: skriv det i notisen och nämn bevakade bolag och bolag i temat, enligt spelplanen i `min-strategi.md`. Inga köp- eller säljråd, bara att tecknen enligt spelplanen har dykt upp.
- När hälften av de tidiga tecknen har synts: byt status till `kandidat` och lägg till mätare. När något i `faller_om` har inträffat, eller tiden har gått ut: sätt `utfall` (`ratt`, `fel` eller `delvis`), `avgjord` och status `avfardad` med lärdomen i `logg`. Radera aldrig en hypotes.

## 3. Nya trender ur banken
Föreslår banken en möjlig ny trend, eller ser du själv ett mönster över flera områden: skapa `trender/<trend>.json` utifrån `$IH/mall-trend.json` om det finns minst en drivkraft på A- eller B-nivå. Det finns ingen gräns för antalet kandidater; de ligger i bakgrunden tills bevisen räcker. Fyll i:
- `fraga`: en fråga som går att besvara med ja eller nej om några år
- `i_en_mening` på klarspråk och `taggar` (samma som i banken)
- `drivkrafter` med typ, text, `niva`, `kalla` och `datum`
- `troskel`: det som måste hända innan trenden kan ta fart, och läget nu
- `matare`: minst en mätare för kunskap eller uppmärksamhet, och **så snart det går en för adoption, kostnad eller pengar** (Our World in Data, OpenAlex, ClinicalTrials.gov eller Wikipedia, se huvudet i `trendmatare.py`). Kontrollera att grafens eller artikelns namn finns. Finns ingen tidsserie: lägg in `"kalla": "manuell"` och skriv värden per år i `serier.<id>.ar`, med källa i `serier.<id>.kalla_text`.
- `konsekvenser`: 2–4 led "om → då", oftast på C-nivå
- `motbevis`: vad som talar emot, och vad som skulle få trenden att stanna
- `status: "kandidat"`, `fas`, `upptackt` och en rad i `logg`

Kör sedan mätaren för trenden: `python3 -I "$IH/verktyg/trendmatare.py" <trend>`.

## 4. Se över trenderna som följs
För varje trend (de äldst granskade först, högst ca 4 per månad):
- Nya beslut, order, siffror eller milstolpar? Lägg till dem i `drivkrafter`, uppdatera `troskel` och skriv en rad i `logg`.
- **Status** enligt tabellen i metod 21, aldrig mer än ett steg per månad, alltid med motivering i `logg`. Avfärdade trender sparas med lärdomen.
- Saknas hårda data (`signal.saknar_hard_data`)? Leta efter en tidsserie för adoption, kostnad eller pengar. Det är den viktigaste förbättringen av en trend.
- Jämför med historiebiblioteket (`signal.liknar` och `trender/historia/`): liknar mönstret en vinnare, en förlorare eller "rätt trend, fel bolag"?
- **Tidsplaner och kapplöpningen:** vilka aktörer tävlar, vem ligger före, och vad säger källfacit om hur ofta den sortens aktör håller sina tidsplaner? Skriv det i `logg` när det ändras.

## 5. Bolagen
För trender med status **följs** eller högre: fyll i eller se över `bolag`, med värdekedjan och flaskhalsen först (metod 06 och 21):
```json
{"namn": "…", "land": "SE", "noterat": true, "spar": "vandning|karna|onoterat", "roll": "flaskhals|tillverkare|leverantor|kund|agare",
 "exponering": "hog|medel|lag", "varfor": "en mening", "vag_in": "för onoterade: noterad ägare eller partner", "niva": "A|B|C|?", "kalla": "…", "slug": "<mapp i bolag/ om det bevakas>"}
```
- Svenska och nordiska bolag först, men ta med de globala ledarna så att jämförelsen finns.
- **Båda spåren:** mindre bolag där trenden kan bli hela affären (Vändning), och större bolag där trenden är tillräckligt stor för att flytta hela bolaget (Kärna).
- **Onoterade bolag** skrivs in med `vag_in`: noterade ägare, noterade partners, planer på notering. Rekommendera aldrig någon väg.
- Ett intressant bolag som inte bevakas: lägg det i `bevakning.md` som kandidat med trendens namn. Användaren väljer om det ska analyseras med `/bolagsanalys`.

## 6. Avsluta
- Bygg sidan (`python3 -I "$IH/verktyg/bygg_sida.py"`) och publicera den till `sida_url` (utelämna `capabilities`).
- I söndagens notis: en rad om nya hypoteser (`Ny hypotes: …, 25 %`), och annars bara om en trend eller hypotes har bytt status eller en viktig tidsplan har ändrats, till exempel `Trender: Drönare stärks (beslutade budgetar i 3 länder).` Annars ingen rad. Antalet sparade observationer behöver inte nämnas.
- Svara kort: ändrad status med motivering, och de 1–3 viktigaste nya bevisen. Nya kandidater och banken nämns i en mening.
