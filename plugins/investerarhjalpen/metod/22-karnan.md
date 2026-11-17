# Kärnspåret – kvalitet och pris för lönsamma bolag

Bolag i spåret **Kärna** tjänar redan pengar. Frågan är inte om de överlever, utan **hur bra bolaget är** och **om priset är rimligt**. Svaret står i rutan **Kvalitet och pris** på bolagssidan. Allt räknas fram ur bolagets egna årssiffror, utan AI, med samma gränser varje gång.

Rutan visar:
1. **Kvalitetsbetyget** A–D. Sex delar med 0–2 poäng var.
2. **Priset nu jämfört med bolagets egen historik.** Är aktien billigare eller dyrare än den brukar vara?
3. **Temahävstången.** Finns det en liten nisch i bolaget som kan lyfta hela affären?
4. **Kvalitetslinserna:** Buffett och Munger, Terry Smith, Graham, Lynch, Piotroski och utdelning. Varje punkt bockas av ur siffrorna.
5. **Årssiffrorna** år för år.

Investerarpanelen (metod 18) är tolkningen i ord. Linserna här är samma filosofier som siffror. Använd båda. Om de inte stämmer överens, ta reda på varför.

## Varifrån kommer siffrorna?

Skriptet `verktyg/arsdata.py` hämtar upp till tio år och sparar dem i `bolag/<namn>/arsdata.json`. Källan väljs i den här ordningen:

| Ordning | Källa | Kostnad | Gäller | Skript |
|---|---|---|---|---|
| 1 | **Börsdata**, om användaren har slagit på det | Eget medlemskap | Alla nordiska bolag, 10–20 år | `borsdata.py` |
| 2 | **ESEF**: bolagens officiella årsredovisningar i maskinläsbar form, via det öppna registret filings.xbrl.org | Gratis | Bolag på huvudlistan i EU, från ca 2019 | `esef.py` |
| 3 | **Årsredovisningar som Claude läser** och sparar med `"kalla": "rapport"` | Gratis, men AI-tokens | Alla bolag, även First North | – |

- Det som finns i **ESEF** har bevisnivå A. Det är bolagets egen reviderade siffra.
- Bolag på **First North och Spotlight** lämnar inte ESEF. För dem läser Claude flerårsöversikten i den senaste årsredovisningen och lägger till raderna med `"kalla": "rapport"`.
- **Rättelser:** saknas ett värde i källan (ofta låneskulder, som bolagen redovisar med egna begrepp), skrivs det in för hand under `"rattelser"` i `arsdata.json`, till exempel `{"2024": {"lan": 145.0}}`. Källan skrivs i `kallor.md`. Rättelser skrivs aldrig över av skripten.
- **Kurser:** årsslutskurserna hämtas gratis från Yahoo och justeras för aktiesplittar. Siffror ur äldre årsredovisningar räknas om till dagens antal aktier.
- **Valuta:** allt räknas i bolagets rapportvaluta, till exempel danska kronor för Novo Nordisk. Om kursen anges i en annan valuta än rapporterna räknas den om med växelkursen vid varje årsslut (gratis från Yahoo, till exempel EURSEK). Det gäller till exempel NYAB, som redovisar i euro men handlas i kronor.

**Kör:** `python3 -I "$IH/verktyg/arsdata.py" <bolagsmapp>`, eller `--karna` för alla kärnbolag. Gör det vid bolagsanalysen, när en årsredovisning har kommit (februari–april) och vid djupdykningen. Bolagets LEI-kod (identitetsnumret i registret) hittas automatiskt och sparas i `kallor_bevakning.lei`. Om sökningen inte hittar rätt bolag visar `python3 -I "$IH/verktyg/esef.py" <namn>` koderna, så att rätt kod kan skrivas in för hand.

### Börsdata senare
Kopplingen är förberedd i `verktyg/borsdata.py` och avstängd som standard. När den slås på hämtar den årssiffror, kvartalssiffror och kurser i samma format, så resten av verktyget fungerar likadant. Gör så här:
1. Skaffa en egen API-nyckel hos Börsdata.
2. Spara nyckeln själv i datamappen, i `privat/borsdata.json`: `{"api_nyckel": "..."}`. Claude skriver aldrig in nyckeln.
3. Sätt `"datakallor": {"borsdata": true}` i `installningar.json`.
4. Testa med `python3 -I "$IH/verktyg/borsdata.py" --testa NOVO-B.CO`.

