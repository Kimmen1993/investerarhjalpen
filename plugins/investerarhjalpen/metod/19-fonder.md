# Fonder – så räknar verktyget

Allt som syns under fliken Fonder, i fondkollen och i fondsignalerna räknas fram av skriptet `verktyg/fonder.py`. Skriptet är gratis och använder ingen AI. Här står exakt vad det gör, så att du kan kontrollera att siffrorna stämmer.

## 1. Varifrån kommer datan?
| Källa | Vad den ger | Hur ofta |
|---|---|---|
| **Finansinspektionen (FI)**, "Fondinnehav per kvartal" | Alla svenskregistrerade fonders hela innehav, förvaltningsavgift per andelsklass, jämförelseindex, aktiv risk, standardavvikelse och fondförmögenhet | En gång i kvartalet. I praktiken publiceras datan ca 4–5 månader efter kvartalets slut, till exempel data per 30 juni den 12 november |
| **Fondbolagets egen innehavsfil** (Excel eller CSV) | Hela innehavet för en utländsk fond | Hämtas igen när det gått 25 dagar sedan förra gången |
| **Fondbolagets rapport** (PDF), inläst av Claude | De största innehaven, branscher och länder | Ungefär en gång i kvartalet |
| **Ersättningsfond** | Innehaven lånas från en svensk indexfond med liknande index | Som FI:s data |

Morgonkollen kör skriptet varje vardag. Det hämtar bara något när FI har publicerat ett nytt kvartal (ca 6 MB).

