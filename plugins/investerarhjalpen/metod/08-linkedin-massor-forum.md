# LinkedIn, mässor och forum

De här källorna ger ofta de **tidigaste** signalerna, men de är också de **svagaste** som belägg. De används för att hitta spår, och spåren kontrolleras sedan i primärkällor.

## 1. LinkedIn
### Vilka vi följer (max ca 10 per bolag, i `bolag/<namn>/natverk.md`)
- **Bolaget:** vd, finanschef, styrelseordförande och aktiva styrelseledamöter, försäljningschef, KAM och affärsutvecklare, produkt- och teknikansvariga
- **Kunder och partners:** den person som syns i samarbetet (projektledare, inköpare, vd)
- **Bolagssidorna** för bolaget, dess kunder och partners

### Vad vi letar efter
| Signal | Exempel | Normal nivå |
|---|---|---|
| Resor och platser | "På väg till launch site", besök hos kund, montrar på mässor | C–B |
| Vem som gillar och kommenterar vad | Kundens vd gillar bolagets inlägg om en leverans | C |
| Rekryteringar | Tjänster inom produktion, kvalitet, exportkontroll, nya länder | B |
| Nya titlar och byten | Säljare som byter till en kund, eller tvärtom | C |
| Kunders inlägg om leverantören | "Excited to see X's products supporting…" | B–A (om det är kundens officiella konto) |

### Gränser
- **Bara yrkesrollen.** Spara endast det personen själv publicerat om jobbet. Aldrig privatliv, familj eller adresser.
- **Inget kontaktande.** Vi läser, men gillar, kommenterar och skickar aldrig förfrågningar.
- **Måttligt tempo:** ca 10–15 profiler per djupdykning, via Claude in Chrome med användarens inloggning. LinkedIn begränsar konton som läses i stor skala.
- **Läckvarning:** verkar ett inlägg avslöja kurspåverkande information som bolaget inte offentliggjort (en order, ett avtal, en siffra), markera det med ⚠️ **Möjlig läcka – handla inte på detta** och vänta tills bolaget själv publicerat. Att handla på icke-offentlig kurspåverkande information kan vara olaglig insiderhandel.

## 2. Mässor och konferenser
Kalendern finns i `teman/massor.md`. Inför och efter en stor mässa i bolagets bransch:
1. **Utställarlistan:** står bolaget med? I vems monter (en partners)?
2. **Talar- och panellistor:** vem sitter med vem? Vd i panel med en potentiell kund är ett C-spår.
3. **LinkedIn under mässveckan:** bilder från montern, "great meeting with…", gemensamma demonstrationer.
4. **Pressmeddelanden under mässveckan:** bolag sparar ofta nyheter till stora mässor.

Ett möte är inte en order. Mässkopplingar blir högst **B**, oftast **C**. Bra att veta: avtal annonseras ofta på eller strax efter stora mässor och konferenser. Unibaps Leonardo-pressmeddelande (5 okt 2026) är till exempel daterat i Antalya, där något branschevenemang troligen pågick (inte kontrollerat).

## 3. Forum och sociala medier
### Grundregel
Allt från forum är **?** tills det har kontrollerats i en primärkälla. Forum används för tre saker:
1. **Hitta spår** att kontrollera
2. **Hitta kritik och motbevis**, oftast det mest värdefulla
3. **Mäta hur upptäckt bolaget är.** Är forumen fulla är informationsövertaget sannolikt borta.

### Rangordning av källor
| Nivå | Källa | Varför |
|---|---|---|
| Högre | Inderes forum, Shareville (Nordnet; innehaven syns), analytikers namngivna konton på X | Moderering eller öppet innehav, ofta med källhänvisningar |
| Mellan | Placera forum, Börsvärldens kommentarer, Aktiespararna | Stora och blandade. Kvaliteten beror helt på skribenten |
| Låg, används för stämning och kritik | Flashback, Reddit (t.ex. r/ISKbets) | Anonymt. Ibland guldkorn, oftast brus |
| **Används aldrig** | Telegram- och Discord-grupper, betalda "signaler", konton som säljer kurser | Hög risk för pump-and-dump |

### Kontrollera varje inlägg
**Röda tecken (hype):**
- 🚀, versaler och många utropstecken
- kursmål utan uträkning ("10x lätt")
- "en insider säger", "jag vet att…"
- brådska ("innan det är för sent")
- nytt konto eller få tidigare inlägg
- många liknande inlägg samtidigt
- inlägg nära en emission eller ett bolagsbesked
- inga källor
- avfärdar all kritik

**Gröna tecken:**
- länkar till primärkällor
- redovisar sitt innehav
- skiljer på fakta och egen gissning ("1+1, inte bekräftat")
- tar upp risker
- har haft rätt förut (se registret)

Ett inlägg med 2 eller fler röda tecken används bara för att se stämningen. Det följs inte upp som spår.

### Skribentregistret (`forumregister.md` i projektroten)
För skribenter som återkommer: alias, forum, vilka bolag de skriver om, och en **träffsäkerhetsanteckning**. Det fylls på efter hand: vad påstod skribenten, och stämde det? Exempel: författaren till Unibap-texten hade rätt om Leonardo-spåret men fel om att iX20 skulle sitta i Altair-1.
