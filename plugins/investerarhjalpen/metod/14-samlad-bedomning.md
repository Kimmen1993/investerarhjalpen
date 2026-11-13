# Samlad bedömning – väg alla linser, lås dig inte vid en

Ingen enskild beräkning är "rätt". Varje lins ser något de andra missar. Vi lägger dem bredvid varandra, väger dem efter **datakvalitet och relevans** och tittar på var de **är överens och var de spretar**.

## Linserna
| Lins | Vad den fångar | Typisk svaghet | Utgångsvikt |
|---|---|---|---|
| Bolagets egna mål | Ledningens plan | Optimism; justera efter leveransgraden | 0,15 |
| Synliga affärer (pipeline) | Det vi kan belägga | Ser inte det som inte syns än | 0,15 |
| Synliga affärer + tratt | Nya kunder utifrån historiken | Förutsätter att historiken upprepar sig | 0,30 |
| Marknaden uppifrån | Hur stort det kan bli | Marknadens storlek är en uppskattning | 0,40 |
| Liknande historiska case | Hur det brukar gå i verkligheten | Inget case är helt lika | 0 tills gjord, sedan 0,15–0,25 |
| Analytikernas prognoser | Vad marknaden redan tror | Ofta betalda uppdragsanalyser | 0 tills hämtad, sedan 0,10 |

Vikterna anges i `marknadsmodell.json` under `metoder` och ska motiveras. **Höj** vikten för en lins med bättre data, till exempel A-källor, flera oberoende signaler eller lång historik. **Sänk** den om data är tunn eller bara bygger på antaganden.

## Så läser vi resultatet
- **Vägt resultat:** den samlade bedömningen per scenario.
- **Spridning (lägst–högst mellan linserna):** stor spridning betyder stor osäkerhet. Ta reda på *varför* linserna skiljer sig. Ofta finns svaret i en enda faktor, till exempel marknadens storlek.
- **Överens:** när 3 eller fler linser hamnar inom ±25 % av varandra är bedömningen robust.
- **Avvikare:** en lins som ligger långt från de andra är antingen fel, eller så ser den något de andra missar. Det kan vara just informationsövertaget, så undersök det innan linsen avfärdas.

## Stoppregel mot överanalys
- En ny lins eller mer data är värd att ta fram bara om den kan ändra det samlade resultatet **mer än ca 10 %**, eller flytta en viktig punkt under "måste vara sant".
- Ändrar den mindre: notera det och gå vidare.
- Mer data är bra **bara om den är trovärdig**. En C-källa med många siffror ska väga mindre än en A-källa med få.

## Var det används
- Sidan visar alla linser, vikterna, det vägda resultatet och spridningen under "Samlad bedömning".
- Värderingen år X räknas på det vägda resultatet.
- Djupdykningen ser över vikterna var tredje gång och när en ny lins tillkommer.