**Börsdatas villkor:** data får bara användas för egen analys. Den får inte delas med andra eller visas på en sida som andra ser. Varje användare behöver alltså ett eget konto. Slutsatser, till exempel ett betyg, får delas med Börsdata som källa.

## Nyckeltalen år för år

| Nyckeltal | Så räknas det |
|---|---|
| Rörelsemarginal | Rörelseresultat ÷ försäljning |
| Bruttomarginal | Bruttoresultat ÷ försäljning. Saknas för bolag som inte redovisar bruttoresultat |
| Avkastning på sysselsatt kapital (ROCE) | Rörelseresultat ÷ (tillgångar − kortfristiga skulder). Saknas de kortfristiga skulderna används eget kapital + räntebärande skulder |
| Avkastning på eget kapital (ROE) | Vinst ÷ eget kapital (snitt av årets början och slut) |
| Fritt kassaflöde | Kassaflöde från den löpande verksamheten − investeringar i anläggningar och immateriella tillgångar |
| Kassaflödeskonvertering | Fritt kassaflöde ÷ vinst |
| Nettoskuld | Lån + leasingskulder − kassa. Saknas om lånen inte finns i källan |
| P/E vid årets slut | Årsslutskurs ÷ vinst per aktie |
| EV/EBIT | (Börsvärde + nettoskuld) ÷ rörelseresultat |

**Att tänka på:** med leasingskulder (IFRS 16) räknas en del av hyrorna som finansiering. Då blir det fria kassaflödet något för högt, och konverteringen kan bli över 100 %. Det gäller till exempel mjukvaru- och tjänstebolag med många hyrda kontor.

## Kvalitetsbetyget A–D

Varje del ger 0–2 poäng, högst 12 poäng totalt. Saknas data för en del räknas betyget på de delar som finns, omräknat till 12. Finns färre än fyra delar blir betyget **?**.

| Del | Frågan | 2 poäng | 1 poäng |
|---|---|---|---|
| **Lönsamhet** | Tjänar bolaget mycket på pengarna som är insatta i verksamheten? | Avkastning på sysselsatt kapital i snitt minst 20 % | Minst 12 % |
| **Stabilitet** | Går det med vinst varje år, utan stora ras? | Vinst alla år och högst ett år då rörelseresultatet föll mer än 10 % | Vinst alla år |
| **Kassaflöde** | Blir vinsten riktiga pengar på kontot? | Kassaflödeskonvertering i snitt minst 90 % | Minst 60 % |
| **Balans** | Klarar bolaget en kris utan att låna eller ge ut aktier? | Nettokassa eller nettoskuld under 1 × rörelseresultatet | Under 3 ×. Saknas lånen används soliditeten: 2 poäng från 40 %, 1 poäng från 25 % |
| **Tillväxt** | Växer försäljningen? | I snitt minst 10 % per år | Minst 4 % |
| **Ägarvänlighet** | Får ägarna del av pengarna utan att spädas ut? | Antalet aktier har ökat högst 2 % och utdelning eller återköp varje år | Ett av de två |

| Betyg | Poäng | Betyder |
|---|---|---|
| **A** | 10–12 | Hög kvalitet |
| **B** | 7–9 | God kvalitet |
| **C** | 4–6 | Blandad kvalitet |
| **D** | 0–3 | Låg kvalitet. Passar kanske bättre i spåret Vändning |

Betyget beskriver **bolaget**, inte aktien. Ett A-bolag kan vara dyrt, och ett C-bolag kan vara billigt av goda skäl.

## Priset jämfört med bolagets egen historik

Tre mått jämförs med **medianen** (mittvärdet) av bolagets egna år:
- P/E-talet
- EV/EBIT
- fritt kassaflöde i procent av börsvärdet

Måttet räknas med dagens kurs och siffrorna för det senaste helåret.

| Läge | Gräns |
|---|---|
| Billigare än vanligt | Under 0,8 × medianen (för kassaflödet: över 1,25 ×) |
| Ungefär som vanligt | Däremellan |
| Dyrare än vanligt | Över 1,2 × medianen (för kassaflödet: under 0,83 ×) |

När två eller tre mått säger samma sak blir det sammanfattningen. Annars står det "spretigt".

**Fallgropen:** ett P/E som är lägre än vanligt kan betyda att marknaden väntar sig att vinsten faller. Kolla alltid nyheterna, pelarna och vad bolaget säger om framtiden innan slutsatsen dras. Det är metod 14: väg linserna.

