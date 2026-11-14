---
name: forslag
description: Skriver ett tydligt förbättringsförslag för verktyget Investerarhjälpen (en bugg, något som borde fungera annorlunda, en ny funktion eller ändrad layout) så att användaren kan skicka det till den som underhåller verktyget. Används när användaren skriver "förslag", "det här borde vara annorlunda", "jag hittade ett fel", "skicka till Kimm" eller liknande om själva verktyget.
---

# Förbättringsförslag

> **Var saker ligger.** Verktygsmappen (kallas `$IH` nedan) är två nivåer upp från den här skillens mapp. Datamappen är användarens mapp med `installningar.json`.

Verktyget är gemensamt: förbättringar görs av den som underhåller det och når alla användare via uppdateringar. Användaren ändrar alltså inte verktyget själv; ditt jobb är att göra förslaget så tydligt att det går att genomföra direkt.

1. **Förstå förslaget.** Ställ högst 2 korta frågor om det behövs: Vad hände, eller vad vill du ha? Var på sidan eller i vilket kommando? Har du ett exempel?
2. **Kolla om det redan är löst.** Läs de senaste raderna i `$IH/ANDRINGAR.md`. Är det redan rättat: säg det och föreslå `/investerarhjalpen:uppdatera-verktyget`.
3. **Skriv förslaget** i den här formen, på enkel svenska:

```
FÖRSLAG TILL INVESTERARHJÄLPEN (<datum>, från <namn i installningar.json>)
Typ: Fel / Förbättring / Ny funktion / Layout
Var: <flik, sida eller kommando>
Vad händer nu: <kort>
Vad borde hända: <kort>
Exempel: <konkret exempel, utan egna innehav, belopp eller annat privat>
Varför det spelar roll: <en mening>
Verktygets version: <mappnamnet i installPath>
```

4. **Integritet:** ta aldrig med användarens innehav, antal, belopp, portföljuppgifter eller annat privat i förslaget. Bolagsnamn bara om förslaget gäller det bolagets analys och användaren säger att det är okej.
5. **Spara** förslaget sist i `forslag.md` i datamappen (skapa filen om den saknas), med datum.
6. **Säg till användaren:** "Kopiera rutan ovan och skicka den till den som underhåller verktyget (till exempel i ett sms). När förbättringen är gjord kommer den till dig automatiskt."