**Kontrollera själv:** datumet "data per" på fondsidan ska vara samma kvartal som den senaste filen på [FI:s sida](https://fi.se/sv/vara-register/fondinnehav/fondinnehav-per-kvartal/).

## 2. Faktarutan på varje fond
| Ruta | Så räknas den |
|---|---|
| **Avgift per år** | FI:s förvaltningsavgift för den andelsklass privatpersoner oftast köper: A-klassen i SEK, annars den dyraste klassen i SEK. Alla klasser visas bakom ett klick. För utländska fonder: avgiften i faktabladet, inskriven för hand |
| **Kostar på 10 år** | Skillnaden mellan 100 000 kr som växer 7 % per år och samma belopp som växer 7 % minus avgiften, efter 10 år |
| **Typ** | *Fond i fonder* om över 50 % är andelar i andra fonder. *Ränte- eller blandfond* om under 40 % är aktier. *Indexfond* om namnet innehåller "index" eller "zero", om den aktiva risken är under 1 %, eller om aktiv risk saknas och avgiften är högst 0,3 %. Annars *Aktivt förvaltad* |
| **De 10 största** | De tio största innehavens andel av fonden tillsammans |
| **Risk** | Standardavvikelsen de senaste 24 månaderna: under 5 % låg, 5–12 % medel, 12–18 % medelhög, över 18 % hög |
| **Mot sitt index** | Aktiv risk: under 1 % följer index nästan exakt, 1–3 % ganska nära, 3–6 % tydlig avvikelse, över 6 % stor avvikelse |
| **Varningen "dyr indexfond"** | Visas när en aktivt förvaltad fond har aktiv risk under 3 % och avgift på minst 1 % |

## 3. Vad förvaltaren har köpt och sålt
- Jämför det senaste kvartalet med kvartalet innan, innehav för innehav (via ISIN-numret).
- **Antalet aktier** används, inte andelen. Andelen ändras även när bara kursen rör sig.
- **In- och utflöden räknas bort:** när sparare sätter in pengar köper fonden mer av allt. Verktyget tar medianförändringen av antalet aktier i hela fonden som fondens flöde och delar varje innehavs förändring med den.
- **Ökat** betyder minst 15 % fler aktier efter flödet och minst 0,3 % av fonden. **Minskat** betyder minst 15 % färre aktier. **Ny** och **Sålt allt** visas om innehavet är minst 0,05 % av fonden.
- En mycket stor ökning kan bero på en aktiesplit.

**Kontrollera själv:** öppna fondbolagets halvårs- eller årsrapport och jämför några av de största innehaven.

## 4. Överlapp mellan fonder
- Överlappet är **summan av den minsta vikten per gemensamt innehav**. Äger fond A 5 % Apple och fond B 3 % Apple, räknas 3 %. Allt gemensamt summeras.
- Innehav kopplas ihop via ISIN-numret. Saknas ISIN (vanligt i utländska fonders filer) letas det upp via bolagsnamnet bland alla innehav i FI:s data.
- Över ca 50 % betyder att fonderna gör ungefär samma jobb.

## 5. Fondkollen (dina egna fonder)
Görs i webbläsaren och syns bara för den inloggade användaren, under Min portfölj och Fonder.
- **Vilka fonder äger du?** Innehaven i portföljen matchas mot FI:s fondregister, först på ISIN och sedan på fondnamnet (utan andelsklass och valuta).
- **Varning om överlapp:** två fonder du äger överlappar med 50 % eller mer.
- **Varning om samma bolag via flera vägar:** genomlysningen lägger ihop det du äger via fonderna (fondens värde × bolagets andel i fonden) med aktier du äger direkt. Varning när samma bolag kommer från minst två håll och tillsammans är minst 10 % av portföljen. Ett informationsmeddelande när du äger ett bolag både direkt och via fonder och det är minst 3 % av portföljen.
- Fonder utan aktuell kurs räknas på vad du betalade.
- **Notis:** när ett nytt kvartal kommer gör morgonkollen samma kontroll och skriver varningarna i notisen.

## 6. Fonder som äger dina bevakade bolag
- Varje bevakat bolag (med ISIN i `status.json`) letas upp i **alla** svenska fonder, både index och aktiva.
- Status per fond: *Ny ägare*, *Har sålt allt*, *Har ökat* (minst 10 % fler aktier efter fondens flöde), *Har minskat* (minst 10 % färre) eller *Oförändrat*.

## 7. Fondsignaler på hela börsen (radarn)
Letar efter mindre svenska bolag (ISIN som börjar med SE) som fonderna börjar köpa eller lämnar.

**Bara aktivt förvaltade fonder räknas.** Bortsorterade är:
- indexfonder, som köper när ett bolag kommer in i ett index
- generations-, pensions- och blandfonder (namn med till exempel Generation, Pension, Mix, Selection, Transfer, Stratega), som köper efter en plan
- in- och utflöden, som räknas bort som ovan (gräns 10 %)

**Bortsorterade bolag och händelser:**
- bolag som redan ägs av fler än 30 aktiva fonder, eller där fondernas innehav är värt över 3 miljarder kr
- nya aktieslag, emissionsrätter, interimsaktier och obligationer
- byte av ISIN: samma namn försvinner ur minst 3 fonder och dyker upp med nytt ISIN i minst 3
- instrument som 8 eller fler fonder fick samtidigt utan att någon ägde dem innan
- fondköp där fondernas sammanlagda innehav är under 5 miljoner kr

**Poäng:**
| Signal | Villkor | Poäng |
|---|---|---|
| Fondköp, starkt | 3 eller fler nya fondägare, eller 5 fler köpare än säljare | +3 |
| Fondköp | 2 nya fondägare, eller 3 fler köpare än säljare | +2 |
| Tidigt-bonus | Högst 5 aktiva fonder ägde bolaget innan, och minst 2 nya | +1 |
| Nynoterat | Bolaget fanns inte i någon fond förra kvartalet | +2 (ingen bonus) |
| Fonder lämnar | 4 eller fler säljer allt, eller 5 fler säljare än köpare | −2 |

*Köpare* är nya ägare plus de som ökat. *Säljare* är de som sålt allt plus de som minskat.

Signalen får datumet då FI publicerade kvartalet. Den ingår i radarn i 90 dagar som alla andra signaler: full vikt de första 30 dagarna, 60 % dag 31–60 och 30 % dag 61–90. Om bolaget har ytterligare en typ av positiv signal, till exempel insiderköp, ger radarn +2 i bonus.

**Kontrollera själv:** tabellen under Radar visar vilka fonder som köpt. Leta upp fonderna i FI:s data eller på fondbolagets sida och se att bolaget finns med.

## 8. Utländska fonder
I den här ordningen:
1. **Fondbolagets innehavsfil** om Claude hittar en direkt länk till en Excel- eller CSV-fil. Rader med kassa, terminer och valuta sorteras bort. Vikter i decimalform (summa ca 1) räknas om till procent.
2. **Ersättningsfond** om fonden är en indexfond utan fil: USA och S&P 500 → Swedbank Robur Access USA, Europa → SEB Europe Exposure, Norden → Handelsbanken Norden Index Criteria, Sverige → Avanza Zero, MSCI World och ACWI → Swedbank Robur Access Global, globala småbolag → Handelsbanken Global Småbolag Index Criteria. Sidan visar en gul ruta med texten "Uppskattning".
3. **Claude läser fondbolagets rapport** och skriver in de största innehaven.

Fondsidan visar alltid vilken källa som används.

## Om något inte stämmer
Skriv `jag har ett förslag` i Claude-appen och beskriv vad du såg och vad du hade väntat dig enligt den här sidan. Ta gärna med fondens namn och vilket kvartal det gäller.
