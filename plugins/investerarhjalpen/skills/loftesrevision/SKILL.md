---
name: loftesrevision
description: Gå igenom 2–3 års kommunikation från ett bolag (rapporter, vd-ord, prospekt, presentationer, pressmeddelanden, intervjuer) och följ upp varje mätbart löfte. Var det i tid, försenat, missat med eller utan rimlig förklaring, eller vilseledande? Använd när användaren skriver "/loftesrevision X", "håller de vad de lovar?" eller som steg i /bolagsanalys.
---

# Löftesrevision

> **Var saker ligger.** Verktygsmappen (kallas `$IH` nedan) är två nivåer upp från den här skillens mapp: mappen som innehåller `verktyg/`, `metod/`, `larande/` och `mall/`. Datamappen är användarens egen mapp med `installningar.json` (oftast mappen sessionen är öppnad i; annars den mapp som `installningar.json` pekar ut). Metodfiler (`metod/…`), lektioner (`larande/…`) och skript (`verktyg/…`) läses i verktygsmappen; allt annat (`bolag/`, `radar/`, `teman/`, `journal.md`, `min-strategi.md`, `site/` …) i datamappen. Kör skript från datamappen och ersätt `$IH` med den riktiga sökvägen, till exempel `cd "<datamappen>" && python3 -I "$IH/verktyg/nyhetskoll.py"`. Sidans adress står i `installningar.json` (`sida_url`). Saknas `installningar.json`: be användaren köra `/investerarhjalpen:kom-igang` först.

1. Läs `metod/05-loftesrevision.md`. Finns `bolag/<namn>/loften.md` redan: fortsätt från dess period och gör inte om arbetet.
2. Lista materialet för perioden, normalt 2–3 år:
   - alla kvartalsrapporter, bokslutskommunikéer och årsredovisningar
   - prospekt och memorandum vid emissioner
   - investerarpresentationer och kapitalmarknadsdagar
   - pressmeddelanden
   - intervjuer som går att hitta
   
   Använd MFN, Inderes, Nasdaq och bolagets IR-sida. Är PDF:er olästa: säg vilka.

   **PDF:er:** ladda ner dem till en egen mapp i scratchpad och läs texten med `swift "$IH/verktyg/pdftext.swift" fil.pdf`. Ger det nästan ingen text är PDF:en inskannad; kör då `swift "$IH/verktyg/ocr.swift" fil.pdf` (macOS textigenkänning). Plocka sedan ut vd-ordet, som börjar vid "VD har ordet" och slutar vid "Uppsala i …".
3. Arbeta **kronologiskt**. Plocka ut varje mätbart löfte med datum och källa. Citera kort, under 15 ord, eller skriv om med egna ord.
4. Leta efter utfallet för varje löfte i senare material. Kolla särskilt:
   - om en förklaring kom *innan* deadline (förtjänar ⚠️) eller först efteråt (❌)
   - om målet bara slutade nämnas (🚩)
   - om insiders sålde nära ett optimistiskt uttalande (Insynsregistret, 🚩)
5. Räkna fram leveransgrad, precision, snittförsening, antal 🚩 och trend. Delas perioden av ett vd-byte: räkna före och efter var för sig.
6. Skriv `bolag/<namn>/loften.md` enligt mallen. Lägg in sammanfattningen under "Löftesrevision" i `tes.md` och en post i `logg.md`.
7. Svara användaren kort:
   - måtten
   - de 3 tydligaste hållna löftena
   - de 3 tydligaste missarna, med förklaringen och om den är rimlig
   - eventuella 🚩, med konkret vad som hänt
   - vad det betyder för hur mycket man kan lita på bolagets prognoser
   
   Påstå aldrig att någon ljugit: beskriv vad som hände.
