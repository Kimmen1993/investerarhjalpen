---
name: djupdykning
description: Grundlig genomgång av ett bevakat bolag ungefär en gång i månaden. Följer en fast ordning (bolaget, kunder och partners, konkurrenter, bransch, ägare, forum), lägger pusslet, söker motbevis och skriver en kort rapport. Används av söndagsuppgiften, eller när användaren skriver "/djupdykning <bolag>" eller "djupdyk i X".
---

# Djupdykning

> **Var saker ligger.** Verktygsmappen (kallas `$IH` nedan) är två nivåer upp från den här skillens mapp: mappen som innehåller `verktyg/`, `metod/`, `larande/` och `mall/`. Datamappen är användarens egen mapp med `installningar.json` (oftast mappen sessionen är öppnad i; annars den mapp som `installningar.json` pekar ut). Metodfiler (`metod/…`), lektioner (`larande/…`) och skript (`verktyg/…`) läses i verktygsmappen; allt annat (`bolag/`, `radar/`, `teman/`, `journal.md`, `min-strategi.md`, `site/` …) i datamappen. Kör skript från datamappen och ersätt `$IH` med den riktiga sökvägen, till exempel `cd "<datamappen>" && python3 -I "$IH/verktyg/nyhetskoll.py"`. Sidans adress står i `installningar.json` (`sida_url`). Saknas `installningar.json`: be användaren köra `/investerarhjalpen:kom-igang` först.

**Läs först `$IH/REGLER.md`** (gemensamma regler: klarspråk, bevisnivåer, inga köp- eller säljråd, integritet) och `min-strategi.md` i datamappen.

Läs `CLAUDE.md` (även Klarspråk) och `metod/01-pusselmetoden.md`.

## Vilka bolag?
- **Söndagsuppgiften:** kör `python3 -I "$IH/verktyg/djupdykning_tur.py"` i datamappen. Den läser användarens inställningar under `djupdykning` i `installningar.json` (antal per söndag, hur ofta, extra bolag och önskade bolag) och skriver ut vilka bolag som står på tur, det äldsta först. Ta exakt de bolagen. Är inget bolag på tur: avsluta direkt med "Ingen djupdykning i dag", utan notis. När alla är klara: kör `python3 -I "$IH/verktyg/djupdykning_tur.py" --nollstall` (tömmer extra och önskade) och sätt `senaste_djupdykning` till dagens datum i varje genomgånget bolag.
- **Första djupdykningen efter en startanalys** (finns `forsta_djupdykning` men ingen rapport i `djupdykningar/`): gör också punkterna under "Att göra vid första djupdykningen" i `tes.md`, och det startanalysen hoppade över ur `/bolagsanalys` (löftesrevision, kundregister, nätverk, möjligheter och värdering) i den mån budgeten räcker. Skriv vad som återstår. Är inget bolag på tur: avsluta direkt med "Ingen djupdykning i dag", utan notis.
- **Med bolagsnamn** ("djupdyk i Kambi"): djupdyk i just det bolaget direkt, oavsett datum. Sätt sedan `senaste_djupdykning` till i dag, så att bolaget får en ny månad innan det är på tur igen.
- **"Djupdyk i X på söndag"** eller "det händer något i X": lägg bolagets mappnamn i `djupdykning.onskade` i `installningar.json` (rör inget annat) och bekräfta att det tas med nästa söndag.
- **"Kör söndagsgenomgången nu"**, eller med fler bolag ("ta 3 extra"): kör urvalet direkt med `djupdykning_tur.py --extra N` och gör sedan djupdykningarna som vanligt.
- **"Ta N extra på söndag"**: sätt `djupdykning.extra_nasta_sondag` till N.
- **"Ändra till N bolag per söndag"** eller "varannan vecka": ändra `djupdykning.per_sondag` respektive `djupdykning.intervall_dagar` (varannan vecka = 13, en gång i månaden = 27). Förklara kort vad det betyder för tokenförbrukningen: fler bolag och tätare genomgångar använder mer av abonnemanget.


## Budget per bolag
Cirka 20–40 sökningar och hämtningar. Steg 0–2b och 7–9 görs alltid. Steg 2c–6b kortas om budgeten tar slut; skriv i så fall vad som hoppades över.

**Tumregel för vad som är värt att följa:** spåret ska kunna flytta ett viktigt påstående, till exempel en milstolpe eller en stor kund, minst ett steg i bevisnivå. Annars hoppar vi över det (`metod/09-spar-och-signaler.md`).

## Steg
**0. Utgångsläge.** Läs `tes.md`, `status.json`, `loften.md`, `kallor.md`, `handelser.json` och loggen sedan förra djupdykningen. Lista:
- påståenden som är C eller ?
- punkterna i "Vad skulle fälla tesen?"
- löften vars deadline har passerat eller närmar sig
- frågorna från förra djupdykningens rapport (`djupdykningar/`)

Det här är **sökordningens mål**: varje steg nedan ska försöka besvara dem.

