# Spår och investerarpanelen – vilken lins mäts bolaget mot?

Olika bolag ska mätas på olika sätt. Ett förlustbolag i en vändning blir underkänt av en kvalitetsinvesterare, och ett stabilt storbolag får noll på en vändningsskala. Båda bedömningarna stämmer, men de svarar på olika frågor. Därför har varje bolag **ett spår**, och det syns alltid vilket.

## Spåren

| Spår | För vilka bolag | Huvudbedömning | Visas som |
|---|---|---|---|
| **Vändning** | Bolag som ännu inte bär sig själva: turnarounds, tidig kommersialisering, kriser, biotech | Turnaround-steg 1–5, redo-poäng, fas 1/2 och löftesrevision (metod 02, 07, 15) | Trafikljus, steg och fas |
| **Kärna** | Lönsamma bolag som bär sig själva: stabila storbolag, kvalitetsbolag, lönsamma tillväxtbolag | Kvalitet, värdering mot egen historik och om vallgraven håller (panelens Buffett, Smith, Graham och Lynch) | Trafikljus och Lynchkategori |

(Ett tredje spår, **Fond**, kommer senare och gäller fonder, inte bolag.)

### Regler
1. **Exakt ett spår per bolag.** Det står i `status.json` som `"spar": "vandning"` eller `"karna"`.
2. **Bedömningen räknas bara inom spåret.** Redo-poäng och turnaround-steg visas bara för Vändning. Ett kärnbolag får inget turnaround-steg.
3. **Verktyget föreslår, användaren bestämmer.** Ett nytt spår sparas med `"spar_bekraftad": false` och visas som "föreslaget" tills användaren har sagt ja. Då sätts `true`.
4. **Byte av spår är en händelse.** Ett vändningsbolag som når steg 5 (stabil lönsamhet) kan flyttas till Kärna, och ett kärnbolag i kris kan flyttas till Vändning. Föreslå bytet, vänta på ja och skriv in det i `journal.md` och `logg.md` med datum och skäl. Byt aldrig tyst.
5. **Osäkert?** Välj det spår vars frågor bäst avgör om bolaget blir en bra investering. Går bolaget med förlust och behöver bevisa något: Vändning. Tjänar det pengar och frågan är hur länge och till vilket pris: Kärna.

## Peter Lynchs sex kategorier

Varje bolag får också en Lynchkategori (`"lynch"` i `status.json`, med en mening i `"lynch_skal"`). Den säger vad man ska förvänta sig av aktien, och den används för att föreslå spår och för fördelningen i Min portfölj.

| Nyckel | Kategori | Kännetecken | Vad man kan vänta sig | Brukar höra till |
|---|---|---|---|---|
| `langsam` | Långsamväxare | Stort, moget bolag som växer ungefär som ekonomin, ofta hög utdelning | Utdelning, lite kursrörelse | Kärna |
| `stabil` | Stabil jätte | Stort, lönsamt bolag som växer ca 5–12 % per år | 30–50 % på några år om priset är rimligt, tål kriser bra | Kärna |
| `snabb` | Snabbväxare | Lönsamt bolag som växer över ca 15–20 % per år | Kan bli många gånger pengarna, men faller hårt när tillväxten stannar | Kärna |
| `cyklisk` | Cykliskt bolag | Vinsten följer konjunkturen (råvaror, bygg, bilar, varv) | Tajmingen är allt. Lågt P/E kan vara en varning nära toppen | Kärna eller Vändning |
| `tillgang` | Tillgångsbolag | Äger något som är värt mer än börsen tror (fastigheter, innehav, kassa) | Vinsten kommer när värdet blir synligt | Kärna |
| `turnaround` | Turnaround | Bolag i kris eller som ännu inte gått med vinst, men kan vända | Stor uppsida om vändningen lyckas, stor risk om den inte gör det | Vändning |

## Investerarpanelen

Panelen visar hur bolaget ser ut med kända investerares glasögon, **enligt deras publicerade filosofi**. Den är ett andra perspektiv och ändrar aldrig spårets huvudbedömning.

### Regler för panelen
- **Tolkning, aldrig citat.** Skriv "enligt Buffetts filosofi" eller "med Buffetts glasögon", aldrig "Buffett säger" eller påhittade citat. Investerarna har inte uttalat sig om bolaget.
- **Siffrorna kommer från bolagets data** med bevisnivå (A/B/C/?). Saknas en siffra: skriv "?" och vad som behövs för att ta reda på den. Gissa inte.
- **Samma checklista varje gång** (nedan), så att korten går att jämföra mellan bolag och över tid.
- **Väger tyngst** för spåret: Vändning → Lynch, Fisher och Blankaren. Kärna → Buffett, Smith, Graham, Lynch och Blankaren. De andra visas som "andra perspektiv".
- **Inga köp- eller säljråd.** "Passar filosofin" betyder bara hur väl bolaget matchar checklistan.
- **Passar filosofin:** `mycket` (de flesta punkter uppfylls), `delvis` (hälften eller kärnpunkterna med reservationer) eller `lite` (kärnpunkterna uppfylls inte).

### Kortets innehåll (`panel.json`)
För varje investerare: `passar`, `dom` (en mening på klarspråk), `gilla` (1–3 punkter), `ogilla` (1–3 punkter), `andra_sig` (vad som skulle få dem att ändra sig) och `siffror` (2–4 nyckeltal ur checklistan med värde och bevisnivå).

