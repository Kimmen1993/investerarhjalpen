# Tomma mallar för ett nytt bolag

Skillen `bolagsanalys` använder de här filerna som mall när användaren saknar ett färdigt bolag att utgå från. De visar bara fälten, utan innehåll. `…` ersätts med text, `0` med siffror och `ÅÅÅÅ-MM-DD` med datum. Där flera värden står med `|` väljer du ett. Fälten förklaras i metoderna:

| Fil | Metod |
|---|---|
| `status.json` | REGLER.md (Mappstruktur), metod 07, 15, 18 och 20 |
| `vardering.json` | metod 11 |
| `mojligheter.json` | metod 12 (`resultat` räknas fram av `pipeline.py`) |
| `marknadsmodell.json` | metod 13 (`resultat` räknas fram av `marknad.py`) |
| `nyckeltal.json` | belopp i miljoner kronor per kvartal |
| `arsdata.json` | metod 22 (skapas av `arsdata.py`; skriv bara själv för bolag utan ESEF) |
| `karna.json` | metod 22, temahävstången (bara spåret Kärna) |
| `handelser.json` | skillen `dagskoll`, avsnitt 2 |
| `tes.md`, `kallor.md`, `loften.md`, `logg.md`, `kundregister.md`, `natverk.md` | rubrikerna att använda |