**1. Bolaget.** Gå igenom pressmeddelanden sedan förra djupdykningen (`nyheter.json`), IR-sidan (nya presentationer, webbsändningar, intervjuer) och eventuella nya rapporter. Leta efter nya mätbara löften (skriv in dem i `loften.md`), ändrad ton och mål som har slutat nämnas.

**2. Kunder, partners och nätverk.** Gå igenom varje kund och partner i `kallor.md`: deras nyhetsrum, pressmeddelanden och upphandlingar (TED, SAM.gov). Kunden pratar ofta före leverantören.
- **LinkedIn:** följ personerna och bolagssidorna i `bolag/<namn>/natverk.md` enligt reglerna i `metod/08-linkedin-massor-forum.md`: bara yrkesroller, ca 10–15 profiler, inget kontaktande, och läckvarning för icke-offentlig kurspåverkande information.
  - **Söndagsuppgiften får läsa LinkedIn automatiskt bara om `linkedin` är `true` i `installningar.json`**, via Claude in Chrome med användarens inloggning. Annars hoppas LinkedIn över.
    - Läs skillen `anthropic-skills:chrome-browser` och ladda Chrome-verktygen med en enda ToolSearch.
    - Öppna en **ny flik** och rör inte användarens andra flikar.
    - **Bara läsa:** inga klick på Gilla, Kontakta, Följ eller Meddelande, och inga ändringar i kontot.
    - Vänta några sekunder mellan profilerna.
    - Stäng fliken när du är klar.
  - Om Chrome inte är anslutet, du kommer till en inloggningssida, eller LinkedIn visar en spärr eller en CAPTCHA: **avbryt LinkedIn direkt** (lös aldrig en CAPTCHA). Skriv det i rapporten och i notisen.
  - Uppdatera "Senast kollad" i `natverk.md` och fyll i namn som saknas där.
- **Mässor:** har en mässa i `teman/massor.md` för bolagets bransch ägt rum sedan förra djupdykningen? Kontrollera då utställarlistan, panelerna och LinkedIn-inlägg och pressmeddelanden från mässveckan. Mässkopplingar blir högst B.

**2b. Kundregistret, kundernas planer och kundens kunder.** Uppdatera `bolag/<namn>/kundregister.md` (mall: Unibap):
- Har någon kund tagit ett steg (kvalificering → avrop → ramavtal → konstellation)?
- Vilka enheter har levererats, skjutits upp eller tagits i drift?
- Har kunderna själva fått finansiering, nya planer eller större konstellationer?
- Kundens kunder (andra ledet): en snabb koll på de 1–2 största kunderna.

Räkna om konverteringsgraden. Se `metod/09-spar-och-signaler.md`.

**2c. Fysiska spår.** Kontrollera de spår som passar bolagets bransch enligt tabellen i `metod/09-spar-och-signaler.md`, till exempel uppskjutningsmanifest och FCC-ansökningar för rymd, kliniska prövningar för läkemedel, eller tillstånd för industri. Stämmer datum, platser och nyttolaster med det bolaget och kunderna säger?

**2d. Bild och video.** Titta på kundernas nya reklam, renderingar och filmer om produkter där bolagets hårdvara kan finnas. Det som syns blir högst B.

**3. Konkurrenter, liknande bolag och värdering.** Ta 3–5 bolag. Har de vunnit kunder som borde gått till vårt bolag? Har de nya produkter? Hur värderas de?
- **Kursen** uppdateras automatiskt av nyhetskollen (Yahoo Finance) i `kurs.json` och `vardering.json`. Kör `python3 -I "$IH/verktyg/nyhetskoll.py"` först. Uppdatera själv kassa, skuld och försäljning de senaste 12 månaderna i `vardering.json` om en rapport har kommit.
- Uppdatera jämförelsen med nya multiplar.
- Var tredje gång, eller när något stort har hänt: se över scenarierna och sannolikheterna (`metod/11-vardering-scenarier.md`), och leta efter 1–2 bolag som har **gjort en liknande resa**, alltså gått från förlust till vinst. Vilken multipel hade de före och efter?

**4. Bransch och tema.** Läs temafilen i `teman/` om den finns. Leta efter nya budgetbeslut, upphandlingar och regler som påverkar marknaden.

**5. Ägare.** Kontrollera Insynsregistret (finns redan i `nyheter.json`), större ägarförändringar och FI:s blankningsregister.

**6. Forum och sociala medier.** Följ `metod/08-linkedin-massor-forum.md`: rangordningen av källor, de röda och gröna tecknen, och aldrig pumpgrupper på Telegram eller Discord.
- Inlägg med 2 eller fler röda tecken används bara för att se stämningen.
- Nya påståenden skrivs in som **?** att kontrollera.
- Leta särskilt efter kritik och motargument.
- Notera hur mycket bolaget diskuteras: ökar det kraftigt kan informationsövertaget vara på väg att försvinna.
- Uppdatera `forumregister.md` med återkommande skribenter och hur deras gamla påståenden har slagit in.

**6b. Testa marknadens oro** (var tredje djupdykning, alltså ungefär en gång per kvartal, eller när oron ökar tydligt):
- Hitta de 2–3 vanligaste farhågorna om bolaget och kontrollera dem mot fakta.
- Bedöm varje farhåga som befogad, delvis befogad eller obefogad.
- Skriv det i `tes.md` under "Marknadens oro".
- En obefogad oro som många delar är ett möjligt informationsövertag. En befogad oro läggs till i "Vad skulle fälla tesen?".

