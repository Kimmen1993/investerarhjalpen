# Värdering i scenarier – vad kan bolaget vara värt?

**Räkneexempel, inte riktkurser eller råd.** Syftet är att förstå vad som redan finns i priset och vad som måste hända för att det ska bli mer, eller mindre, värt.

## Grundidén
Värdet på ett tillväxtbolag ≈ **framtida försäljning × multipel + nettokassa**, delat med antalet aktier.
- **Försäljningen** beror på bolaget: ordrar, kunder, kapacitet.
- **Multipeln** (EV/S, alltså vad marknaden betalar per krona i försäljning) beror på marknaden: tillväxt, lönsamhet, bransch, och var i cykeln vi är.

Det mesta av rörelsen i ett turnaround-case kommer av att **båda** stiger samtidigt. När bolaget går från förlust till vinst brukar marknaden betala en högre multipel. Ett tenbagger-case är nästan alltid "försäljningen 3 gånger högre och multipeln 3 gånger högre".

## Fem steg
**1. Läget i dag.** Kurs, antal aktier, börsvärde, nettokassa, EV och EV/S på de senaste 12 månadernas försäljning. Skriv datum och källa för kursen.

**2. Omvänd värdering.** Vilken försäljning krävs för att dagens EV ska stämma med multiplerna 2x, 4x, 6x och 10x? Det visar vad marknaden redan tror.

**3. Försäljning om 2 år, i tre scenarier.**
| Scenario | Hur det tas fram |
|---|---|
| Svagt | Basfrekvensen: liknande bolag brukar bli försenade. Lägre än bolagets mål |
| Troligt | Bolagets mål, justerat med löftesrevisionens precision. Kontrollera mot orderboken eller det kontrakterade värdet |
| Starkt | Bolagets mål i övre delen, plus de katalysatorer som är beskrivna (stora avrop och konstellationer) |

**4. Multipel för varje scenario**, från jämförelsen:
- **Direkta konkurrenter** i samma bransch och storlek
- **Bolag som gjort resan**, alltså gått från förlust till vinst eller från litet till stort, även i andra branscher. Vilken multipel hade de före och efter?
- **Branschens snitt och spridning**, gärna med ytterkanterna förklarade

Låt multipeln följa scenariot: ett svagt scenario får en låg multipel, ett starkt får en högre. Det är så marknaden brukar fungera.

**5. Matris och vägning.**
- Matrisen visar försäljning × multipel som kr per aktie, så att man ser hela spannet.
- De sammanhängande scenarierna ger varje scenario sin multipel, nettokassa, antal aktier (inklusive framtida utspädning) och sannolikhet. Ett vägt värde räknas fram.
- Jämför med dagens kurs. Ligger dagens kurs nära det svaga scenariot är risken lägre; ligger den nära det starka har marknaden redan räknat med mycket.

## Två tidshorisonter
- **2 år:** vad som rimligen kan hända med de avtal som redan finns. Där kommer de flesta kursrörelser de närmaste åren ifrån.
- **5 år:** hela resan. Tillväxt, lönsamhet och en högre multipel hinner samverka. Det är här tenbaggers syns. Tillväxt räknas som ränta-på-ränta: 30 % per år i 5 år ≈ 3,7 gånger, och 45 % per år ≈ 6,4 gånger.

## Rimlighetskontroll 1: räkna i styck
Omvandla försäljningen till enheter, kunder eller satelliter: **försäljning ÷ intäkt per enhet**. Kräver scenariot fler enheter än marknaden kan ta, eller fler än bolaget kan tillverka, är det orimligt. Ett avtal "värt ett par miljarder" kräver till exempel 1 000–2 000 datorer om en dator ger 1–2 MSEK. Det motsvarar mycket stora program, inte en enskild konstellation på 50 satelliter.

## Rimlighetskontroll 2: avtalets värde är inte bolagets värde
- Ett avtal värt X kr fördelat över N år ger ungefär X/N kr i försäljning per år.
- Bolagets värde ≈ den årliga försäljningen × multipeln.
- Ett avtal på 2 mdr kr över 5 år ger ca 400 MSEK per år. Vid 5x blir det ca 2 mdr kr i värde, plus värdet av resten av affären.

## Från framtid till i dag (diskontering)
Ett värde om 5 år är inte jämförbart med dagens kurs. Dela med (1 + avkastningskrav)^5. Med 20 % per år betyder det att 25 kr om 5 år motsvarar ca 10 kr i dag. Då syns om dagens kurs ger betalt för risken och väntan.

## Fällor
- **Utspädning:** räkna alltid med optioner och troliga emissioner i scenarier där kassan tar slut.
- **Multipelns ytterkanter:** Rocket Lab (över 25x) är inte en rimlig jämförelse för ett litet bolag som gör hårdvara. Förklara varför ett bolag ligger högt eller lågt.
- **Kursen ändras:** uppdatera kursen vid varje djupdykning. Med Börsdata sker det automatiskt.
- **Falsk precision:** svaret är ett spann, inte en siffra.

## Fil per bolag: `bolag/<namn>/vardering.json`
Innehåller kurs, aktier, kassa, skuld, försäljning de senaste 12 månaderna, scenarierna (tillväxt, år, multipel, nettokassa, aktier, sannolikhet, motivering), matrisens multiplar och jämförelsen. Webbsidan räknar fram resten. Mall: `$IH/mall-bolag/vardering.json`.
