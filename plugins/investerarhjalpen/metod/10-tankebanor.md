# Tankebanor – hur de bästa investerarna tänker

Informationsövertag är bara ett av fem sätt att slå marknaden, och det är det som är svårast att behålla. Den här filen samlar tankebanorna och säger hur verktyget använder dem.

## De fem övertagen
| Övertag | Fråga | Vem som är känd för det |
|---|---|---|
| **1. Information** | Vet vi något tidigare eller mer än andra? | Philip Fisher (scuttlebutt), hedgefonder med alternativ data |
| **2. Analys** | Tolkar vi samma fakta bättre? | Buffett och Munger, Michael Burry, kritiska blankare |
| **3. Beteende** | Agerar vi rationellt när andra är rädda eller giriga? | Howard Marks, Seth Klarman |
| **4. Tidshorisont** | Kan vi vänta 3–5 år när andra tänker i kvartal? | Buffett, Terry Smith |
| **5. Struktur** | Kan vi köpa det som stora aktörer inte får eller vill köpa? | Peter Lynch, Joel Greenblatt |

## Biblioteket
### 1. Information
| Tankebana | Vad den betyder | Hur vi gör |
|---|---|---|
| Scuttlebutt (Fisher) | Fråga kunder, leverantörer, konkurrenter och tidigare anställda | Vi läser deras offentliga kanaler (`natverk.md`). **Användaren** kan själv mejla IR eller ställa frågor på stämman: listan "Frågor till IR" i linsgenomgången |
| Alternativ data | Spår som syns före siffrorna | `metod/09-spar-och-signaler.md`: manifest, register, jobbannonser, apprankning |
| Leverantörskedjan | När en vinnare växer, vilka leverantörer följer med? | Temaanalysen (värdekedjan) och kundens kunder |
| Smarta pengar | Vad gör de som vet mest? | Insiders (nyhetskollen), nya stora ägare, fondernas innehav (halvårsrapporter), kända privatinvesterare på ägarlistorna |
| Blankarnas argument | De som tjänar på att bolaget faller har ofta gjort grundlig research | FI:s blankningsregister och blankningsrapporter. Läses som motbevis |

### 2. Analys
| Tankebana | Vad den betyder | Hur vi gör |
|---|---|---|
| **Andra nivåns tänkande** (Marks) | Det räcker inte att bolaget är bra. Är det *bättre än vad marknaden redan tror*? | Linsfråga 2: vad förväntar sig priset? Grovt nu, exakt med Börsdata senare (vilken tillväxt priset kräver) |
| **Inversion** (Munger) | "Tala om var jag kommer att dö, så går jag aldrig dit" | Linsfråga 3: pre-mortem. Det är 3 år fram och aktien har halverats. Varför? |
| Vallgrav (Buffett) | Vad hindrar konkurrenter från att ta kunderna? | Linsfråga 4: byteskostnader, flight heritage, certifieringar, nätverkseffekter |
| Kapitalallokering | Vad gör ledningen med pengarna? | Linsfråga 5: emissioner, förvärv, aktiverade kostnader, teckningsoptioner. Löftesrevisionen |
| **Redovisningens kvalitet** (Burry, blankare) | Stämmer vinsten med pengarna? | Linsfråga 6: rörelseresultat jämfört med kassaflöde, aktiverad utveckling, kundfordringar, varulager |
| Basfrekvenser (Mauboussin, Kahneman) | Hur brukar det gå för liknande bolag i samma läge? | Linsfråga 8: referensklassen. Hur många liknande bolag nådde lönsamhet utan ny emission? |
| Lynchs kategorier | Långsam växare, stabil, snabb växare, cyklisk, turnaround eller tillgångscase. Varje kategori säljs och följs upp olika | Linsfråga 1 |

### 3. Beteende
| Tankebana | Vad den betyder | Hur vi gör |
|---|---|---|
| Cykler och stämning (Marks) | Var i cykeln är bolaget, branschen och marknaden? Överdriven optimism eller pessimism? | Temafasen (metod 06) och testet av marknadens oro (metod 09) |
| Säkerhetsmarginal (Klarman) | Köp bara när det finns utrymme för fel | Påståenden på C-nivå väger lätt. Sälj- och utvärderingskriterier skrivs i förväg |
| Beslutsjournal och kalibrering (Tetlock) | Skriv förutsägelser med sannolikhet och följ upp. Det bygger omdöme | `journal.md` |
| Bekräftelsebias | Vi ser det vi vill se | Motbevislistan först, varje gång |

### 4. Tidshorisont
| Tankebana | Vad den betyder | Hur vi gör |
|---|---|---|
| Ägare, inte handlare | Tänk som om du köpte hela bolaget för 5 år | Turnaround-stegen och milstolpar med tidsangivelse (metod 07) |
| Katalysatorer | Vad får marknaden att se det vi ser, och när? | Linsfråga 7: katalysatorkalendern |

### 5. Struktur
| Tankebana | Vad den betyder | Hur vi gör |
|---|---|---|
| För små för fonderna | Fonder kan inte köpa illikvida småbolag | Skälet att vi letar bland småbolag (metod 02) |
| **Tvingade säljare** (Greenblatt) | Avknoppningar, indexändringar, emissionsgaranter som säljer, uppköp, lock-up som löper ut | Linsfråga 7 och temaskanningen: leta händelser där någon *måste* sälja oavsett pris |
| Speciella situationer | Avknoppningar, omstruktureringar, rekonstruktioner, uppköpserbjudanden | Egen screening senare |

### Övergripande
| Tankebana | Vad den betyder | Hur vi gör |
|---|---|---|
| Makro och likviditet (Druckenmiller) | Räntor och kapitalflöden styr särskilt småbolag | Temaskanningen: en kort makrorad (räntor, småbolagsindex) en gång i månaden |
| Reflexivitet (Soros) | Kursen kan påverka bolaget, till exempel genom att en hög kurs gör emissioner billigare | Notera om bolaget är beroende av kursen för sin finansiering |

## Linsgenomgången – 10 frågor
Besvaras i `tes.md` under "Linsgenomgång" vid varje bolagsanalys och uppdateras var tredje djupdykning. Korta svar.
1. **Kategori (Lynch):** vilken typ av case är det, och vad betyder det för vad vi ska följa?
2. **Förväntningar (andra nivån):** vad verkar priset redan räkna med? Vad måste hända för att det ska bli *bättre än förväntat*?
3. **Pre-mortem (inversion):** det är 3 år fram och aktien har halverats. De 3 troligaste orsakerna?
4. **Vallgrav:** vad hindrar kunderna från att byta? Hur stark är den, på en skala 0–2?
5. **Kapitalallokering:** emissioner, utspädning, teckningsoptioner, förvärv och aktiverade kostnader. Skapar ledningen värde per aktie?
6. **Redovisningens kvalitet:** rörelseresultat jämfört med kassaflöde, hur mycket som aktiveras, och kundfordringar och lager jämfört med försäljningen. Några varningar?
7. **Katalysatorer och tvingade säljare:** vad kan få marknaden att ändra uppfattning de närmaste 12 månaderna? Finns det någon som måste sälja?
8. **Basfrekvens:** vilken är referensklassen, och hur brukar det gå för den?
9. **Smarta pengar:** vilka äger, köper och säljer? Har kunniga ägare kommit in?
10. **Frågor till IR:** 3–5 frågor som användaren kan ställa till bolaget, per mejl eller på en stämma, och som skulle flytta viktiga påståenden.
