---
name: trendspaning
description: Trendradarn. Spanar brett i hela världen efter stora skiften (beslutade pengar, fallande kostnader, flaskhalsar, regler, geopolitik, demografi och hälsa, tekniska genombrott), mäter dem över flera år med gratis data, jämför med historiska vinnare och hypefällor, och letar upp bolag i båda spåren, även onoterade och vägar in i dem. Används av söndagsuppgiften första söndagen i månaden, eller när användaren skriver "kör trendspaningen", "vad blir nästa stora trend", "/trendspaning", eller frågar om en framtidsfråga som "kommer elflyg att slå igenom?".
---

# Trendspaning

> **Var saker ligger.** Verktygsmappen (kallas `$IH` nedan) är två nivåer upp från den här skillens mapp: mappen som innehåller `verktyg/`, `metod/`, `larande/` och `mall/`. Datamappen är användarens egen mapp med `installningar.json` (oftast mappen sessionen är öppnad i; annars den mapp som `installningar.json` pekar ut). Metodfiler (`metod/…`), lektioner (`larande/…`) och skript (`verktyg/…`) läses i verktygsmappen; allt annat (`bolag/`, `radar/`, `teman/`, `journal.md`, `min-strategi.md`, `site/` …) i datamappen. Kör skript från datamappen och ersätt `$IH` med den riktiga sökvägen, till exempel `cd "<datamappen>" && python3 -I "$IH/verktyg/nyhetskoll.py"`. Sidans adress står i `installningar.json` (`sida_url`). Saknas `installningar.json`: be användaren köra `/investerarhjalpen:kom-igang` först.

**Läs först `$IH/REGLER.md`** (gemensamma regler: klarspråk, bevisnivåer, inga köp- eller säljråd, integritet), `min-strategi.md` i datamappen och `$IH/metod/21-trendradarn.md`.

Trendradarn följer stora skiften i **hela världen** under lång tid och letar sedan upp bolag, helst svenska och nordiska, som kan rida på vågen. Du samlar bevis och presenterar dem. Användaren tar ställning. Gör aldrig förutsägelser som om de vore säkra, och ge inga köp- eller säljråd.

## Vilket läge?
- **Månadsspaningen** (söndagsuppgiften första söndagen i månaden, eller "kör trendspaningen"): gör steg 1–6.
- **En fråga från användaren** ("kommer elflyg att slå igenom?", "vad händer om Kina inte får fler barn?"): gör steg 2–5 för just den frågan. Finns trenden redan i `trender/`: uppdatera den.
- **"Vilka trender följer vi?"**: läs `trender/*.json` och svara kort med status, signal och vad som har ändrats.

## 1. Mät det som redan följs
Kör `python3 -I "$IH/verktyg/trendmatare.py"` från datamappen. Läs utskriften: vilka trender har fått starkare eller svagare hårda data, och finns någon hypevarning?

## 2. Spana brett (högst ca 15 sökningar per månad)
Gå igenom de sju drivkrafterna i metod 21 med blicken på **hela världen**: beslutade pengar, kostnader som faller, flaskhalsar, regler med datum, geopolitik, demografi och hälsa, och tekniska genombrott. Prioritera källor på A- och B-nivå:
- beslut om budgetar och program (EU, USA, Kina, Indien, NATO, stora länders regeringar)
- storbolagens investeringsplaner och vad de säger är flaskhalsar i sina rapporter
- statistik över försäljning och användning (IEA, Our World in Data, Eurostat, branschorganisationer)
- stora studieresultat, godkännanden och certifieringar
- återkommande ämnen i rapporter från centralbanker, IEA, WHO, FN och stora konsultbolag (B-nivå: de är prognoser)

Leta efter **det som rör sig men inte står på förstasidorna**. Tänk också på andra och tredje ledet: om det här händer, vad behövs sedan?

## 3. Nya kandidater (högst 2 per månad)
Skapa `trender/<trend>.json` utifrån `$IH/mall-trend.json` för en ny trend bara om den har minst en drivkraft på A- eller B-nivå. Fyll i:
- `fraga`: en fråga som går att besvara med ja eller nej om några år
- `i_en_mening` på klarspråk
- `drivkrafter` med typ, text, `niva`, `kalla` och `datum`
- `troskel`: det som måste hända innan trenden kan ta fart, och läget nu
- `matare`: minst en mätare för kunskap eller uppmärksamhet, och **så snart det går en för adoption, kostnad eller pengar** (Our World in Data, OpenAlex, ClinicalTrials.gov eller Wikipedia, se skriptets huvud). Kontrollera att grafens eller artikelns namn finns. Finns ingen tidsserie: lägg in `"kalla": "manuell"` och skriv värden per år i `serier.<id>.ar` med källa i `serier.<id>.kalla_text`.
- `konsekvenser`: 2–4 led "om → då", oftast på C-nivå
- `motbevis`: vad talar emot, och vad skulle få trenden att stanna?
- `status: "kandidat"`, `fas`, `upptackt` och en rad i `logg`

Kör sedan mätaren för trenden: `python3 -I "$IH/verktyg/trendmatare.py" <trend>`.

## 4. Se över trenderna som följs
För varje trend (de äldst granskade först, högst ca 4 per månad):
- Nya beslut, order, siffror eller milstolpar? Lägg till dem i `drivkrafter`, uppdatera `troskel` och skriv en rad i `logg`.
- **Status** enligt tabellen i metod 21, aldrig mer än ett steg per månad, alltid med motivering i `logg`. Avfärdade trender sparas med lärdomen.
- Saknas hårda data (`signal.saknar_hard_data`)? Leta efter en tidsserie för adoption, kostnad eller pengar. Det är den viktigaste förbättringen av en trend.
- Jämför med historiebiblioteket (`signal.liknar` och `trender/historia/`): liknar mönstret en vinnare, en förlorare eller "rätt trend, fel bolag"?

## 5. Bolagen
För trender med status **följs** eller högre: fyll i eller se över `bolag`, med värdekedjan och flaskhalsen först (metod 06 och 21):
```json
{"namn": "…", "land": "SE", "noterat": true, "spar": "vandning|karna|onoterat", "roll": "flaskhals|tillverkare|leverantor|kund|agare",
 "exponering": "hog|medel|lag", "varfor": "en mening", "vag_in": "för onoterade: noterad ägare eller partner", "niva": "A|B|C|?", "kalla": "…", "slug": "<mapp i bolag/ om det bevakas>"}
```
- Svenska och nordiska bolag först, men ta med de globala ledarna så att jämförelsen finns.
- **Båda spåren:** mindre bolag där trenden kan bli hela affären (Vändning), och större bolag där trenden är tillräckligt stor för att flytta hela bolaget (Kärna).
- **Onoterade bolag** skrivs in med `vag_in`: noterade ägare, noterade partners, planer på notering. Rekommendera aldrig någon väg.
- Ett intressant bolag som inte bevakas: lägg det i `bevakning.md` som kandidat med trendens namn. Användaren väljer om det ska analyseras med `/bolagsanalys`.

## 6. Avsluta
- Bygg sidan (`python3 -I "$IH/verktyg/bygg_sida.py"`) och publicera den till `sida_url` (utelämna `capabilities`).
- I söndagens notis: en rad om trenderna, till exempel `Trender: ny kandidat Elflyg. Drönare stärks (beslutade budgetar i 3 länder).` Har inget ändrats: hoppa över raden.
- Svara kort: nya kandidater, ändrad status med motivering, och de 1–3 viktigaste nya bevisen.
