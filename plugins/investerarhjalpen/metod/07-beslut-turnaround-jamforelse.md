# Beslut, turnaround-steg och jämförelse

## 1. Beslut efter första analysen
Varje `/bolagsanalys` slutar med **ett** av tre beslut. Beslutet och motiveringen skrivs i `status.json` och syns på webbsidan.

| Beslut | Kriterier |
|---|---|
| **Bevaka** | Checklistan ger ≥ 12 poäng **och** minst 2 A-påståenden som bär tesen **och** efterfrågan pekar uppåt (metod 16). Röda flaggor sänker poängen och skrivs ut, men stänger inte ute bolaget (min-strategi.md) |
| **Avvakta** | Intressant men något avgörande saknas: en rapport, finansiering, en kundbekräftelse. Ange **vad** som måste hända och **när** det ska kollas igen |
| **Kasta** | Allvarliga problem: misstanke om oegentligheter, ingen plan för finansieringen, ledning som säljer stort, efterfrågan som tydligt försvinner, ett 🚩 i löftesrevisionen, eller checklistan under 10 poäng |

Kastade bolag sparas i `kastade.md` med datum och skäl. På så sätt:
- analyserar vi inte samma bolag igen i onödan
- kan vi gå tillbaka och se om beslutet var rätt, vilket gör att du lär dig av det
- tas bolaget upp igen om något grundläggande ändras, till exempel ny ledning eller ny finansiering

## 2. Turnaround-stegen: var står bolaget?
| Steg | Namn | Kännetecken (mätbara) |
|---|---|---|
| 1 | **Kris** | Fallande omsättning, stora förluster, kassan tar slut, ledningsbyten |
| 2 | **Stabilisering** | Kostnaderna nere, finansiering säkrad 12+ månader framåt, fokus (bolaget säljer eller lägger ner sidoverksamheter) |
| 3 | **Kommersiellt genombrott** | Återkommande kunder, ramavtal, orderingång större än omsättning, första större ordrar |
| 4 | **Lönsamhet** | Positivt rörelseresultat och kassaflöde **över ett helt år**, och inget behov av emissioner |
| 5 | **Uppvärdering** | Analytiker och fonder upptäcker bolaget och värderingen stiger. Informationsövertaget är borta |

Det största värdet brukar skapas i övergången **steg 2 → 4**. Där vill vi vara.

För varje bevakat bolag anges:
- **nuvarande steg** och belägg
- **milstolpar kvar** till nästa steg, till exempel "positivt kassaflöde ett helt år" eller "första avropet under ramavtalet"
- **bedömd tid** till nästa steg. Bolagets egen tidplan justeras med löftesrevisionens precision. Om bolaget brukar vara ett kvartal sent lägger vi på ett kvartal.

## 3. Jämförelse med liknande bolag
Välj 3–5 bolag som liknar det vi analyserar: samma bransch eller affärsmodell, helst noterade i Norden eller Europa. Jämför:

| Mått | Varför |
|---|---|
| Börsvärde och EV | Storlek |
| Omsättningstillväxt (senaste 12 mån) | Fart |
| Bruttomarginal och rörelsemarginal | Hur lönsam affären kan bli |
| EV/S (värdering mot omsättning) | Hur mycket marknaden betalar per krona försäljning |
| Kassa / burn rate | Risken för nyemission |
| Turnaround-steg | Var de andra bolagen står |

Frågan att besvara: **om bolaget når nästa steg, vad betalar marknaden då för liknande bolag?** Det ger ett grovt spann för hur mycket värderingen kan förändras. Det är aldrig en riktkurs eller ett råd.

Utan Börsdata hämtas siffrorna ur bolagens rapporter, vilket tar längre tid. Med Börsdata Pro går det snabbt.
