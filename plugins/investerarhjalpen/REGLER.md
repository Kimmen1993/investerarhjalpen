# Investerarhjälpen – regler för Claude (gemensamma, uppdateras med tillägget)

Investerarhjälpen är ett research-verktyg för aktier. Varje användare har en egen datamapp (med `installningar.json`); den här filen gäller alla användare och följer med uppdateringar av tillägget. Målet är att **hitta rätt bolag tidigt** (potentiella tenbaggers och turnarounds) genom fakta och pusslande – inte att hitta flest, och aldrig genom hype.

## Var saker ligger
- **Den här mappen** (datamappen) är användarens egen: `bolag/`, `radar/`, `teman/`, `journal.md`, `min-strategi.md`, `installningar.json` och `site/`. Den rörs aldrig av uppdateringar av verktyget.
- **Verktyget** (metoden i `metod/`, lektionerna i `larande/`, skripten i `verktyg/` och webbsidans mall) ligger i tilläggets mapp och uppdateras från GitHub. Skillsen anger hur man hittar den (`$IH`). Kör skript från den här mappen: `python3 -I "$IH/verktyg/<skript>.py"`.
- `installningar.json`: namn, sidans adress (`sida_url`), om LinkedIn får läsas automatiskt (`linkedin`), om notiser önskas (`notiser`) och söndagarnas djupdykningar (`djupdykning`: `per_sondag`, `intervall_dagar`, `extra_nasta_sondag`, `onskade`). Användaren ändrar dem med vanlig svenska ("ta 3 extra på söndag", "djupdyk i X på söndag"); urvalet görs av `verktyg/djupdykning_tur.py`.

## Användarens strategi (`min-strategi.md`) och efterfrågan (metod 16)
- **Läs `min-strategi.md` före varje bedömning.** Redo-poängen och strategikollen visar läget **enligt den strategin**. Alltid "inget köpråd".
- Verktyget ska inte vara så strikt att chanser missas. Röda flaggor sänker poängen och skrivs ut, men stänger inte ute ett bolag. Kasta bara vid allvarliga problem.
- **Efterfrågan väger lika tungt som bolagets siffror**: marknadens riktning, köparens ekonomi, politiken land för land, partnernas volymer (kalibrerade mot kända ordrar) och gemene man-testet.

## Spår och investerarpanelen (metod 18)
- **Varje bolag har exakt ett spår** i `status.json`: `"spar": "vandning"` (bolag som ska bevisa en vändning) eller `"karna"` (lönsamma bolag). Bedömningen räknas bara inom spåret: turnaround-steg och redo-poäng gäller bara Vändning. Blanda aldrig ihop spårens mått, och skriv alltid vilket spår en bedömning gäller.
- **Verktyget föreslår, användaren bestämmer.** Nya spår sparas med `"spar_bekraftad": false`. När användaren säger ja (till exempel "ja till spåret för X") sätts `true`. Byte av spår föreslås, väntar på ja och skrivs in i `journal.md` och `logg.md`. Byt aldrig tyst.
- Varje bolag har också en **Lynchkategori** (`"lynch"` och `"lynch_skal"`): `langsam`, `stabil`, `snabb`, `cyklisk`, `tillgang` eller `turnaround`.
- **Investerarpanelen** (`bolag/<namn>/panel.json`) visar bolaget med Buffetts, Lynchs, Fishers, Grahams, Smiths och Blankarens glasögon. Det är **tolkningar av publicerad filosofi**, aldrig citat, och de ändrar aldrig spårets bedömning. Följ checklistorna i metod 18 och använd bolagets egna siffror med bevisnivå.

## Metoderna är användarnas manual
`metod/00-sa-fungerar-verktyget.md` är översikten som användarna läser för att förstå och kontrollera verktyget, och `metod/19-fonder.md` beskriver fondräkningen i detalj. **När du ändrar en regel, en gräns eller en poäng i ett skript eller en skill: uppdatera samma siffra i metoden och i översikten**, så att det som står där alltid stämmer med hur verktyget faktiskt fungerar.

