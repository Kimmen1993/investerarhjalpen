# Bolagsjakt – så hittar vi nästa bolag, och vet när det är läge

Målet är **3–5 riktigt bra case per år**, hittade tidigt och följda tills de närmar sig vändningen. Det kräver en tratt som är **bred och billig i början och smal och grundlig på slutet**. Är den för smal hittar vi inget; är den för bred drunknar vi.

## Tratten (ungefärliga antal per år)
| Steg | Vad | Hur | Kostnad | Antal |
|---|---|---|---|---|
| 0. Universum | Svenska noterade bolag (Nasdaq, First North, Spotlight, NGM), även nordiska | Alla som syns i MFN och FI | – | ca 700 |
| 1. **Signalradar** (dagligen, automatiskt) | Bolag med tidiga signaler: första order, ramavtal, strategiska partners, nya ägare, insiderköp i kluster | `verktyg/signalradar.py`, gratis och utan AI | Gratis | ca 100–150 med någon signal |
| 2. **Triage** (varje söndag, högst 5 bolag) | 10 minuter per bolag: storlek, affär, kassa, röda flaggor, tema | Claude, kort | Liten | ca 50–80 per år |
| 3. **Radar** | De som klarar triagen följs passivt, och signalerna samlas | `radar/radar.json` och sidan | Gratis | 20–40 åt gången |
| 4. **Bolagsanalys** | Full analys: löftesrevision, kundregister, pipeline, marknad, linser och värdering | `/bolagsanalys` | Större | ca 10–15 per år |
| 5. **Bevakning** | Morgonkoll och djupdykning varannan vecka | Automatiskt | Mellan | 6–10 åt gången |
| 6. **Läge att ta ställning** | När redo-poängen är hög | användaren beslutar | – | 3–5 per år |

## Parametrar
**Steg 1, signalradarn (bred, med avsikt):** inga filter på bransch eller nyckeltal. Bara signaler:
| Signal | Exempel | Poäng |
|---|---|---|
| Första order, genombrott, kvalificering eller pilot med en större kund | "första order", "first order", "qualification", "pilot", "design win" | +3 |
| Strategiskt samarbete eller partnerskap | "strategiskt samarbete", "strategic partnership", "joins forces" | +3 |
| Ramavtal eller större order | "ramavtal", "framework agreement", "order värd", "contract" | +2 |
| Insiderköp i kluster | 2 eller fler personer köper, eller köp för minst 0,5 MSEK på 14 dagar | +3 |
| Ny kunnig ägare | Riktad emission till en namngiven strategisk investerare eller industriell partner | +2 |
| Ny vd eller ny styrelseordförande | | +1 |
| **Fondköp** (en gång per kvartal) | Aktivt förvaltade svenska fonder köper in sig: 3 nya fondägare eller 5 fler köpare än säljare ger +3, 2 nya eller 3 fler köpare +2. +1 extra om högst 5 aktiva fonder ägde bolaget innan. Nynoterade bolag +2 | +2 till +4 |
| **Fonder lämnar** | 4 fonder säljer allt, eller 5 fler säljare än köpare | −2 |
| **Negativa signaler** | Vinstvarning, företrädesemission med stor rabatt, rekonstruktion, insiders säljer | −3 |

Signalerna summeras över 90 dagar, och nyare väger tyngre.

**Om fondsignalerna:** de räknas av `verktyg/fonder.py` ur Finansinspektionens kvartalsdata och läses in av radarn. Bara aktivt förvaltade fonder räknas. Indexfonder köper när ett bolag kommer in i ett index, och generations-, pensions- och blandfonder köper efter en plan, så ingen av dem visar övertygelse. In- och utflöden i fonderna räknas bort. Bolag som redan ägs av fler än 30 aktiva fonder sorteras bort, liksom byten av ISIN, emissionsrätter och obligationer. Datan är några månader gammal när den kommer, så fondsignalen är en bekräftelse på att proffsen har hittat bolaget, inte ett tidigt tips i sig. Störst värde har den tillsammans med andra signaler, som insiderköp eller en första order. De största bolagen (som Saab och Ericsson) sorteras bort med en lista som byggs ut vid triagen.

**Steg 2, triagen (snävare):**
- **Storlek:** börsvärde ca 50 MSEK – 5 mdr. Större bolag bara om vändningen är tydlig (metod 02).
- **Affären går att förstå:** vad säljer bolaget och till vem, på en mening.
- **Kassa:** pengarna räcker 12 månader eller mer, eller finansieringen är löst.
- **Inga röda flaggor** (metod 02 och 04).
- **Tema:** helst ett tema i fas 1–2 (metod 06), men inget krav.
- Resultatet blir **Radar** (följ passivt), **Bolagsanalys** (värt full analys) eller **Bort** (med skäl).

**Steg 4, bolagsanalysen:** hela metoden med beslutet Bevaka, Avvakta eller Kasta (metod 07).

## Redo-poäng: när är det läge att ta ställning?
Att vara tidig betyder **att börja följa tidigt**, inte att köpa tidigt. Redo-poängen visar när riskerna har minskat medan uppsidan finns kvar. Varje punkt ger 0, 1 eller 2 poäng (max 20):
1. **Turnaround-steg:** steg 3 och på väg mot 4. Milstolparna börjar uppfyllas.
2. **Finansiering:** kassan räcker 18 månader eller mer, eller en emission är nyss gjord, så att utspädningen redan är tagen.
3. **Marginal och kassaflöde:** förbättring 2 kvartal i rad eller mer.
4. **Kunder kommer tillbaka:** återkommande ordrar, och fler tester blir kontrakt.
5. **Signalindex:** stigande.
6. **Insiders:** köper och säljer inte.
7. **Prissättning:** den samlade bedömningen, omräknad till dagens värde, ligger tydligt över kursen. Marknaden räknar med lite.
8. **Ledningen levererar:** leveransgrad 70 % eller mer.
9. **Kursen bekräftar:** kursen har börjat vända upp från en bas. Ingen jakt på toppar.
10. **Likviditet:** aktien handlas tillräckligt för att det ska gå att köpa och sälja.

| Poäng | Läge |
|---|---|
| 15–20 | **Läge att ta ställning.** användaren beslutar; ingen rådgivning |
| 10–14 | **Följ noga.** Vänta på de saknade punkterna |
| under 10 | **För tidigt** (eller för sent: titta på punkt 7 och 9) |

## Skydd mot fel
- **Basfrekvens:** de flesta "tidiga signaler" leder ingenstans. Därför följer vi länge innan vi agerar.
- **Kastade bolag sparas** med skäl, och följs upp en gång per kvartal: hade vi rätt att kasta dem?
- **Temajakt:** ett hett tema gör inte ett bolag bra; lönsamheten avgör (lärdom från de historiska casen).
- **Kvalitet före kvantitet:** hellre 3 bra case än 10 halvbra.
