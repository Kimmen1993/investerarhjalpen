# Pipeline och framtid – räkna på det som kommer, inte det som redan är känt

Det som redan är officiellt (signerade avtal, rapporterade siffror) är oftast redan inprisat. Informationsövertaget finns i **det som är på väg**: affärer som syns i signaler innan de blir pressmeddelanden. Den här metoden gör de signalerna till en prognos och en värdering.

**Flödet:** informationsövertag (signaler) → möjliga affärer → prognos → värdering → jämför med priset och med liknande historiska case.

## 1. Registret över möjliga affärer (`bolag/<namn>/mojligheter.json`)
Varje möjlig affär har:
| Fält | Vad |
|---|---|
| `namn`, `kund` | Till exempel "Altair-satelliterna 11–50", Orbitworks |
| `status` | `signal` (spår finns), `kvalificering` (kunden testar), `forhandling` (tydliga tecken på upphandling), `signerat` (avtal finns) |
| `signaler` | Lista med datum, signal, källa och bevisnivå (A/B/C/?) |
| `intakt_msek` | Spann [lägst, högst] för hela affären: antal enheter × pris per enhet. Visa uträkningen i `berakning` |
| `ar` | [startår, slutår]: när intäkterna kan komma |
| `sannolikhet` | 0–1. Se tabellen nedan |
| `inprisat` | Bedömning: syns affären redan i bolagets officiella kommunikation? (ja / delvis / nej) |

### Sannolikhet: utgångsläge efter status, justeras med signaler
| Status | Utgångsläge | Höj om | Sänk om |
|---|---|---|---|
| Signal | 5–20 % | Flera oberoende källor, kunden har finansiering, tidsplan finns | Bara en källa, kunden saknar pengar |
| Kvalificering | 20–40 % | Testet går bra, kunden pratar offentligt, återkommande ordrar | Tyst länge, konkurrent nämns |
| Förhandling | 40–70 % | Upphandling pågår, kunden bekräftar leverantörsval | Förseningar, budgetbesked |
| Signerat | 90–100 % för minimivolym | – | Exportlicens, kunden i kris |

Varje ändring av sannolikheten skrivs i `logg.md` med skälet. Då kan vi i efterhand se om vi bedömde rätt.

## 2. Prognosen
Försäljning år X = **löpande affär** (små kunder, mjukvara, service) + **signerat** + Σ (sannolikhet × intäkt för år X) för alla möjliga affärer. Intäkten fördelas jämnt över affärens år. Tre banor:
- **Svag:** löpande affär utan tillväxt + signerat. Inga nya affärer.
- **Förväntad:** löpande affär med måttlig tillväxt + signerat + varje affär × sannolikheten × mitten av spannet.
- **Stark:** löpande affär med god tillväxt + signerat + varje affär × en högre sannolikhet (× 1,6, max 100 %) × den övre delen av spannet.

Skriptet `verktyg/pipeline.py` räknar fram prognosen och signalindexet och sparar dem i `mojligheter.json` under `resultat`.

## 3. Vad har marknaden redan räknat med?
- **Golv:** värdet om bara det signerade och den löpande affären blir av, alltså den svaga banan × en låg multipel.
- **Pipelinevärde:** den förväntade banan × en normal multipel.
- **Dagens pris** ligger någonstans mellan dem. Andelen (pris − golv) / (pipelinevärde − golv) visar **ungefär hur stor del av pipelinen marknaden redan räknar med**.
- Låg andel och starka signaler: möjligt informationsövertag. Hög andel: mycket är redan betalt.

## 4. Signalindexet
Antalet nya signaler per kvartal, viktade efter bevisnivå (A = 3, B = 2, C = 1). Signalerna kan vara nya kunder som testar, kundernas offentliga uttalanden, mässor, rekryteringar, nya partners och upphandlingar. **Stigande index samtidigt som kursen står still** är precis det läge vi letar efter: fler aktörer intresserar sig innan resten av marknaden har sett det. Det är ingen garanti, men det är en tydlig signal att granska.

## 5. Liknande historiska case (`analoga-case.md`)
För bolag som gjort en liknande resa: vilka tidiga signaler fanns, när kom det första stora avtalet, när blev bolaget lönsamt, och hur rörde sig multipeln och kursen före och efter? Frågan är hur lång tid det brukar ta från första signal till omvärdering, och vad som var den avgörande signalen.

## Fällor
- **Önsketänkande:** varje affär måste ha minst en signal. Utan signal blir det ingen post.
- **Dubbelräkning:** en affär som blir signerad flyttas till signerat och tas bort som möjlighet.
- **Fel tid:** affärer tar nästan alltid längre tid. Använd löftesrevisionens precision för att skjuta fram tidsfönstret.
- **Insiderinformation:** bara offentliga signaler. Se metod 08.
