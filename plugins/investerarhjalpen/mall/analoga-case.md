# Liknande historiska case

Bolag som har gjort, eller försökt göra, en resa liknande den vi letar efter. Syftet är att lära oss **hur det brukar gå i verkligheten**: hur snabbt försäljningen växer, när och varför multipeln stiger eller faller, och vad som avgör. Casen används också som en egen lins i den samlade bedömningen (metod 14).

*Första versionen 2026-11-13. Data från öppna källor (StockAnalysis, Yahoo, bolagens rapporter, Motley Fool, TradingView). Siffror som inte är kontrollerade mot årsredovisningar är markerade. Med Börsdata kan historiken göras exakt.*

## Översikt
| Case | Typ | Försäljning | Lönsamt? | Värdering | Utfall | Bevisnivå |
|---|---|---|---|---|---|---|
| **Invisio** (SE) | Försvar, utrustning för soldater | 593 → 1 810 MSEK 2021–2024 (**+45 %/år**) | Ja, EBIT ca 20–22 % | Hög; kursen 196 → 276 kr 2023–2024 | ✅ Lönsam tillväxt omvärderades | B |
| **MilDef** (SE) | Försvar, robust IT | Ca 470 → 1 200 MSEK 2021–2024 (≈ +37 %/år; årsfördelningen osäker), ca 2 050 MSEK 2025 med förvärv | Ja (inte detaljkontrollerat) | Börsvärde ca 2,6 mdr (mitten av 2024) → **9,8 mdr (mars 2025)** → 5,6 mdr (dec 2025) → ca 11–12 mdr (2026) | ✅ Omvärderades mycket snabbt när Europa rustade upp, men var mycket volatil | B/C |
| **AAC Clyde Space** (SE) | Rymd, småsatelliter | 81 → 409 MSEK 2019–2024 (**+38 %/år**), sedan 338 MSEK 2025 (−17 %) | **Nej**, förlust även 2025 | Ca 2–3x försäljningen 2026, börsvärde ca 0,9 mdr | ⚠️ **Tillväxt utan lönsamhet gav ingen omvärdering**; många emissioner | B (försäljning), C (emissioner) |
| **GomSpace** (DK) | Rymd, nanosatelliter | Stark tillväxt fram till ca 2018, sedan ett ras | Nej i många år; lönsam igen enligt senare rapporter | Ca 4,8x försäljningen 2026 | ⚠️ **En stor konstellationskund gick i konkurs** (ca 2019); kursen rasade och bolaget fick strukturera om | ? (ur minnet, ska kontrolleras) |
| **Rocket Lab** (US) | Rymd, uppskjutningar och rymdsystem | Ca 0,8–0,9 mdr USD senaste 12 mån, +66–73 % (2026); orderstock 3,57 mdr USD | Nej (förlust) | Lägsta kurs 3,47 USD (apr 2024) → **topp 150 USD (maj 2026), ca 43 gånger** → ca 61 USD (nov 2026). Börsvärde ca 40 mdr USD, 40–60x försäljningen | 🚀 Extrem omvärdering på berättelse plus orderstock, och extrema ras (−60 %) | B |

## Lärdomar för oss
1. **Lönsamhet avgör omvärderingen, inte tillväxten i sig.** AAC Clyde Space växte nästan lika snabbt som Invisio (38 % mot 45 % per år) men utan vinst, och värderas till 2–3x försäljningen. Invisio och MilDef blev lönsamma och omvärderades. **För Unibap är positivt kassaflöde den viktigaste milstolpen för det starka scenariot.**
2. **Budgetchocker ger snabba omvärderingar.** MilDefs börsvärde nästan fyrdubblades på ca 9 månader (mitten av 2024 till mars 2025) när Europa rustade upp, och halverades sedan igen. **Signal → omvärdering kan gå på månader**, men kursen svänger mycket.
3. **Kundkoncentration kan krascha allt.** GomSpace föll när en stor konstellationskund gick omkull. För Unibap står Leonardo, Loft/Orbitworks och Argotec för en stor del. Bevaka deras finansiella hälsa.
4. **Utspädning äter upp tillväxten.** AAC Clyde Space är exemplet: försäljningen femdubblades men aktieägarna fick inte del av det. Unibap har samma historik (7 gånger fler aktier sedan 2023).
5. **När marknaden tror på en plattform** (Rocket Lab) kan multipeln gå från några få gånger till 40–60 gånger försäljningen. Det är ytterkanten, inte basfallet, men det visar vad drömscenariot kan innebära.
6. **Tillväxttakter i verkligheten:** de nordiska bolagen som lyckades växte ca **37–45 % per år i ca 3 år**, sedan långsammare. Det stämmer med Unibaps mål (30–50 %).

## Casen som lins för Unibap
I `bolag/unibap/marknadsmodell.json` (metoden "Liknande historiska case"):
- **Golv**, som GomSpace: ett bakslag med en stor kund ger platt försäljning (+2 %/år)
- **Förväntat**, som medianen av de nordiska bolagen: +30 %/år i 3 år, sedan +20 %
- **Starkt**, som Invisio och MilDef: +45 %/år i 3 år, sedan +25 %
- **Dröm**, som Rocket Lab: +60 %/år

Casen stöder också framåtmultiplarna: olönsamma rymdbolag ligger på 2–3x och lönsamma försvarsbolag på 5–8x.

## Att undersöka vidare
| Bolag | Varför | Status |
|---|---|---|
| GomSpace | Kontrollera tidslinjen och siffrorna för fallet | Att göra |
| MilDef | Exakt försäljning per år och när de första signalerna kom | Att göra (Börsdata) |
| Invisio | Den tidiga vändningen (ca 2010–2015) och dess signaler | Att göra |
| Kitron eller Mycronic | Omvärdering efter lönsamhet i industriell elektronik | Att göra |

## Källor
- MilDef: https://mb.cision.com/Main/20537/4140584/3415879.pdf, https://finance.yahoo.com/quote/MILDEF.ST/key-statistics/, https://www.tipranks.com/news/company-announcements/mildef-posts-record-2025-results-and-ramps-capacity-on-surging-nato-demand
- Invisio: https://stockanalysis.com/quote/lon/0R86/revenue/, https://www.marketscreener.com/news/invisio-annual-report-2025-report-ce7e51d3de81ff23
- AAC Clyde Space: https://stockanalysis.com/quote/sto/AAC/revenue/, https://pitchbook.com/profiles/company/169173-01
- Rocket Lab: https://www.fool.com/investing/2026/11/05/rocket-lab-stock-has-lost-about-70-from-its-record-is-it-finally-a-buy/, https://www.tradingview.com/symbols/NASDAQ-RKLB/, https://robinhood.com/us/en/stocks/RKLB/
