# Trendradarn – att se nästa stora skifte i världen tidigt

Den bästa investeringen börjar ofta ta form 1–2 år innan man köper. Trendradarn följer stora skiften i **hela världen** under lång tid, mäter dem med samma data varje månad och letar sedan upp de bolag, helst svenska och nordiska, som kan rida på vågen. Det gäller både vändningsbolag och stora, stabila bolag.

Trendradarn arbetar i två steg:
1. **Djärva hypoteser (före bevisen).** Här får verktyget gissa och pussla, på samma sätt som de investerare som såg något flera år före alla andra. Det är här pengarna kan tjänas.
2. **Trender (när bevisen kommer).** Hypoteserna prövas mot data som samlas i flera år. Det som håller blir en trend som följs. Det som inte håller avfärdas, med lärdomen sparad.

Ingen kan förutse framtiden säkert. En hypotes är en kvalificerad gissning med bevisnivå C, och den märks alltid så. Besluten fattar användaren.

Metod 06 beskriver hur ett enskilt tema analyseras. Den här metoden beskriver hur trender hittas, mäts och följs över flera år.

**Banken sköts i bakgrunden.** Verktyget samlar information varje månad, sparar den och följer upp den. På sidan visas de djärva hypoteserna överst, sedan trender med bevis. Banken finns kvar tills den behövs.

## A. Djärva hypoteser: före bevisen
**När något syns i statistiken är det ofta redan i priset.** Därför börjar trendradarn med hypoteser: kvalificerade gissningar om vad som kan hända, byggda av pusselbitar som de flesta inte orkar lägga.

**Förebilden är Michael Burry**, som flera år före finanskrisen 2008 förutsåg att den amerikanska bostadsbubblan skulle spricka. Han gissade inte i blindo:
- **Han läste det ingen läste:** prospekten för hundratals bolånepaket, sida för sida. Där syntes att lånen var mycket sämre än marknaden trodde.
- **Han såg en mekanism med ett datum:** lågräntelånens räntor skulle räknas om 2006–2007. Då skulle många inte klara betalningarna.
- **Han hade asymmetri:** om han hade fel var förlusten begränsad, om han hade rätt blev vinsten mångdubbel.
- **Han var för tidig:** det tog nästan två år innan marknaden höll med, och under tiden ifrågasatte hans investerare honom. Rätt tes med fel tidpunkt är också en risk.

### Så byggs en hypotes
| Del | Fråga |
|---|---|
| **Påstående** | Vad tror vi kommer att hända, och ungefär när? |
| **Riktning** | Möjlighet (något växer) eller risk (något är skört och kan spricka)? |
| **Konsensus** | Vad tror de flesta i dag? |
| **Var konsensus kan ha fel** | Vad ser vi som de missar, och varför missar de det? |
| **Mekanismen** | Varför skulle det hända? Orsak och verkan i klartext |
| **Pusselbitarna** | Bitarna som pekar dit, var och en med källa och bevisnivå. Gärna från källor som få läser |
| **Tidiga tecken** | Vad borde synas först om vi har rätt? De följs upp varje månad |
| **Utlösaren** | Finns det ett datum eller en händelse som tvingar fram förändringen, som räntorna 2007? |
| **Asymmetrin** | Vad händer om vi har rätt, och vad händer om vi har fel? |
| **Vad fäller den?** | Det som skulle visa att hypotesen är fel |
| **Vår sannolikhet** | En siffra i procent. Den ändras när tidiga tecken syns eller uteblir |

### Var de bästa hypoteserna finns
- **Källor som få läser:** budgetpropositioner och deras bilagor, upphandlingsunderlag, myndigheters ansökningsregister (patent, frekvenser, tillstånd, kliniska prövningar), fotnoter i årsredovisningar, centralbankers stabilitetsrapporter, handels- och tullstatistik, platsannonser och bygglov. Varje månad läses några av dem på riktigt.
- **Glappet mellan berättelse och verklighet:** när det som sägs och det som syns i siffrorna går isär.
- **Det sköra:** hög belåning, priser långt över det som går att motivera, villkor som ändras vid ett visst datum, beroende av en enda leverantör eller ett enda land.
- **Andra och tredje ledet:** om X händer, vem behöver vad sedan? Marknaden prissätter oftast första ledet.
- **Tråkiga områden:** där ingen tittar, eftersom det inte är spännande.

