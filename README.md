# Investerarhjälpen

Ett verktyg som hjälper dig att hitta och följa aktiebolag med fakta i stället för hype. Claude läser rapporter och pressmeddelanden, skriver analyser på enkel svenska, håller koll på dina bolag varje morgon och bygger en egen webbsida åt dig. Du lär dig samtidigt att läsa rapporter i fliken **Skolan**.

Verktyget ger **aldrig** råd om att köpa eller sälja. Besluten är alltid dina.

---

## Så kommer du igång (ca 15 minuter)

### Det här behöver du
- En dator (helst Mac).
- Ett Claude-konto med **Pro** (eller Max). Det kostar en månadsavgift hos Anthropic.

### Steg 1. Skaffa Claude Pro
1. Gå till **claude.ai** och skapa ett konto (eller logga in).
2. Klicka på ditt namn nere till vänster → **Upgrade** → välj **Pro**.

### Steg 2. Installera Claude-appen
1. Gå till **claude.ai/download** och ladda ner appen till din dator.
2. Öppna appen och logga in med samma konto.

### Steg 3. Öppna "Code"
1. Klicka på fliken **Code** högst upp i appen.
2. Välj en mapp när appen frågar, till exempel **Dokument**. Det spelar ingen roll vilken.

### Steg 4. Installera verktyget
Kopiera hela meningen nedan, klistra in den i skrivrutan och tryck **Enter**:

```
Installera tillägget Investerarhjälpen åt mig från GitHub-arkivet Kimmen1993/investerarhjalpen. Kör Claude Codes eget program som följer med appen (sök efter Contents/MacOS/claude under ~/Library/Application Support/Claude/claude-code/) med: plugin install investerarhjalpen --marketplace Kimmen1993/investerarhjalpen. Slå sedan på automatiska uppdateringar genom att sätta "autoUpdate": true på investerarhjalpen under extraKnownMarketplaces i ~/.claude/settings.json.
```

Claude installerar och säger till när det är klart. Claude frågar om lov ett par gånger (för att köra programmet och för att ändra en inställning): klicka **Tillåt** (eller **Allow**) varje gång.

### Steg 5. Starta en ny session
Tillägget börjar gälla i en **ny** session. Klicka på **New session** (eller **Ny session**) uppe till vänster och välj samma mapp som förut.

### Steg 6. Starta
Skriv i skrivrutan:

```
kom igång
```

Claude ställer några enkla frågor (vad du heter, hur du vill investera) och fixar resten: din egen mapp, din egen webbsida och en morgonkoll varje vardag. Svara bara på frågorna.

---

## Så använder du det

Skriv vanlig svenska i Code-fliken. Till exempel:

| Du skriver | Det händer |
|---|---|
| `analysera Kambi` | Claude gör en grundlig analys och lägger bolaget på din sida |
| `uppdatera mig om Kambi` | Senaste nytt om bolaget, på enkel svenska |
| `leta nya bolag` | Claude letar efter intressanta bolag på hela börsen |
| `vad betyder EV/S?` | En enkel förklaring |
| `uppdatera verktyget` | Hämtar senaste versionen |

**Din webbsida** har adressen som Claude gav dig i början. Den är privat tills du själv delar den (knappen **Share** på sidan). Där finns:
- **Läget nu**: hur dina bolag mår, med trafikljus
- **Min portfölj**: läs in dina affärer från banken (Avanza eller Handelsbanken). Bara du ser dem.
- **Skolan**: korta lektioner om hur man läser rapporter
- **Fråga Claude**: knappen nere till höger

**Automatiken:**
- Varje vardag kl. 08.30 kollar Claude nyheter om dina bolag.
- Varje söndag kl. 17 görs en grundligare genomgång.
- Datorn och Claude-appen behöver vara igång då. Annars körs det nästa gång appen är öppen.

---

## Vanliga frågor

**Kostar det något mer?** Nej, bara ditt Claude-abonnemang. Verktyget och sidan är gratis.

**Kan någon se mina bolag eller min portfölj?** Nej. Din mapp ligger på din dator, och din sida är privat tills du delar den. Portföljen syns bara för dig, även om du delar sidan.

**Något fungerar inte.** Skriv `uppdatera verktyget`. Hjälper inte det: beskriv problemet för Claude med egna ord, eller hör av dig till den som skickade länken.

---

*För den som underhåller verktyget:* tillägget ligger i `plugins/investerarhjalpen/`. Användarens data ligger i användarens egen mapp (med `installningar.json`) och rörs aldrig av uppdateringar. Skriv en rad i `ANDRINGAR.md` vid varje ändring. Versionen räknas fram ur git, så varje uppladdning når användarna.