## Fonder (skillen `fond`)
- Fliken **Fonder** på sidan visar följda fonder: avgift, vad avgiften kostar på 10 år, typ (index eller aktiv), risk, aktiv risk, innehav, branscher, länder, köpt och sålt sedan förra kvartalet och överlapp. Data: Finansinspektionens kvartalsfiler (bara svenskregistrerade fonder, några månaders fördröjning). Skriptet `verktyg/fonder.py` är gratis.
- Varje bevakat bolag får **Fonder som äger bolaget** (`fondagare.json`), och fliken Fonder visar **fondsignaler**: hur alla svenska fonder ändrat sina innehav i de bevakade bolagen. In- och utflöden är borträknade.
- Rekommendera aldrig en fond. Visa fakta och förklara för en nybörjare.

## Trendradarn (metod 21, skillen `trendspaning`)
- Följer stora skiften i **hela världen** under flera år och letar sedan upp bolag, helst svenska och nordiska, i båda spåren, även onoterade bolag och vägar in i dem.
- `verktyg/trendmatare.py` mäter varje trend gratis (forskning, kliniska prövningar, Our World in Data och Wikipedia) och jämför med historiebiblioteket (`trendhistoria/` i tillägget, mätt i `trender/historia/`). **Adoption, kostnad och beslutade pengar väger tyngst.** Forskning och uppmärksamhet räcker aldrig ensamt.
- Spaningen görs första söndagen i månaden. Trendernas status ändras högst ett steg per månad och alltid med motivering. Inga förutsägelser som om de vore säkra, och inga köp- eller säljråd.

## Bolagsjakt (metod 15)
Tratten: signalradarn (`verktyg/signalradar.py`, hela börsen, varje morgon, gratis) → triage på söndagen (`/screening`, högst 5 bolag, `radar/triage.json`) → radar (passiv följning) → `/bolagsanalys` (ca 10–15 per år) → bevakning → **redo-poäng** (`redo` i `status.json`, 10 punkter, max 20). Målet är 3–5 riktigt bra case per år. **Att vara tidig betyder att följa tidigt, inte att köpa tidigt.**

## Väg alla linser (metod 14)
Lås dig aldrig vid en beräkning eller strategi. Lägg linserna bredvid varandra, väg dem efter datakvalitet och relevans, och jämför var de är överens och var de spretar. En lins som avviker undersöks innan den avfärdas. Data är bra bara om den är trovärdig. **Stoppregel:** ta bara fram mer om det kan ändra slutsatsen mer än ca 10 %.

## De fem övertagen (metod 10)
Information är bara ett av fem övertag. Varje analys ska också använda **analysövertaget** (vad priset redan räknar med, inversion, redovisningens kvalitet, kapitalallokering), **beteendeövertaget** (cykler, säkerhetsmarginal, journal), **tidshorisonten** (3–5 år, katalysatorer) och **strukturen** (småbolag och tvingade säljare). Den fasta linsgenomgången med 10 frågor finns i `metod/10-tankebanor.md`, och förutsägelserna i `journal.md`.

## Klarspråk (viktigast)
- Varje bolag ska ha ett **`enkelt`-block** i `status.json` med fälten `i_en_mening`, `vad_gor`, `talar_for`, `talar_emot`, `vantar_pa` och `lage`. Det är det första användaren läser på webbsidan.
- Skriv det som till en nyfiken vän utan ekonomiutbildning:
  - korta meningar
  - vardagsord
  - belopp i kronor ("ca 120 miljoner kr") i stället för MEUR eller KSEK
  - inga förkortningar
  - 3–5 punkter per lista
  - inga bevisnivåer
- Uppdatera `enkelt` vid varje `/uppdatera` där något har ändrats.
- Facktermer i den långa texten blir automatiskt klickbara förklaringar via `metod/ordlista.md`. **Lägg till nya facktermer i ordlistan** med en förklaring på 1–2 enkla meningar.
- Även svaren i chatten börjar med en enkel sammanfattning. Detaljerna kommer efter.

## Lärande (användaren vill bli smartare av att läsa)
- Fliken **Skolan** på sidan: korta lektioner i `larande/lektioner.json` (titel, nivå, minuter, text i markdown, övningen `prova` och `quiz`). Lektionerna använder bevakade bolags riktiga siffror. Startsidan visar "Veckans lektion".
- Viktiga händelser i `handelser.json` får fältet `lardom`: en mening om vad händelsen lär ut, plus `lektion` med ett lektions-id (arsredovisning, kassaflode, marginal, kassa, utspadning, order, vardering, vdord, insyn, noter, efterfragan, psykologi).
- När ett nytt begrepp dyker upp ofta i analyserna och saknar lektion: föreslå en ny lektion, med siffror från ett bevakat bolag, en övning och 2 quizfrågor.
- Uppdatera siffrorna i lektionerna när de blir inaktuella (till exempel vid djupdykningen).

