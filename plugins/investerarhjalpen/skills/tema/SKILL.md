---
name: tema
description: Analysera ett investeringstema eller leta efter nästa stora fokusområde. Använd för att bedöma ett tema (fas, drivkrafter, värdekedja, flaskhalsar) och hitta noterade bolag (svenska först) som är exponerade. Använd när användaren skriver "/tema X", "vad blir nästa stora grej", "vilka bolag gynnas av X" eller frågar om omvärldsläget.
---

# Tema

> **Var saker ligger.** Verktygsmappen (kallas `$IH` nedan) är två nivåer upp från den här skillens mapp: mappen som innehåller `verktyg/`, `metod/`, `larande/` och `mall/`. Datamappen är användarens egen mapp med `installningar.json` (oftast mappen sessionen är öppnad i; annars den mapp som `installningar.json` pekar ut). Metodfiler (`metod/…`), lektioner (`larande/…`) och skript (`verktyg/…`) läses i verktygsmappen; allt annat (`bolag/`, `radar/`, `teman/`, `journal.md`, `min-strategi.md`, `site/` …) i datamappen. Kör skript från datamappen och ersätt `$IH` med den riktiga sökvägen, till exempel `cd "<datamappen>" && python3 -I "$IH/verktyg/nyhetskoll.py"`. Sidans adress står i `installningar.json` (`sida_url`). Saknas `installningar.json`: be användaren köra `/investerarhjalpen:kom-igang` först.

Två lägen:

## A. Ett angivet tema (`/tema rymdförsvar`)
1. Läs `metod/06-omvarld-och-teman.md`. Finns `teman/<tema>.md`: uppdatera den i stället för att börja om.
2. Belägg drivkrafterna med källor och bevisnivå. Prioritera **beslutade pengar**, som budgetar, program och storbolagens investeringsplaner, framför prognoser.
3. Bedöm fasen (1–4) och motivera. Ta med vad "massan" redan pratar om: medier, temafonder, forum.
4. Rita värdekedjan, peka ut flaskhalsarna och tänk ett steg till ("vad behövs nästa år om detta lyckas?").
5. Lista noterade bolag i varje led, svenska först. Ange för varje bolag:
   - hur stor del av omsättningen som är exponerad mot temat, om den går att veta
   - börsvärde
   - en mening om varför bolaget är med
6. Skriv vad som skulle få temat att stanna av, och vilka signaler som ska bevakas.
7. Spara `teman/<tema>.md` och lägg till de bästa bolagen som kandidater i `bevakning.md`. Länka till befintliga bolagsmappar.

## B. Leta nästa tema (`/tema` utan argument)
1. Sök efter fas 1–2-signaler från de senaste 6–12 månaderna:
   - nya budgetbeslut och program (EU, NATO, Sverige, USA)
   - tekniktrösklar som nyligen passerats
   - flaskhalsar som storbolag nämner i sina rapporter
   - regler med kommande deadline
   - geopolitiska skiften
2. Ta fram 3–5 tänkbara teman. För varje tema: drivkraften med A/B-källa, bedömd fas, och varför det kanske inte redan är upptäckt.
3. Svara användaren med en kort jämförelse och fråga vilket tema som ska djupanalyseras med läge A. Var ärlig om osäkerheten: det här är sannolikheter, inte förutsägelser.

Ge aldrig köp- eller säljråd.