**6c. Linserna och journalen.**
- **Varje gång:** finns förutsägelser i `journal.md` för bolaget vars slutdatum har passerat, eller som har avgjorts? Fyll i utfallet.
- **Var tredje gång**, tillsammans med 6b: uppdatera "Linsgenomgång" i `tes.md` (de 10 frågorna i `metod/10-tankebanor.md`), skriv nya förutsägelser och fyll i kvartalsgenomgången i journalen.

**6d. Pipelinen (varje gång, viktigast).** Gå igenom `mojligheter.json` affär för affär:
- nya signaler från steg 1–6
- sannolikhet, intäktsspann (enheter × pris) och tidsfönster
- nya möjligheter (minst en signal krävs)
- affärer som blivit signerade flyttas till `signerat`

Se över `okand_framtid` mot signalindexets trend. **Det viktigaste i rapporten är:** vilka signaler höjde eller sänkte vilken affär, och hur stor del av pipelinen räknar marknaden nu med (visas på sidan)? Pekar signalerna på mer än priset räknar med, så är det just det informationsövertag vi letar efter.

**6d2. Efterfrågan (metod 16), var tredje gång eller när politiken eller marknaden ändras:** uppdatera efterfrågekartan i `tes.md` och partnernas volymer. Ny politik (stöd, krav, förbud) eller nya siffror om marknaden är viktiga signaler, även när de inte kommer från bolaget.

**6e. Marknaden och "måste vara sant".** Varje gång: har någon signal bekräftat eller motsagt en punkt under `maste_vara_sant` i `marknadsmodell.json`? Uppdatera sannolikheterna och skriv skälet. Var tredje gång: se över marknadens storlek (nya budgetbeslut och program i temafilen), andelen per region och tratten (nya kundrelationer och konverteringar ur kundregistret).

**6f. Samlad bedömning (metod 14).**
- Varje gång: kontrollera på sidan om linserna är överens.
- En lins som avviker undersöks: varför?
- Var tredje gång: se över vikterna i `metoder` och motivera ändringar.
- När ett historiskt case är gjort eller analytikernas prognoser är hämtade: lägg in dem som lins med `banor` och ge dem vikt.
- Stoppregel: lägg bara tid på en ny lins om den kan ändra resultatet mer än ca 10 %.

**Var tredje gång:** gör ett case i `analoga-case.md` (från listan "Att undersöka") och skriv lärdomen i rapporten.

**7. Lägg pusslet.**
- Koppla ihop bitarna: matchar belopp, datum, personer, platser, uppskjutningar eller kundnamn mellan källor?
- Flytta påståenden mellan nivåerna (C → B → A, eller ner till ✗) och ange varför.
- Formulera nya hypoteser som C, med vad som skulle bekräfta dem.
- Varning för kedjor: flera C-steg i rad är svagt.

**8. Motbevis.** Sök aktivt efter varje punkt i "Vad skulle fälla tesen?". Skriv vad som hittades, även om det var inget.

**8b. Redo-poäng.** Uppdatera `redo` i `status.json`: de 10 punkterna i metod 15, med 0–2 poäng och en mening per punkt. Har bolaget passerat 15 poäng, eller fallit under 10: skriv det i notisen.

**9. Uppdatera och rapportera.**
- `tes.md`: påståenden, nivåer, motbevis och jämförelse
- `status.json`: `trafikljus`, `lage_mening`, `enkelt`, steg, poäng, milstolpar, `nasta_handelse` och `senaste_djupdykning` (dagens datum)
- `handelser.json`: lägg till viktiga fynd som händelser, även om de inte kom från bolaget, till exempel en kunds nyhet
- `logg.md`: en kort post
- `larande/lektioner.json`: rätta siffror i lektionerna om bolagets siffror har ändrats (kassa, kurs, antal aktier)
- **Rapporten:** `bolag/<namn>/djupdykningar/ÅÅÅÅ-MM-DD.md`, enligt mallen nedan, på klarspråk först

```
# Djupdykning <bolag> – <datum>

## Kort och enkelt
3–5 meningar: hur står det till, vad är nytt sedan förra gången, har något ändrats?

## Nya pusselbitar
- <fynd> (källa, datum, bevisnivå)

## Stärker tesen
## Försvagar tesen
## Ändrade bevisnivåer
| Påstående | Från → till | Varför |

## Frågor till nästa djupdykning
- …

## Hoppades över denna gång
- … (t.ex. LinkedIn om Chrome inte var anslutet)
```

## Efteråt
- Kör `python3 -I "$IH/verktyg/bygg_sida.py"` och publicera `site/index.html` till `sida_url` i `installningar.json`.
- Skicka **en** PushNotification under 200 tecken, till exempel: `Djupdykning klar: Unibap grönt, ny kundsignal från Leonardo. Mildef gult, svagare orderingång. Läs på sidan.`
- Ge inga köp- eller säljråd.