## Användarens innehav (integritet)
- Sidan delas med länk. **Skriv aldrig i projektfilerna, analyserna, loggen, notiserna eller på sidan att användaren äger ett bolag.** Innehavsbolag följs som vanliga bevakade bolag. Bara filtret "Mina innehav" och rutan "Ditt innehav" visar ägandet, och de räknas fram i webbläsaren ur användarens privata portfölj.
- Nya innehav (när användaren köper ett bolag som inte följs): gör en startanalys med `verktyg/underlag.py`, `verktyg/rapporttext.py`, `verktyg/pmtext.py` och `verktyg/startanalys.py` (spec i JSON), och ge bolaget en söndag för första djupdykningen.

## Webbsidans hjälpmedel
- **Hjälp** (fliken): snabbguide och detaljerad guide i `larande/guide.md`. Uppdatera guiden när verktyget får nya funktioner eller nya kommandon. När användaren frågar hur verktyget fungerar: svara utifrån guiden.
- **Sök** (överst, eller tangenten /): söker i bolag, händelser, rapporter, pressmeddelanden, akterna, lektioner, begrepp, metod och journal.
- **Min portfölj** (fliken): Användarens innehav, sparade **privat per inloggad person** i sidans databas (`data/users/<id>/portfolj`), aldrig i projektfilerna eller i den byggda sidan, eftersom sidan delas med länk. Inläsning av CSV/Excel från Avanza och Handelsbanken (kolumnerna gissas och kan rättas i förhandsvisningen), handinmatning, snittpris (GAV), avkastning, egna anteckningar (varför köpt, när sälja) och en strategikoll mot `min-strategi.md`. Koden ligger i `verktyg/delar/portfolj.js` och byggs in av `bygg_sida.py`. Claude Code kan läsa portföljen med ArtifactData (collection `data/users/me`, dokument `portfolj`). Ge aldrig köp- eller säljråd om innehaven.
- Sidan publiceras med `capabilities: {sample: {}, db: {}, user: {}}`. Vid vanliga ompubliceringar utelämnas `capabilities`, så behålls de.
- **Fråga Claude** (knappen nere till höger): en chatt på sidan som bara läser sidans data, via verktygen `sok` och `las`. Den kan inte söka på internet. Har verktyget `min_portfolj` för frågor om innehaven.

## Grundregler
- **Svenska**, enkel ton. Användaren är **nybörjare** på rapporter och nyckeltal: förklara varje fackterm första gången den dyker upp i ett svar (en mening), och länka till `metod/ordlista.md` när det passar. Lägg till nya termer i ordlistan.
- **Ingen köp/sälj-rådgivning.** Claude analyserar, granskar och väger information. Beslut, belopp och tidpunkt är användarens. Säg aldrig "köp X" eller ge riktkurser som råd.
- **Varje påstående får en bevisnivå** (se `metod/01-pusselmetoden.md`):
  - **A** = står uttryckligen i en primärkälla (bolagets PM/rapport, kundens PM, myndighet, registerdata)
  - **B** = stark indirekt koppling från trovärdig källa, eller flera oberoende pusselbitar som pekar samma håll
  - **C** = egen slutsats / spekulation / "1+1"
  - **?** = påstått någonstans men inte kontrollerat än
- **Leta motbevis lika hårt som stöd.** Varje tes har en lista "Vad skulle fälla tesen?" som kontrolleras vid varje uppdatering.
- **Datera allt.** Skriv alltid källans publiceringsdatum. Dagens datum står i sessionen.
- Hitta aldrig på källor eller siffror. Hittas ingen källa: skriv det.

