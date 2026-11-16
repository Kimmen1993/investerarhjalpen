# Så fungerar verktyget – översikt och kontrollpunkter

Den här sidan förklarar kort vad verktyget gör, vilka regler det följer och hur du själv kan kontrollera att det fungerar. Varje del länkar till metoden där alla detaljer står.

**Hittar du något som inte stämmer med det som står här?** Skriv `jag har ett förslag` i Claude-appen och beskriv vad du såg och vad du väntade dig. Det är det bästa sättet att hitta buggar.

Två saker gäller överallt:
- **Inga köp- eller säljråd.** Verktyget visar fakta och läget enligt din egen strategi. Besluten är dina.
- **Bevisnivåer:** A = står i en originalkälla, B = stark indirekt koppling, C = slutsats, ? = inte kontrollerat.

---

## 1. Varje dag: morgonkollen
**Vad:** varje vardag kl. 08.30 hämtar verktyget nya pressmeddelanden (MFN), insynsaffärer (FI) och kurser (Yahoo, ca 15 minuters fördröjning) för dina bevakade bolag. Det kostar nästan inget, eftersom ingen AI används för hämtningen. Har inget hänt stannar den direkt. Annars sammanfattar Claude varje nyhet på klarspråk, uppdaterar trafikljuset och skickar en notis.

**Trafikljuset:**
| Färg | Betyder |
|---|---|
| 🟢 Grön | Tesen håller |
| 🟡 Gul | Något viktigt försvagar eller är oklart: en missad milstolpe, en svag rapport, en mindre insiderförsäljning |
| 🔴 Röd | Något på listan "Vad skulle fälla tesen?" har hänt: en emission med stor rabatt, en förlorad nyckelkund, en vinstvarning, en stor insiderförsäljning |

Rött ändrar aldrig beslutet automatiskt. Du får en notis och tar ställning själv.

**Nytt sedan sist** (överst på Läget nu): varje gång sidan byggs jämförs den med förra bygget. Allt nytt sparas med tidpunkt: händelser, ändrade trafikljus och beslut, nya rapporter, djupdykningar och panelkort, nya bolag på radarn, triagebeslut och nya fonddata. Rutan visar det som har kommit sedan ditt förra besök. Webbläsaren kommer ihåg det, och första gången visas de senaste 3 dagarna. Du kan också välja de senaste 7 dagarna. Dina egna innehav visas först, men bara för dig. Har sidan inte uppdaterats på över ett dygn en vardag visas en gul varning.

**Notis i mobilen:** kräver Claude-appen i mobilen, inloggad på samma konto, och att Remote Control är påslaget för nya sessioner i Claude-appen på datorn. Notisen skickas bara när du inte sitter vid datorn.

**Kontrollera själv:** öppna bolagets pressmeddelanden (knappen på bolagssidan) och se att de senaste finns under Senaste nytt med en rimlig förklaring. Jämför tiden "Sidan uppdaterades" i rutan Nytt sedan sist med när morgonkollen kördes.

---

## 2. Hitta nya bolag: signalradarn
**Vad:** varje morgon letar radarn efter tidiga signaler på hela den svenska börsen. Signalerna ger poäng, och poängen summeras över 90 dagar.

| Signal | Poäng |
|---|---|
| Första order, genombrott, kvalificering eller pilot | +3 |
| Strategiskt samarbete eller partnerskap | +3 |
| Insiderköp i kluster (minst 2 personer, eller minst 0,5 MSEK på 14 dagar) | +3 |
| Fondköp (en gång per kvartal) | +2 till +4 |
| Ramavtal eller större order | +2 |
| Ny strategisk ägare | +2 |
| Ny vd eller styrelseordförande | +1 |
| Fonder lämnar | −2 |
| Vinstvarning, företrädesemission, rekonstruktion, insiders säljer | −3 |

- Nya signaler väger fullt de första 30 dagarna, 60 % dag 31–60 och 30 % dag 61–90.
- Två eller fler olika typer av positiva signaler ger +2 i bonus.
- Bolag med minst 3 poäng syns under Radar (högst 40). Bevakade och kastade bolag, och de största börsbolagen, hoppas över.
- Varje söndag gör Claude en kort triage av högst 5 bolag: *Radar* (följ passivt), *Bolagsanalys* eller *Bort*.

