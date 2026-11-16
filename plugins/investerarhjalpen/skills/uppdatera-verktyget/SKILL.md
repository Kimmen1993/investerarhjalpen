---
name: uppdatera-verktyget
description: Hämtar senaste versionen av Investerarhjälpen-tillägget och bygger om användarens sida med den. Används när användaren skriver "uppdatera verktyget", "hämta senaste versionen" eller när något verkar trasigt efter en rättning.
---

# Uppdatera verktyget

> **Var saker ligger.** Verktygsmappen (kallas `$IH` nedan) är två nivåer upp från den här skillens mapp. Datamappen är användarens mapp med `installningar.json`.

**Läs först `$IH/REGLER.md`** (gemensamma regler: klarspråk, bevisnivåer, inga köp- eller säljråd, integritet).

Användarens data (bolag, journal, strategi, portfölj) rörs aldrig av en uppdatering.

1. Kör Claude Codes program som följer med appen (sök efter `Contents/MacOS/claude` under `~/Library/Application Support/Claude/claude-code/`; finns `claude` i terminalen går det också): `<programmet> plugin update investerarhjalpen@investerarhjalpen`. Fungerar det: säg att uppdateringen är hämtad och att den gäller från nästa session (eller efter `/reload-plugins`).
2. Fungerar kommandot inte (till exempel för att `claude` inte finns i terminalen): be användaren klicka på **+** bredvid skrivrutan → **Plugins** → **Marketplaces** → **investerarhjalpen** → **Update marketplace**, och gärna **Enable auto-update** så att det sker av sig självt framöver.
3. När den nya versionen är laddad: kör `cd "<datamappen>" && python3 -I "$IH/verktyg/bygg_sida.py"` och publicera `site/index.html` till `sida_url` i `installningar.json` (utelämna `capabilities`).
4. Saknar några bolag `spar` i `status.json` (nytt sedan 2026-11-14): föreslå spår och Lynchkategori för dem enligt `$IH/metod/18-spar-och-investerarpanelen.md`, utifrån det som redan står i `status.json` (ingen sökning behövs). Spara med `"spar_bekraftad": false`, bygg om sidan och visa förslagen som en kort lista. Panelen tas fram vid nästa djupdykning, eller direkt om användaren ber om det.
5. Saknar bolag `kalender` i `status.json` (nytt sedan 2026-11-16): fyll i den utifrån `nasta_handelse` och `enkelt.vantar_pa`, utan sökningar. Exakta datum där de står, annars bara månaden med `"ungefar": true` (format i skillen `dagskoll`, avsnitt 4c). Pelare och jämförelse fylls i vid nästa djupdykning.
6. Berätta kort vad som är nytt om `$IH/ANDRINGAR.md` finns (de senaste raderna).