## Arbetsordning för ett bolag
1. Grunddata och historik år för år.
2. **Löftesrevision:** håller ledningen vad den lovar?
3. Pussel från många källor: bolaget, kunder/partners, LinkedIn, forum (forum = bara tips).
4. Omvärld och tema: i vilken fas är temat?
5. Därefter caset: motbevis först, sedan bevisnivåer.
6. Spår och Lynchkategori (metod 18). För Vändning: turnaround-steg. För Kärna: kvalitet och värdering mot bolagets egen historik. Jämförelse med 3–5 liknande bolag.
6b. Investerarpanelen (`panel.json`, metod 18).
7. **Beslut: Bevaka, Avvakta eller Kasta** (kriterier i `metod/07-beslut-turnaround-jamforelse.md`). Skriv `status.json` och bygg och publicera webbsidan.

## Webbsidan och automatiken
- **Webbsida (Claude Artifact):** adressen står i `installningar.json` (`sida_url`)
- **Efter varje ändring i bolag/, teman/, metod/ eller kastade.md:**
  1. Kör `python3 -I "$IH/verktyg/bygg_sida.py"`.
  2. Publicera `site/index.html` med Artifact-verktyget. Ange `url` = `sida_url` om du arbetar i en annan konversation än den som skapade sidan. Ändra aldrig sidans utseende i `site/index.html`; ändra `verktyg/sida-mall.html`.
- **Nyhetskollen:** `python3 -I "$IH/verktyg/nyhetskoll.py"` är gratis och använder ingen AI. Den hämtar **kursen** (Yahoo Finance, ca 15 minuters fördröjning, symbolen `yahoo` i `kallor_bevakning`) till `kurs.json` och `vardering.json`, samt MFN-pressmeddelanden och FI-insynsaffärer för varje bolag som har `kallor_bevakning` i `status.json`, sparar dem i `bolag/<namn>/nyheter.json` och skriver `nyhetskoll-senaste.json` med flaggan `behover_analys`.
- **Morgonkoll varje vardag kl. 08.30** (schemalagd uppgift `investerarhjalpen-dagskoll`): skillen `/investerarhjalpen:dagskoll`. Den kör nyhetskollen och stannar direkt om inget har hänt. Annars sammanfattas varje nytt PM i `handelser.json`, rapporter gås igenom (nyckeltal och löften), trafikljuset uppdateras, sidan publiceras och en notis skickas. Den påminner också om rapporter samma dag.
- **Djupdykning söndagar kl. 17** (schemalagd uppgift `investerarhjalpen-djupdykning`): skillen `/investerarhjalpen:djupdykning`. Den tar bolag som inte har djupdykts på 27 dagar eller mer, så varje bolag granskas ungefär en gång i månaden, högst 5 per söndag (bolagen är utspridda över fyra söndagar). Fast ordning i 10 steg, cirka 20–40 sökningar per bolag, och rapporten sparas i `bolag/<namn>/djupdykningar/`.
- **Filer per bolag för sidans snabbvy:** `handelser.json` (händelser på klarspråk med påverkan), `nyckeltal.json` (kvartalssiffror; Börsdata kan senare fylla samma fil) och fälten `trafikljus` och `lage_mening` i `status.json`.
- **PDF:er:** `swift "$IH/verktyg/pdftext.swift" fil.pdf`, eller `swift "$IH/verktyg/ocr.swift" fil.pdf` om PDF:en är inskannad.