**Kontrollera själv:** klicka på en signal under Radar och se att pressmeddelandet verkligen säger det signalen påstår. Räkna ihop poängen för ett bolag och jämför.

Läs mer: [Metod 15, Bolagsjakt](#metod-15)

---

## 3. Bedöma ett bolag: spåret avgör måttstocken
**Vad:** varje bolag har exakt ett spår, och det står överst på bolagssidan.
- **Vändning:** bolag som ännu inte bär sig själva. De mäts med turnaround-steg 1–5 och redo-poäng.
- **Kärna:** lönsamma bolag. De mäts på kvalitet och pris, med Peter Lynchs kategori.

Står det *(förslag)* har verktyget gissat spåret. Du bekräftar med `ja till spåret för <bolag>`.

**Redo-poängen** (bara Vändning): tio punkter med 0–2 poäng var, max 20.
| Poäng | Läge enligt din strategi |
|---|---|
| 15–20 | Fas 2: vändningen bekräftad, läge att ta ställning till en större position |
| 10–14 | Fas 1: tidigt läge, en liten startposition kan vara aktuell om tesen håller |
| under 10 | För tidigt |

**Kontrollera själv:** öppna Redo-poäng på ett bolag och se att varje punkt har en motivering som stämmer med siffrorna under Siffror per kvartal.

Läs mer: [Metod 15](#metod-15) (redo-poängen) och [Metod 18, Spår och investerarpanelen](#metod-18)

---

## 3b. Tesens pelare och jämförelsen
**Vad:** varje bolag får 3–5 **pelare**, det som måste stämma för att tesen ska hålla. Varje pelare visar vad vi väntade oss, läget nu och en pil: ↑ stärks, → oförändrat, ↓ försvagas. Pilarna syns också i korten på Läget nu. **Jämförelsen** ställer bolaget bredvid 3–5 liknande bolag (börsvärde, EV/S, tillväxt och marginal) och svarar på vad marknaden betalar för bolag som redan har kommit längre. Båda ses över vid varje djupdykning.

**Kontrollera själv:** läget för varje pelare ska ha en bevisnivå och stämma med Senaste nytt och Siffror per kvartal.

Läs mer: [Metod 20](#metod-20)

---

## 3c. Kalendern
**Vad:** fliken Kalender samlar allt som händer framöver: rapporter, stämmor, emissioner, mässor och studier, och Riksbankens räntebesked. Datum som inte är klara visas per månad och fylls i vid djupdykningen. **Dagen före en rapport** skriver morgonkollen *Vad ska jag titta efter?*. Söndagens notis har en rad om **veckans viktigaste datum**, och Läget nu visar *Snart*: de närmaste 14 dagarna.

**Kontrollera själv:** jämför rapportdatumen med bolagets finansiella kalender på IR-sidan.

---

## 3d. Trendradarn
**Vad:** stora skiften i hela världen som vi följer under flera år, till exempel elflyg, drönare, robotar och fetmaläkemedel. Varje trend är en fråga som går att besvara om några år. Mätarna hämtas gratis varje vecka: adoption, kostnad, beslutade pengar, forskning och uppmärksamhet. Forskning och läsning räknas som andel av totalen. Trenden jämförs med ett **historiebibliotek** av vinnare (elbilar, upprustningen), förlorare (vätgasbilar, 3D-skrivare) och "rätt trend, fel bolag" (vind- och solkraft).
- **Saknar hårda data** betyder att det ännu inte finns någon mätare för adoption, kostnad eller pengar. Då går trenden inte att bedöma, hur mycket det än forskas.
- **Hypevarning** betyder att uppmärksamheten växer mycket snabbare än köpen, medan under 2 % av marknaden har tagit till sig det nya.
- Första söndagen i månaden spanar Claude efter nya trender (högst 2 per månad) och ser över de gamla. Status ändras högst ett steg per månad.

Trenderna finns under fliken Teman.

**Kontrollera själv:** öppna en mätare och jämför med källan, till exempel elbilarnas andel hos Our World in Data.

Läs mer: [Metod 21, Trendradarn](#metod-21)

---

## 4. Investerarpanelen
**Vad:** sex knappar på varje bolagssida visar bolaget med Buffetts, Lynchs, Fishers, Grahams, Terry Smiths och Blankarens glasögon. Varje investerare har en fast checklista, så att korten går att jämföra. Det är tolkningar av deras publicerade filosofi, inga citat. En blå prick betyder att rösten väger tyngst för bolagets spår. Panelen ändrar aldrig bedömningen.

**Kontrollera själv:** jämför ett kort med checklistan i metod 18. Siffrorna på kortet ska ha en bevisnivå och finnas i bolagets data.

Läs mer: [Metod 18](#metod-18)

---

## 5. Djupdykningen varje söndag
**Vad:** söndagar kl. 17 går Claude igenom de bolag som inte har granskats på 27 dagar, högst 5 per söndag. Det blir ungefär en gång i månaden per bolag. Genomgången följer en fast ordning: bolaget, kunder och partners, konkurrenter, bransch, ägare, forum, motbevis, redo-poäng och panel. Rapporten finns under fliken Djupdykningar på bolagssidan.

**Kontrollera själv:** datumet för senaste djupdykning står i bolagets akt. Inget bolag ska ha gått mer än ca 5 veckor utan genomgång.

Läs mer: [Metod 01, Pusselmetoden](#metod-01), [Metod 05, Löftesrevision](#metod-05) och [Metod 14, Samlad bedömning](#metod-14)

---

## 6. Fonder
**Vad:** fliken Fonder visar avgift, vad avgiften kostar på 10 år, typ (index eller aktiv), risk, innehav, vad förvaltaren har köpt och sålt, och överlapp mellan fonder. Datan kommer från Finansinspektionen en gång i kvartalet. Utländska fonder får sina innehav från fondbolagets egen fil, eller från en svensk ersättningsfond, och då står det "Uppskattning".

**Fondkollen** varnar när två fonder du äger överlappar med minst 50 %, eller när du äger samma bolag via flera vägar och det tillsammans blir minst 10 % av portföljen.

**Kontrollera själv:** jämför de största innehaven med fondbolagets egen rapport.

Läs mer: [Metod 19, Fonder: så räknar verktyget](#metod-19)

---

## 7. Min portfölj
**Vad:** dina affärer från Avanza eller Handelsbanken (CSV- eller Excel-fil) räknas om till innehav, snittpris (GAV) och avkastning. Portföljen sparas privat per person och syns aldrig för andra, även om sidan delas. Varje innehav får en strategikoll: trafikljus, fas för vändningsbolag och spår för kärnbolag. Fördelningen visar hur stor del som ligger i Vändning och Kärna, och i Lynchs kategorier.

**Kontrollera själv:** jämför antal och snittpris för några innehav med bankens egen översikt.

---

## Alla metoder
| Metod | Handlar om |
|---|---|
| [01](#metod-01) | Pusselmetoden: informationsövertag utan att lura sig själv |
| [02](#metod-02) | Turnaround- och tenbaggerchecklistan |
| [03](#metod-03) | Källkarta: var informationen finns |
| [04](#metod-04) | Varningsflaggor: hype, bluff och självbedrägeri |
| [05](#metod-05) | Löftesrevision: håller ledningen vad den lovar? |
| [06](#metod-06) | Omvärld och teman |
| [07](#metod-07) | Beslut, turnaround-steg och jämförelse |
| [08](#metod-08) | LinkedIn, mässor och forum |
| [09](#metod-09) | Spår och signaler i verkligheten |
| [10](#metod-10) | Tankebanor: hur de bästa investerarna tänker |
| [11](#metod-11) | Värdering i scenarier |
| [12](#metod-12) | Pipeline och framtid |
| [13](#metod-13) | Marknaden uppifrån |
| [14](#metod-14) | Samlad bedömning: väg alla linser |
| [15](#metod-15) | Bolagsjakt, radarn och redo-poängen |
| [16](#metod-16) | Efterfrågan |
| [18](#metod-18) | Spår och investerarpanelen |
| [19](#metod-19) | Fonder: så räknar verktyget |
| [20](#metod-20) | Tesens pelare och jämförelsen med liknande bolag |
| [21](#metod-21) | Trendradarn: stora skiften i världen |
| [Ordlista](#metod-ordlista) | Alla förklarade ord |
| [Min strategi](#metod-strategi) | Din egen strategi (personlig) |
