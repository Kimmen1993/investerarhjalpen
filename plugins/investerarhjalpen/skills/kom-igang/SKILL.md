---
name: kom-igang
description: Första uppsättningen av Investerarhjälpen för en ny användare. Skapar användarens egen datamapp, skriver in strategin, bygger och publicerar användarens egen webbsida och schemalägger morgonkoll och söndagsgenomgång. Används när någon skriver "kom igång", "starta", "sätt upp verktyget" eller saknar installningar.json.
---

# Kom igång med Investerarhjälpen

> **Var saker ligger.** Verktygsmappen (kallas `$IH` nedan) är två nivåer upp från den här skillens mapp: mappen som innehåller `verktyg/`, `metod/`, `larande/` och `mall/`.

Användaren är ofta **helt ny** både på aktieanalys och på Claude. Skriv kort, vänligt och på enkel svenska. En sak i taget. Förklara varje steg med en mening. Använd frågeverktyget (AskUserQuestion) med färdiga svarsalternativ i stället för öppna frågor när det går.

## 1. Kolla datorn (tyst, utan att störa användaren i onödan)
- Kör `python3 --version`. Saknas Python på en Mac: be användaren köra `xcode-select --install` (ett fönster öppnas, klicka **Installera**) och säga till när det är klart. På Windows: be användaren installera Python från Microsoft Store.
- PDF:er kan läsas med Read-verktyget om `swift` saknas, så det behövs inte.

## 2. Finns redan en datamapp?
Leta efter `installningar.json` i den öppna mappen och i `~/Documents/Investerarhjalpen`. Finns den: säg att allt redan är uppsatt och erbjud att analysera ett första bolag. Avsluta annars inte här.

## 3. Fråga (en fråga i taget, med svarsalternativ)
1. Vad ska verktyget kalla dig? (förnamn)
2. Hur vill du investera? Föreslå: "Hitta små bolag tidigt som kan vända (turnarounds), små startpositioner och större när vändningen bekräftas" (rekommenderat, standard), "Stabila bolag som växer lugnt", "Blandat". Låt användaren skriva med egna ord om hen vill.
3. Får söndagsgenomgången läsa LinkedIn automatiskt via Claude in Chrome (bara läsa, bara yrkesroller, ca 10–15 profiler)? Ja eller nej. Förklara att det kräver Claude-tillägget i Chrome och att man är inloggad på LinkedIn.
4. Vill du ha notiser när något händer i dina bolag? Ja eller nej.

## 4. Skapa datamappen
- Plats: `~/Documents/Investerarhjalpen` (fråga bara om användaren vill ha en annan plats).
- Kör `python3 -I "$IH/verktyg/ny_datamapp.py" "<mappen>" --namn "<namn>" --egna-ord "<svaret på fråga 2>" --linkedin ja|nej --notiser ja|nej` (svaren på fråga 3 och 4).
- Passar standardstrategin inte svaret på fråga 2: justera `min-strategi.md` med användarens ord, men behåll strukturen (fas 1, fas 2, redo-poäng).

## 5. Bygg och publicera användarens egen sida
- `cd "<mappen>" && python3 -I "$IH/verktyg/bygg_sida.py"`.
- Publicera `site/index.html` med Artifact-verktyget som en **ny** artifact, med `capabilities: {"sample": {}, "db": {}, "user": {}}`, `icon` "chart" och beskrivningen "Min investerarhjälp". Spara adressen i `installningar.json` som `sida_url`.
- Berätta att sidan är **privat** tills användaren själv delar den i Share-menyn.

## 6. Schemalägg automatiken
Använd verktyget för schemalagda uppgifter och skapa två uppgifter (fråga först om tiderna passar):
- `investerarhjalpen-dagskoll`, vardagar kl. 08.30 (`30 8 * * 1-5`). Prompt: "Kör /investerarhjalpen:dagskoll. Datamappen är <mappen>."
- `investerarhjalpen-djupdykning`, söndagar kl. 17 (`0 17 * * 0`). Prompt: "Kör först /investerarhjalpen:screening och sedan /investerarhjalpen:djupdykning. Datamappen är <mappen>."
Förklara att datorn och Claude-appen behöver vara igång vid de tiderna; annars körs uppgiften nästa gång appen är öppen.

## 7. Uppdateringar
Kontrollera att `~/.claude/settings.json` har `"autoUpdate": true` på `investerarhjalpen` under `extraKnownMarketplaces`. Saknas det: fråga användaren först ("Får jag slå på automatiska uppdateringar av verktyget? Det ändrar en inställning i Claude."), och lägg till det bara om svaret är ja (ändra inget annat i filen). Säg sedan en gång, enkelt: "Verktyget hämtar förbättringar av sig självt. Vill du hämta direkt kan du skriva 'uppdatera verktyget'."

## 8. Första bolaget och portföljen
- Fråga vilket bolag användaren vill börja med, och kör `/investerarhjalpen:bolagsanalys <bolag>`. Säg att en första analys tar en stund.
- Berätta att egna innehav läses in under fliken **Min portfölj** på sidan (exportfil från banken), och att de bara syns för användaren.

## 9. Avsluta
Sammanfatta på 4–5 rader: var mappen ligger, sidans adress, när automatiken körs, och tre saker man kan skriva: "analysera <bolag>", "uppdatera mig om <bolag>", "leta nya bolag". Påminn om att verktyget aldrig ger köp- eller säljråd.