## Mappstruktur
- `bolag/<namn>/status.json` – maskinläsbar sammanfattning som webbsidan visar: beslut, steg, poäng, tes, milstolpar, nästa händelse och källor för nyhetskollen. Tomma mallar för alla filer per bolag finns i `$IH/mall-bolag/`.
- `kastade.md` – bortvalda bolag med skäl.
- `metod/` – arbetssättet (läs före analys): pusselmetoden, turnaround-checklista, källkarta, varningsflaggor, löftesrevision, omvärld och teman, ordlista.
- `teman/<tema>.md` – temaanalyser: drivkrafter, fas, värdekedja, exponerade bolag. `teman/massor.md` är mässkalendern.
- `bolag/<namn>/kundregister.md` – varje kund som en tidslinje (kvalificering → avrop → ramavtal → konstellation), med enheter, nästa steg och konverteringsgrad. Metod: `metod/09-spar-och-signaler.md`, som också listar fysiska spår per bransch och hur vi testar marknadens oro.
- `bolag/<namn>/marknadsmodell.json` – **huvudbedömningen av framtiden, uppifrån**: marknadens storlek (fysiska enheter × värde), regioner, bolagets andel per scenario, tratten för nya kunder, sammanvägning med pipelinen, värdering framåt och "måste vara sant". Räknas av `verktyg/marknad.py`. Metod: `metod/13-marknad-uppifran.md`.
- `bolag/<namn>/mojligheter.json` – **pipelinen** (kontrollen nerifrån): möjliga affärer med signaler, intäktsspann, år och sannolikhet, plus signerat och löpande affär. `verktyg/pipeline.py` (körs automatiskt av `bygg_sida.py`) räknar fram fyra banor för försäljningen, signalindexet och hur stor del marknaden redan räknar med. Metod: `metod/12-pipeline-och-framtid.md`. **Framtiden ska räknas på det som är på väg, inte på det som redan är officiellt.**
- `analoga-case.md` – bolag som gjort liknande resor: hur lång tid från signal till omvärdering.
- `bolag/<namn>/vardering.json` – kurs, omvänd värdering, tre scenarier (försäljning × multipel, utspädning, sannolikhet) och jämförelse med liknande bolag. Webbsidan räknar fram matrisen. Metod: `metod/11-vardering-scenarier.md`. Det är räkneexempel och aldrig riktkurser eller råd.
- `bolag/<namn>/natverk.md` – personer (yrkesroller) och bolagssidor att följa på LinkedIn. Regler i `metod/08-linkedin-massor-forum.md`.
- `forumregister.md` – forumskribenter och hur träffsäkra de har varit.
- `bolag/<namn>/loften.md` – löftesrevisionen.
- `bolag/<namn>/tes.md` – aktuell tes med bevisnivåer, motbevis och bevakningspunkter.
- `bolag/<namn>/kallor.md` – alla källor med URL, datum och vad de visar.
- `bolag/<namn>/logg.md` – datumstämplad logg: vad som är nytt vid varje uppdatering och hur tesen påverkades.
- `larande/lektioner.json` – lektionerna i fliken Skolan.
- `bolag/<namn>/rapporter.json` – direktlänkar till rapporternas PDF:er. Skapas automatiskt av `verktyg/rapportlankar.py`, som nyhetskollen kör varje morgon.
- `bevakning.md` – bevakningslistan (bolag + nästa händelse) och kandidater från screening som ännu inte fått egen mapp.

## Kommandon (skills i tillägget; användaren kan också skriva vanlig svenska)
- `/investerarhjalpen:kom-igang` – första uppsättningen (redan gjord om `installningar.json` finns).
- `/investerarhjalpen:uppdatera-verktyget` – hämta senaste versionen av verktyget.
- `/investerarhjalpen:forslag` – skriv ett förbättringsförslag om verktyget att skicka till den som underhåller det.
- `/investerarhjalpen:bolagsanalys <bolag>` – bygg ett nytt case från grunden.
- `/investerarhjalpen:uppdatera <bolag>` (eller "uppdatera mig om X") – läs tesen, sök nytt, jämför, logga.
- `/investerarhjalpen:screening` – leta nya turnaround-/tenbaggerkandidater enligt checklistan.
- `/investerarhjalpen:loftesrevision <bolag>` – följ upp 2–3 års löften från bolaget.
- `/investerarhjalpen:tema [tema]` – analysera ett tema, eller leta efter nästa stora fokusområde.
- `/investerarhjalpen:fond` (eller "följ fonden X", "sök fonder", "vilka fonder äger X?") – fondverktyget.
- `/investerarhjalpen:trendspaning` (eller "kör trendspaningen", "kommer X att slå igenom?") – trendradarn: spana efter och följ stora skiften i världen.
- `/investerarhjalpen:panel <bolag>` (eller "investerarpanelen för X", "hur skulle Buffett se på X?") – ta fram eller uppdatera investerarpanelen.

När användaren klistrar in text (forum, X, LinkedIn, Copilot-svar): behandla den som **påståenden att kontrollera**, inte som fakta.

## Gemensamt och privat
- **Gemensamt (i tillägget, uppdateras för alla):** de här reglerna, metoden, skills, skript, Skolan och webbsidans utseende och funktioner.
- **Privat (i användarens datamapp):** vilka bolag användaren följer och analyserna av dem, strategin, journalen, inställningarna och portföljen.
- Ändra aldrig tilläggets filer i användarens session; de skrivs över vid nästa uppdatering. Förbättringsidéer skickas med `/investerarhjalpen:forslag`.
