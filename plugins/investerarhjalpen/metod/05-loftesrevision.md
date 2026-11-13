# Löftesrevision – håller ledningen vad den lovar?

Det här är ofta den **mest värdefulla** analysen av ett bolag. En ledning som har hållit vad den lovat tidigare kommer sannolikt att göra det igen, och tvärtom. Det är också en analys som nästan ingen privatinvesterare gör, eftersom den kräver att man läser 2–3 års material.

## 1. Samla in löftena
Gå igenom **2–3 år** bakåt, eller längre om bolaget är i en vändning:
- vd-ord i kvartalsrapporter och årsredovisningar
- **prospekt och memorandum** vid emissioner (här står ofta de mest konkreta målen, eftersom bolaget behöver sälja in emissionen)
- kapitalmarknadsdagar och investerarpresentationer
- pressmeddelanden ("förväntas", "planeras", "under H2")
- intervjuer och webbsändningar (Börsvärlden, Placera, Redeye, Analysguiden, poddar)

Ett **löfte** är något som går att mäta: ett mål med siffra, en produkt som ska lanseras, en order, ett datum, ett lönsamhetsmål, ett tillstånd eller ett godkännande. Vaga ord som "spännande år framöver" räknas inte. Skriv dock upp hur ofta de förekommer.

## 2. Klassa utfallet
| Symbol | Kategori | Betyder |
|---|---|---|
| ✅ | **I tid** | Levererat senast vid utlovad tidpunkt |
| 🕐 | **Försenat** | Levererat, men sent. Ange hur sent |
| ⏳ | **Inte förfallet** | Deadline har inte passerat |
| ⚠️ | **Missat, rimlig förklaring** | Inte levererat, men av en verifierbar extern orsak (exportlicens, kundens satellit försenad, pandemi) som bolaget **själv berättade om i tid** |
| ❌ | **Missat, svag förklaring** | Inte levererat, och förklaringen saknas, kom först i efterhand eller går inte att kontrollera |
| ❔ | **Slutade nämnas** | Målet följs aldrig upp och utfallet går inte att se. Räknas inte i leveransgraden men redovisas separat. Många ❔ är ett mönster att väga in, och om det gäller ett *viktigt* mål blir det 🚩 |
| 🚩 | **Vilseledande** | Målet togs bort tyst, formulerades om utan att det sades, siffrorna går inte ihop, eller ledningen sålde aktier strax efter ett optimistiskt uttalande |

**Om ordet "ljug":** vi kan nästan aldrig bevisa avsikt. Därför skriver vi 🚩 och beskriver vad som faktiskt hände, till exempel "målet om lönsamhet 2024 nämns inte i någon rapport efter Q2 2024". Läsaren får dra slutsatsen. Det skyddar mot att vi själva sprider rykten.

## 3. Räkna fram mått
- **Leveransgrad** = (✅ + 🕐) / alla förfallna löften
- **Precision** = ✅ / (✅ + 🕐), det vill säga hur ofta bolaget levererar i tid när det väl levererar
- **Snittförsening** för 🕐, i månader
- **Antal 🚩** – ett enda kan väga tyngre än allt annat
- **Trend:** blir bolaget bättre eller sämre på att hålla löften över tid? En ny vd kan vända trenden; räkna då gärna före och efter separat.

Ungefärlig läsning:

| Läge | Bedömning |
|---|---|
| Leveransgrad > 80 %, inga 🚩 | Pålitlig ledning |
| Leveransgrad 50–80 % | Normalt för små tillväxtbolag. Räkna med förseningar i allt bolaget lovar |
| Leveransgrad < 50 % eller ett 🚩 | Lita inte på framåtblickande uttalanden. Bara siffror som redan finns räknas |

## 4. Läs tonen över tid
Jämför vd-orden kvartal för kvartal:
- Blir orden mer eller mindre konkreta?
- Försvinner ett tidigare huvudtema utan förklaring?
- Flyttas samma mål fram år efter år ("nästa år")?

## 5. Vad vi gör med resultatet
Leveransgraden avgör **hur mycket vi litar på bolagets egna prognoser** i caset. En pålitlig ledning gör att B-påståenden som bygger på bolagets egna ord väger tyngre. En opålitlig ledning gör att bara A-siffror som redan har levererats räknas.

## Fil per bolag: `bolag/<namn>/loften.md`
```
# Löftesrevision – <bolag>
Period: <från> – <till>. Senast uppdaterad: <datum>.

## Sammanfattning
Leveransgrad X % (n av m) · Precision Y % · Snittförsening Z mån · 🚩: n · Trend: …

## Löften
| # | Datum lovat | Källa | Löfte | Deadline | Utfall | Datum utfall | Kategori | Förklaring/kommentar |
|---|---|---|---|---|---|---|---|---|

## Tonen över tid
Kort, per år.
```