### Regler för hypoteser
- En hypotes är alltid **C-nivå** som helhet och märks som gissning. Pusselbitarna har sina egna nivåer.
- Varje hypotes måste ha **tidiga tecken** och **vad som fäller den**. Annars går den inte att pröva.
- **Sannolikheten skrivs ner från början** och ändras med motivering. Facit sparar alla hypoteser med datum och utfall, så att vi lär oss hur ofta våra gissningar slår in. Även 30 % träffar kan räcka om vinsterna är mycket större än förlusterna.
- När hälften av de tidiga tecknen har synts flyttas hypotesen till **kandidat** och mäts som en trend.
- **Tidig betyder följa tidigt, inte köpa allt tidigt.** Användarens strategi avgör om en liten startposition är aktuell. Verktyget ger inga köp- eller säljråd.

## 0. Informationsbanken
All information som spaningen hittar sparas som **observationer** i `trender/bank/`, även sådant som inte hör till någon trend än. Banken raderas aldrig. Varje observation har datum, område, typ (beslut, investering, regel, tidsplan, milstolpe, försening, bakslag, siffra eller forskning), aktör, källa, bevisnivå och taggar. Skriptet `verktyg/trendbank.py` håller ordning på den.

**Brett, inte bara det användaren nämner.** Spaningen sveper över 16 fasta områden varje månad: energi, transport, hälsa, livsmedel och vatten, rymd, försvar, AI och data, halvledare, material och råvaror, bygg och städer, finans, demografi och arbete, klimat, konsumenter, geopolitik och handel, samt industri och automation. Användarens frågor och exempel läggs till ovanpå, men styr aldrig vilka områden som söks.

**Nya trender växer fram ur banken.** När samma ämne (tagg) dyker upp i minst 3 observationer, av minst 2 slag och från minst 2 källor, utan att höra till någon trend, föreslår skriptet en ny kandidat.

## 0b. Tidsplaner, förseningar och källfacit
Nya områden blir nästan alltid en kapplöpning, och nästan allt blir försenat. Därför sparas varje **tidsplan** (vem som har lovat vad till när) och varje uppföljning: en ny tidpunkt, en milstolpe som nås eller en plan som stryks. En försening gör inte att vi slutar följa trenden. Vi flyttar fram datumet och följer vidare.

Över tid ger det ett **källfacit**: hur ofta olika slags aktörer håller sina tidsplaner, och hur mycket de brukar bli försenade. Stater, EU, storbolag, nystartade bolag, forskare och analytiker räknas var för sig. Det är samma tanke som löftesrevisionen för bolag (metod 05), men för hela branscher. Det svarar på vilken information man kan lita på. Om nystartade bolag i en bransch brukar bli 3 år sena, ska en ny tidsplan därifrån läsas med det i bakhuvudet.

## 1. En trend börjar med en fråga
Varje trend formuleras som en fråga som går att besvara med ja eller nej om några år, till exempel:
- Blir elflyg vanligt på sträckor under 500 km?
- Blir läkemedel mot fetma lika vanliga som blodtrycksmedicin?
- Ersätter robotar en stor del av arbetskraften i åldrande länder som Kina och Japan?
- Kommer flygande taxibilar i reguljär trafik i någon storstad?

En tydlig fråga gör att trenden går att följa, och att vi kan se om vi hade rätt.

## 2. Hela världen, sju drivkrafter
Spaningen söker brett, inte bara i Sverige. Världen sätter farten, och svenska bolag rider på vågen. Spaningen går igenom sju drivkrafter (se också metod 06):

