---
name: panel
description: Ta fram eller uppdatera investerarpanelen för ett bevakat bolag, alltså hur bolaget ser ut med Buffetts, Lynchs, Fishers, Grahams, Terry Smiths och Blankarens glasögon enligt deras publicerade filosofi. Används när användaren skriver "investerarpanelen för X", "hur skulle Buffett se på X?", "/panel X", och som steg i bolagsanalys och djupdykning. Hanterar också spår och Lynchkategori ("ja till spåret för X", "byt spår för X").
---

# Investerarpanelen

> **Var saker ligger.** Verktygsmappen (kallas `$IH` nedan) är två nivåer upp från den här skillens mapp: mappen som innehåller `verktyg/`, `metod/`, `larande/` och `mall/`. Datamappen är användarens egen mapp med `installningar.json`. Metodfiler läses i verktygsmappen; `bolag/`, `journal.md` och `site/` i datamappen. Sidans adress står i `installningar.json` (`sida_url`).

**Läs först `$IH/REGLER.md`** och `$IH/metod/18-spar-och-investerarpanelen.md`.

## Ta fram panelen för ett bolag
1. Läs `bolag/<namn>/status.json`, `tes.md`, `nyckeltal.json`, `vardering.json`, `kurs.json`, `loften.md` och `kundregister.md` (de som finns). Sök bara på nätet om en siffra i checklistan saknas och kan ändra något kort. Högst ca 3 sökningar per bolag.
2. Saknar bolaget `spar` eller `lynch`: föreslå dem enligt metod 18 med `"spar_bekraftad": false`.
3. Gå igenom checklistan för var och en av de sex investerarna (`buffett`, `lynch`, `fisher`, `graham`, `smith`, `blankaren`) och skriv `bolag/<namn>/panel.json`:
```json
{"datum": "ÅÅÅÅ-MM-DD", "roster": [
 {"id": "buffett", "passar": "mycket | delvis | lite",
  "dom": "En mening på klarspråk: hur bolaget ser ut med den här investerarens glasögon.",
  "siffror": [{"namn": "Avkastning på kapitalet", "varde": "18 %", "niva": "A", "kommentar": "2025"}],
  "gilla": ["1–3 punkter"], "ogilla": ["1–3 punkter"],
  "andra_sig": "Vad som skulle få investeraren att ändra sig."}]}
```
   - Lägg först de investerare som väger tyngst för spåret (Vändning: Lynch, Fisher, Blankaren; Kärna: Buffett, Smith, Graham, Lynch, Blankaren).
   - **Blankaren** bedöms omvänt: `passar: "mycket"` betyder stora risker för ägarna. `gilla` är riskerna för ägaren (det Blankaren skulle satsa på), `ogilla` är det som skyddar ägaren och `andra_sig` är vad som skulle få Blankaren att ge upp.
   - Saknas en siffra: `"varde": "?"`, `"niva": "?"` och vad som behövs. Gissa aldrig.
   - Skriv "enligt X:s filosofi" eller "med X:s glasögon", aldrig citat eller "X säger".
   - Säg tydligt när ett lågt betyg är väntat för spåret, till exempel att Graham sällan gillar förlustbolag.
4. Bygg sidan (`python3 -I "$IH/verktyg/bygg_sida.py"` från datamappen) och publicera `site/index.html` till `sida_url` (utelämna `capabilities`).
5. Svara kort: spåret, en rad per investerare med `passar` och domen, och var de är överens eller spretar.

## Bekräfta eller byta spår
- "Ja till spåret för X": sätt `"spar_bekraftad": true` i `status.json`, bygg och publicera sidan.
- "Byt spår för X" eller ett förslag från djupdykningen som användaren säger ja till: ändra `spar` (och vid behov `lynch`), sätt `spar_bekraftad: true`, skriv en rad i `bolag/<namn>/logg.md` och i `journal.md` med datum, gammalt och nytt spår och skälet. Uppdatera panelen, bygg och publicera.
- Flera bolag på en gång ("ja till alla spårförslag"): visa listan först och vänta på ja.

Ge aldrig köp- eller säljråd.