### Buffett och Munger: vallgraven
Kärnfråga: *Är det här ett utmärkt bolag till ett rimligt pris, som jag förstår och vill äga i tio år?*
- **Förståelse:** går affären att förklara enkelt, och går det att se ungefär var bolaget står om 10 år?
- **Vallgrav:** varumärke, kostnadsfördel, nätverkseffekt eller höga byteskostnader som skyddar vinsten.
- **Avkastning på kapitalet (ROIC eller ROE)** över ca 15 % i många år, utan hög skuld.
- **Stabil och stigande vinst** och fritt kassaflöde. Inga ständiga emissioner.
- **Ledning:** ärlig, äger aktier och använder pengarna klokt (återköp, utdelning eller lönsamma investeringar).
- **Pris:** rimligt i förhållande till kassaflödet. Hellre ett utmärkt bolag till ett okej pris än tvärtom.
- Typiskt nej: förlustbolag, emissioner, teknik som ändras snabbt, affärer man inte kan förutse.

### Peter Lynch: vilken sorts bolag, och är tillväxten billig?
Kärnfråga: *Vilken kategori är det, och stämmer berättelsen med siffrorna?*
- **Kategori** (tabellen ovan) och vad den betyder för förväntningarna.
- **Berättelsen på två minuter:** varför ska bolaget gå bättre, och vad måste hända?
- **PEG-tal** (P/E delat med tillväxten i procent): under 1 är billigt, över 2 är dyrt. Gäller lönsamma bolag.
- **Balansräkningen:** nettokassa eller låg skuld. För turnarounds: räcker kassan genom vändningen?
- **Lynchs plus:** tråkigt namn eller nisch som analytikerna inte följer, insiders som köper, bolaget köper tillbaka aktier, en produkt man själv ser användas.
- **Lynchs varningar:** "nästa stora grej", bolag som köper på sig mycket utanför kärnan, beroende av en enda kund.
- För turnarounds: vad gör att bolaget överlever, och vad är det konkreta vändningsbeviset?

### Philip Fisher: scuttlebutt och långsiktig tillväxt
Kärnfråga: *Har bolaget produkter och människor som kan få försäljningen att växa i många år, och vad säger kunder, leverantörer och konkurrenter?*
- **Marknad:** finns det utrymme för flera år av växande försäljning?
- **Nästa produkt:** satsar ledningen på det som ska bära försäljningen när dagens produkter mognar?
- **Forskning och säljorganisation:** ger utvecklingen resultat, och kan bolaget sälja?
- **Marginal:** tillräckligt hög och på väg upp?
- **Ledningen:** ärlig även när det går dåligt, med djup i organisationen.
- **Scuttlebutt:** vad säger kunderna, partnerna och konkurrenterna (kundregistret, nätverket, metod 08–09)?
- **Utspädning:** växer bolaget utan att ständigt behöva nya pengar som spär ut ägarna?

### Benjamin Graham: säkerhetsmarginalen
Kärnfråga: *Om jag har fel, hur illa kan det gå? Betalar jag mindre än vad bolaget är värt?*
- **P/E under ca 15** på snittvinsten de senaste åren.
- **P/E × P/B under ca 22,5** (P/B är priset delat med det egna kapitalet).
- **Stark balansräkning:** omsättningstillgångar minst dubbelt så stora som de kortfristiga skulderna, och låg långfristig skuld.
- **Vinst varje år** de senaste ca 10 åren och utdelning utan avbrott.
- **Storlek:** inte för litet bolag.
- Typiskt nej: alla förlustbolag och de flesta tillväxtbolag. Det är väntat, eftersom Graham letade efter billiga och trygga bolag.

### Terry Smith: köp bra bolag, betala inte för mycket, gör ingenting
Kärnfråga: *Är det ett kvalitetsbolag som omvandlar vinsten till riktiga pengar och kan återinvestera dem med hög avkastning?*
- **Hög avkastning på sysselsatt kapital (ROCE)** över ca 20 %.
- **Hög bruttomarginal**, ett tecken på prissättningsmakt.
- **Kassaflödeskonvertering:** hur stor del av vinsten som blir fritt kassaflöde (helst över ca 90 %).
- **Tillväxt** som kan återinvesteras med samma höga avkastning.
- **Låg skuld och lite förvärv** som grumlar siffrorna.
- **Pris:** fritt kassaflöde i förhållande till börsvärdet (FCF-avkastning) jämfört med räntan.
- Typiskt nej: cykliska bolag, banker och förlustbolag.

### Blankaren: vad kan gå fel?
En påhittad roll, ingen verklig person. Kärnfråga: *Om aktien halveras om ett år, vad var den troligaste orsaken?*
- Pengarna tar slut och nya aktier ges ut.
- Kunder eller ordrar som inte blir intäkter, eller intäkter som inte blir pengar på kontot.
- Redovisning som ser bättre ut än verkligheten (aktiverade kostnader, engångsposter, kundfordringar som växer).
- Ledningen lovar mer än den levererar (löftesrevisionen), eller säljer aktier.
- En konkurrent, teknik eller politik som gör produkten mindre värd.
- Värdering som redan räknar med att allt går bra.
- Blankaren bedöms omvänt: `mycket` betyder stora risker för ägarna. På sidan visas `gilla` som "Risker för dig som ägare" (rött), `ogilla` som "Det som skyddar dig" (grönt) och `andra_sig` som "Risken minskar om".

## När panelen tas fram
- **Bolagsanalys:** för nya bolag efter beslutet (Bevaka eller Avvakta).
- **Djupdykning:** korten ses över varje gång. Ändras `passar` för någon: skriv det i rapporten.
- **Fråga vidare:** på sidan öppnar knappen chatten med investerarens checklista. Där kan användaren ställa egna frågor.