| Drivkraft | Exempel |
|---|---|
| **Beslutade pengar** | Försvarsbudgetar, EU:s och USA:s program, storbolagens investeringsplaner |
| **Kostnader som faller** | Batterier, solpaneler, uppskjutningar, gensekvensering |
| **Flaskhalsar** | El, chips, kylning, råvaror, kompetens |
| **Regler med datum** | Utsläppskrav, förbud, certifieringar |
| **Geopolitik** | Krig, sanktioner, självförsörjning, nya allianser |
| **Demografi och hälsa** | Åldrande, fetma, urbanisering, nya sjukdomsmönster |
| **Tekniska genombrott** | Nya material, nya behandlingar, AI-förmågor |

## 3. Mät, år efter år
Varje trend får **mätare** som hämtas automatiskt och gratis (`verktyg/trendmatare.py`). Värdena sparas och raderas aldrig, så att kurvorna blir längre för varje år.

| Typ | Vad den visar | Källor |
|---|---|---|
| **Adoption** | Hur stor del av marknaden som redan använder det nya | Our World in Data, statistik |
| **Kostnad** | Om priset faller tillräckligt snabbt | Our World in Data |
| **Kunskap** | Forskning och kliniska prövningar | OpenAlex, ClinicalTrials.gov |
| **Uppmärksamhet** | Hur mycket folk läser om ämnet | Wikipedias sidvisningar |
| **Manuell** | Beslut, order och milstolpar som inte finns som tidsserie | Spaningen skriver in dem med källa |

Forskning och läsning räknas som **andel av totalen**. Forskningen växer överlag, och färre läser Wikipedia sedan AI-tjänsterna kom. Utan den justeringen ser allt ut att växa eller krympa.

**Lärdom ur historien:** forskning ensam räcker inte. Forskningen om vätgasbilar växte lika snabbt som den om elbilar, men vätgasbilarna slog aldrig igenom. Det som skilde dem åt var att folk köpte elbilar, och att batterierna blev billigare varje år. Därför väger **adoption och kostnad** tyngst.

## 4. S-kurvan och tröskeln
Nya saker sprids nästan alltid längs en S-kurva: långsamt, sedan mycket snabbt, sedan långsamt igen.

| Andel av marknaden | Läge | För oss |
|---|---|---|
| under 2 % | Tidigt | Följ. Svårt att veta om det blir av |
| **2–10 %** | **Genombrott** | **Huvudläget:** bevisat, men inte färdigt. Elbilar var här 2018–2021 |
| 10–50 % | Mainstream | Tillväxten fortsätter, men den finns i priset |
| över 50 % | Mättnad | Vinnarna är redan utsedda |

Varje trend får också en eller flera **trösklar**: det som måste hända innan trenden kan ta fart, till exempel "batterier med minst 400 Wh/kg i serieproduktion" för elflyg, eller "certifiering hos EASA och FAA" för flygande taxibilar. Trösklarna mäts när det går. Ett steg närmare tröskeln är en av de starkaste signalerna.

## 5. Hypevarningen
**Hypevarning** när uppmärksamheten växer mycket snabbare än de hårda data (adoption, kostnad, beslutade pengar) medan adoptionen fortfarande är under 2 %. Utan en mätare för adoption går det inte att bedöma, och då står det **"saknar hårda data"**. Forskning räknas som kunskap, inte som hårda data. Det var mönstret för vätgasbilar, cannabis 2018 och 3D-skrivare 2013. En trend med hypevarning flyttas inte upp förrän substansen hinner ikapp.

## 6. Konsekvenskedjor: tänk två steg till
Den största vinsten finns ofta i andra eller tredje ledet. För varje trend skrivs en kedja: **om** det här händer, **vad händer då?**

Exempel: elflyg blir billigt på korta sträckor → fler små flygplatser används igen → efterfrågan på laddinfrastruktur vid flygplatser → regionala flygbolag och laddbolag gynnas, medan vissa tåglinjer får färre resenärer.

Varje led är en egen hypotes med bevisnivå, oftast C tills den bekräftas. Kedjor med många C-led i rad är svaga (metod 01).

