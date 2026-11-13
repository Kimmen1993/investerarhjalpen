# Marknaden uppifrån – hur stort kan bolaget bli?

Pipelinen (metod 12) ser bara det som syns i dag. För ett turnaround-bolag är det fel tak. Den här metoden börjar **uppifrån**: hur mycket ska världen lägga på det bolaget säljer, vilka konkurrerar om pengarna, och hur stor andel är rimlig för just det här bolaget? Därefter vägs svaret ihop med pipelinen och tratten. Storfondernas modeller är byggda för stora, likvida bolag. Det här är vår egen version för små bolag på väg att växa.

## Ordningen
1. **Temat och marknaden** (`teman/<tema>.md`)
   - Räkna i **fysiska enheter** och beslutade pengar, inte i marknadsrapporternas spretiga dollarbelopp. Exempel: antal satelliter × andel med produkten × värde per enhet.
   - Tre nivåer (låg, mitten, hög), år för år i 5 år, gärna med en utblick mot 10 år.
   - **Kalibrera** så att bolagets försäljning i dag ger en rimlig andel av dagens marknad. Om andelen blir orimligt hög är marknaden underskattad.
2. **Regioner:** hur stor del av marknaden finns i Europa, Nordamerika, Asien, Mellanöstern och övriga världen, och vilken **tillgång** har bolaget i varje region?
   - Geopolitik: ett svenskt eller europeiskt bolag utan amerikanska exportregler (ITAR) jämfört med amerikanska eller kinesiska leverantörer
   - Krav på lokal tillverkning
   - Suveränitet
   - Befintliga referenskunder
3. **Konkurrenterna:** vem finns i varje region, vad är deras styrka, och vad gör bolaget unikt? Svenska bolag rankas ofta högt, men bara om det finns substans: flight heritage, certifieringar och kunder.
4. **Andelen per region och scenario** (golv, förväntat, starkt, dröm). Andelen byggs upp från dagens andel. **Ett etablerat bolag med stora referenskunder vinner oftare** när nya länder och kunder sätter igång, och det motiverar en stigande andel.
5. **Tratten** ur kundregistret: nya kundrelationer per år × hur stor andel som blir kontrakt × intäkt per konverterad kund × livslängd. Den fångar affärer som inte syns ännu.
6. **Väg ihop:** uppifrån (marknad × andel) jämfört med nerifrån (pipeline + tratt). Ger de ungefär samma svar är prognosen mer trovärdig. Om de skiljer sig mycket: ta reda på varför.
7. **Värdera framåt:** år X värderar marknaden bolaget på förväntad försäljning år X+2, gånger en framåtmultipel. Räkna om till dagens värde med avkastningskravet.
8. **"Vad måste vara sant?"** Skriv 3–5 punkter för det starka scenariot. De blir **signalerna vi letar efter** i dagskollen och djupdykningen.
9. **Känslighet:** visa kr per aktie för marknadens storlek × bolagets andel. Det är de två faktorer som betyder mest.

## Filer
- `teman/<tema>.md`: marknadens drivkrafter, storlek, regioner och konkurrenter, med källor
- `bolag/<namn>/marknadsmodell.json`: indata. Mall: Unibap
- `verktyg/marknad.py`: räknar fram resultatet (körs automatiskt av `bygg_sida.py`)

## Fällor
- **Dubbel optimism:** stor marknad × hög andel × hög multipel samtidigt. Därför använder det starka scenariot mellannivån för marknaden. Bara drömscenariot använder den höga nivån.
- **Marknadsrapporter:** många är betalda pressmeddelanden utan redovisad metod. Använd dem bara som rimlighetskontroll.
- **Kalibreringen glöms bort:** stämmer inte dagens andel med bolagets faktiska försäljning, så är modellen fel från början.