## Kvalitetslinserna

Samma filosofier som i investerarpanelen, men som siffror som bockas av:
- ✓ uppfyllt
- ✗ inte uppfyllt
- – går inte att avgöra

| Lins | Punkter |
|---|---|
| **Buffett och Munger** | Avkastning på eget kapital över 15 % minst 7 av 10 år · vinsten per aktie växer · nettoskuld under 2 × rörelseresultatet · antalet aktier har ökat högst 5 % |
| **Terry Smith** | Avkastning på sysselsatt kapital i snitt över 20 % · bruttomarginal över 40 % · kassaflödeskonvertering över 90 % · fritt kassaflöde i procent av börsvärdet (visas, jämförs med räntan) |
| **Benjamin Graham** | Vinst varje år · utdelning varje år · P/E under 15 på snittvinsten för tre år · P/E × P/B under 22,5 · omsättningstillgångar minst dubbla kortfristiga skulder |
| **Peter Lynch** | PEG-tal under 2, där under 1 är billigt (bygger på den historiska vinsttillväxten) · försäljningen växer · nettokassa eller nettoskuld under 1 × rörelseresultatet |
| **Piotroskis F-poäng** | Nio test av om bolaget blev starkare än året innan: vinst, kassaflöde, högre avkastning, kassaflöde större än vinst, lägre skuld, bättre betalningsförmåga, inga nya aktier, högre marginal och mer försäljning per krona i tillgångar. 8–9 är starkt, 0–2 svagt. Test som saknar data räknas inte |
| **Utdelning** | År med utdelning · år i rad som utdelningen har höjts eller hållits oförändrad · andel av vinsten som delas ut · direktavkastning |

## Investmentbolag: substansvärdet i stället för betyget

Investmentbolag och andra tillgångsbolag (Lynchkategori `tillgang`) tjänar pengar på att innehaven stiger i värde. Vinsten svänger med börsen och säger lite om kvaliteten. De får därför inget kvalitetsbetyg. Rutan heter i stället **Substansvärde och pris** och visar:
- **Substansvärdet per aktie:** vad innehaven minus skulderna är värda per aktie.
- **Premie eller rabatt:** kursen jämfört med substansvärdet, nu och vid varje årsslut.
- **Läget mot historiken:** mer än 10 procentenheter från mittvärdet räknas som större eller mindre rabatt än vanligt.
- **Substansvärdets utveckling** per aktie och år.

Substansvärdet per år skrivs i `arsdata.json` (`substansvarde` och `substansvarde_per_aktie`). Investmentbolag redovisar det varje kvartal. Det senaste skrivs därför i `karna.json` vid varje rapport, så att premien räknas mot dagens värde och inte mot årsskiftets:

```json
{"substans_senaste": {"datum": "2026-09-30", "per_aktie": 8.17, "kalla": "Delårsrapport Q3 2026"}}
```

## Temahävstången

Ibland gömmer sig en liten, snabbväxande nisch i ett stort bolag, till exempel ett försvarsbolag med en drönaraffär eller ett industribolag med en del inom kärnkraft. Temahävstången räknar på hur mycket nischen kan lyfta hela bolaget. Den skrivs för hand i `bolag/<namn>/karna.json`:

```json
{"temahavstang": {"nisch": "…", "tema": "…", "andel_nu_pct": 8, "tillvaxt_nisch_pct": 35,
  "tillvaxt_ovrigt_pct": 4, "ar": 5, "niva": "B", "skal": "Varför nischen kan växa, med källa."}}
```

Skriptet räknar fram hur stor andel nischen är efter så många år, hur fort hela bolaget då växer och hur många procentenheter per år nischen lyfter. Andelen ska komma från bolagets egen redovisning (bevisnivå A), eller vara en tydlig uppskattning med bevisnivå. Tillväxttakten är ett antagande. Hämta den gärna från temat (`teman/`) eller trendradarn. Det är ett räkneexempel, ingen prognos.

## När rutan uppdateras
- `bygg_sida.py` räknar om allt vid varje bygge med dagens kurs. Det kostar ingenting.
- `arsdata.py` körs när en ny årsredovisning har kommit, och vid djupdykningen.
- Byte av spår (metod 18) gör att rutan visas eller försvinner. Redo-poängen visas bara för Vändning, och kvalitetsbetyget bara för Kärna.
