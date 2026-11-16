# Tesens pelare och jämförelsen med liknande bolag

Två rutor på bolagssidan som gör tesen lätt att följa.
- **Tesens pelare** visar vilka delar av tesen som håller och vilka som haltar.
- **Jämförelsen** visar vad marknaden betalar för liknande bolag.

Båda fylls i vid bolagsanalysen och ses över vid varje djupdykning.

## Tesens pelare
En tes vilar på 3–5 bärande pelare. Varje pelare är något som **måste stämma** för att tesen ska hålla, och som går att följa upp. Exempel: "Kunderna beställer igen", "Kassan räcker till vinst", "Marginalen stiger med volymen".

| Fält | Vad |
|---|---|
| `pelare` | Pelaren, högst ca 8 ord |
| `forvantan` | Vad vi väntade oss när tesen skrevs, mätbart om det går |
| `lage` | Läget nu, en mening med siffror |
| `trend` | `upp` (stärks), `still` (oförändrat) eller `ner` (försvagas) |
| `niva` | Bevisnivå för läget: A, B, C eller ? |

Dessutom `pelare_datum` (när de senast sågs över) och `overtygelse`: `hog`, `medel` eller `lag`. Övertygelsen anger hur säkra vi är på tesen som helhet, inte hur bra aktien är.

**Regler**
- Pelarna ska vara **falsifierbara**: det ska gå att se om de brister. "Bra ledning" är ingen pelare. "Ledningen levererar minst 70 % av sina löften" är det.
- Varje pelare hör ihop med något på listan "Vad skulle fälla tesen?". Om en pelare går `ner` två gånger i rad ska trafikljuset ses över.
- Pelarna för ett kärnbolag handlar om kvalitet och pris (till exempel "Marginalen håller mot konkurrenterna"). För ett vändningsbolag handlar de om milstolparna i vändningen.
- Skriv på klarspråk. Pelarna läses av nybörjare.

## Jämförelse med liknande bolag
Välj 3–5 noterade bolag som liknar vårt: samma bransch eller affärsmodell, helst i Norden eller Europa. Ta gärna med **ett bolag som redan har nått nästa steg**, för att se vad marknaden betalar då. Metoden finns i metod 07, avsnitt 3.

| Fält per bolag | Vad |
|---|---|
| `namn`, `land` | |
| `varfor` | Varför det är jämförbart, kort |
| `borsvarde_mkr` | Börsvärde i miljoner kronor (omräknat) |
| `ev_s` | EV/S: företagsvärde delat med försäljningen de senaste 12 månaderna |
| `tillvaxt_pct` | Försäljningstillväxt senaste 12 månaderna |
| `rorelsemarginal_pct` | Rörelsemarginal senaste 12 månaderna |
| `lage` | Var bolaget står: turnaround-steg eller Lynchkategori, kort |
| `niva`, `kalla`, `datum` | Bevisnivå, källa och datum för siffrorna |

Vårt eget bolag läggs till automatiskt från `vardering.json` och `kurs.json` när det går.

Dessutom `slutsats`: 1–3 meningar på klarspråk som svarar på frågan **"om bolaget når nästa steg, vad brukar marknaden betala då?"**, och `datum`.

**Regler**
- Siffror som inte kunde kontrolleras skrivs som `null` med `niva: "?"`. Gissa aldrig.
- Jämförelsen är en pusselbit och aldrig en riktkurs.
- Med Börsdata Pro (tillägg senare) hämtas siffrorna automatiskt. Utan den hämtas de ur rapporter och kurssidor vid djupdykningen.

## I `status.json`
```json
"pelare": [
  {"pelare": "Kunderna beställer igen", "forvantan": "Minst 3 kunder med upprepade order 2026",
   "lage": "Leonardo, Loft och Argotec har beställt igen", "trend": "upp", "niva": "A"}
],
"pelare_datum": "2026-11-16",
"overtygelse": "medel",
"jamforelse": {
  "datum": "2026-11-16",
  "bolag": [{"namn": "…", "land": "SE", "varfor": "…", "borsvarde_mkr": 900, "ev_s": 2.1,
             "tillvaxt_pct": 15, "rorelsemarginal_pct": -8, "lage": "Steg 3", "niva": "B", "kalla": "…", "datum": "2026-11-14"}],
  "slutsats": "…"
}
```
Det gamla textfältet `jamforelse` ("Inte gjord än") ersätts av objektet ovan.