## 7. Från trend till bolag
1. **Värdekedjan och flaskhalsen** (metod 06). Vinsten hamnar oftast hos den som äger flaskhalsen, inte hos den som syns mest.
2. **Rätt trend, fel bolag** är den vanligaste fällan. Vindkraften växte kraftigt, men flera av de stora tillverkarna förlorade pengar. Fråga alltid vem som har prissättningsmakt.
3. **Bolag i båda spåren:**
   - **Vändning:** mindre bolag där trenden kan bli hela affären.
   - **Kärna:** större bolag där trenden är tillräckligt stor för att flytta hela bolaget. En het division som är 3 % av omsättningen flyttar inte aktien.
4. **Exponering:** hög (trenden är kärnan i affären), medel eller låg.

## 8. Onoterade bolag och vägar in
Ibland finns de mest intressanta bolagen inte på börsen, som Aira inom värmepumpar eller Heart Aerospace inom elflyg. Skriv in dem ändå, och leta efter **vägar in**:
- **Noterade ägare:** investmentbolag eller andra noterade bolag som äger en del, till exempel Flat Capital, Kinnevik eller Investor.
- **Noterade partners:** leverantörer, kunder eller samarbetspartners, till exempel Ferroamp, som samarbetar med Aira.
- **Kommande noteringar:** planer på börsnotering.
- **Nyemissioner och crowdfunding** för onoterade bolag. Det är hög risk, ofta svårt att sälja och kräver egen kontroll.

Verktyget visar vägarna. Det rekommenderar aldrig någon av dem.

## 9. En trends liv
| Status | Betyder |
|---|---|
| **Hypotes** | En djärv gissning med pusselbitar, tidiga tecken och vad som fäller den (avsnitt A) |
| **Kandidat** | Ny. Bevisen är tunna, och mätarna ska få samla data |
| **Följs** | Minst en drivkraft på A-nivå och mätare som växer |
| **Stärks** | Adoptionen eller kostnaden rör sig åt rätt håll i minst två mätningar i rad, utan hypevarning |
| **Genombrott** | Adoption 2–10 % eller en tröskel passerad. Huvudläget för att leta bolag |
| **Mainstream** | Över 10 %, eller tydligt upptäckt av alla |
| **Avfärdad** | Substansen uteblev. Trenden sparas med lärdomen |

Status ändras bara med en motivering och ett datum i trendens logg, och aldrig mer än ett steg per månad. Loggen sparas, så att vi om några år kan se om trendradarn såg saker tidigt.

**Det som visas på sidan:** trender med status Följs eller högre, och det som har ändrats sedan förra månaden. Kandidater och banken ligger i bakgrunden, men går att öppna.

## 10. Historiebiblioteket
`trender/historia/` innehåller trender där vi vet hur det gick: vinnare, förlorare och "rätt trend, fel bolag". För varje fall: vilka signaler syntes när, vilken fas det var och vem som tjänade pengarna. Nya trender jämförs med dem: *ser det här ut som elbilar 2018 eller som vätgas 2019?*

## 11. Rytmen
- **Varje vecka** (söndag): mätaren körs, gratis.
- **Varje månad** (första söndagen): spaningen sveper över alla 16 områden, sparar observationerna i banken, följer upp tidsplaner som har passerat och ser över trenderna.
- **Varje kvartal:** konsekvenskedjor och bolagslistor ses över.
- **Trender rör sig långsamt.** Det är normalt att inget ändras på flera månader.

## Fil per trend: `trender/<trend>.json`
Fälten: `namn`, `fraga`, `taggar` (kopplar observationer i banken till trenden), `i_en_mening`, `status`, `fas`, `upptackt`, `drivkrafter`, `troskel`, `matare`, `serier` (skrivs av skriptet), `signal` (räknas av skriptet), `konsekvenser`, `motbevis`, `bolag`, `logg`. Historiska fall har dessutom `facit`. Mall: `$IH/mall-trend.json`.
