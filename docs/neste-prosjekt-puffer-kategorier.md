# Neste prosjekt: Boblebomben-kategorier inspirert av Krillion Puffer Party

Kartlagt 18. november 2026. Dette er en plan, ikke kode ennå.

## Hva Puffer Party gjør annerledes enn dagens dykk

Dette er kategoriene som faktisk dukket opp i en runde Puffer Party (8–10 spillere, Quick Play):

| # | Kategori i Puffer Party | Hva slags kategori |
|---|---|---|
| 1 | A way to listen to music | Hverdag / tjenester |
| 2 | A math symbol | Hverdag / skole |
| 3 | A Pixar character | Popkultur / figurer |
| 4 | A way to video call | Hverdag / apper |
| 5 | A European Cup / Champions League winner | Sport |
| 6 | A term of endearment | Språk |
| 7 | A city in England | Geografi |
| 8 | An item of clothing | Hverdag |
| 9 | A US president | Historie |
| 10 | A type of vinegar | Mat |
| 11 | A Sonic character | Popkultur / spill |
| 12 | A chip (crisp) flavour | Mat / merkevarer |
| 13 | A candy | Mat / merkevarer |
| 14 | An email provider | Hverdag / tjenester |

Det Krillion selv sier om utvalget (FAQ): svarlistene settes sammen fra flere kilder (ordbøker, wikisider, leksikon). Sjeldenhet regnes ut maskinelt der det går. Ellers brukes en språkmodell pluss en manuell runde. I Puffer Party trekkes lunta tilfeldig mellom 10 og 30 sekunder. Den er felles for hele rommet, og spilleren som tar over, får alltid minst 8 sekunder.

**Lærdommen:** Kategoriene i Puffer Party er raske og hverdagslige. Alle i rommet skal kunne komme på noe innen 2–3 sekunder, mens de sjeldne svarene gir ekte dybde. Over halvparten er *ikke* rene Wikidata-klasser: kjælenavn, potetgullsmaker, godteri, måter å høre musikk på. Boblebomben trenger flere slike, i tillegg til de store kunnskapslistene vi har.

## Norsk kartlegging

Status:
- ✅ **testet mot Wikidata 18.11.** Spørringen finner riktige svar og kan legges rett i `tools/make_configs.py`.
- ⚠️ **Wikidata, men spørringen må rettes.** Riktig klasse eller egenskap er ikke funnet ennå.
- 📝 **Kuratert liste.** Lages for hånd eller fra en åpen ordliste (se kilder nederst), med sjeldenhet fra frekvens eller manuell vurdering.
- 🟦 **Finnes allerede** i Dypdykk.

### 1. Hverdag, apper og tjenester
| Norsk spørsmål | Inspirert av | Kilde / spørring | Status |
|---|---|---|---|
| Nevn en måte å høre på musikk (strømmetjeneste, app, apparat) | listen to music | Kuratert: Spotify, Tidal, WiMP, radio, kassett … | 📝 |
| Nevn en app for videosamtale | video call | Kuratert | 📝 |
| Nevn en e-posttjeneste | email provider | Kuratert | 📝 |
| Nevn et sosialt medium | (ny) | `?item wdt:P31/wdt:P279* wd:Q3220391` (187 treff, Facebook og TikTok finnes) | ✅ |
| Nevn en nettleser | (ny) | `?item wdt:P31/wdt:P279* wd:Q6368` (133 treff, Firefox må legges til som alias) | ✅ |
| Nevn et klesplagg | clothing | Kuratert: Norsk ordbank + manuell liste | 📝 |
| Nevn et yrke | (ny) | Wikidata occupation Q28640 gir bare 316 treff med høy terskel. Bruk heller kuratert liste fra SSB/STYRK | 📝 |
| Nevn et matematisk symbol | math symbol | Kuratert fra Unicode-blokken «Mathematical Operators», med norske navn | 📝 |
| Nevn en emoji | (ny) | Unicode CLDR har offisielle norske emoji-navn (åpen lisens) | 📝 |
| Nevn et kortspill | (ny) | `?item wdt:P31/wdt:P279* wd:Q142714` (427 treff) | ✅ |
| Nevn en fobi | (ny) | `?item wdt:P279+ wd:Q175854` (82 treff) | ✅ |
| Nevn en sjakkåpning | (ny) | `?item wdt:P31 wd:Q103632` (308 treff) | ✅ |

### 2. Mat og merkevarer
| Norsk spørsmål | Inspirert av | Kilde / spørring | Status |
|---|---|---|---|
| Nevn en potetgullsmak | chip flavour | Kuratert: Maarud, Kims, Sørlandschips + utenlandske | 📝 |
| Nevn et godteri eller en sjokolade | candy | Kuratert: Freia, Nidar, Cloetta + internasjonale | 📝 |
| Nevn en type eddik | vinegar | `?item wdt:P279+ wd:Q41354` (40 treff) | ✅ |
| Nevn en brus eller leskedrikk | (ny) | Wikidata gir for få (21). Kuratert: Solo, Pepsi Max, Mozell … | 📝 |
| Nevn et pålegg | (ny) | Kuratert: brunost, leverpostei, Nugatti … | 📝 |
| Nevn en frokostblanding | (ny) | Kuratert | 📝 |
| Nevn en pizzatopping | (ny) | Kuratert | 📝 |
| Nevn en norsk butikkjede | (ny) | `?item wdt:P31/wdt:P279* wd:Q507619 ; wdt:P17 wd:Q20` (Wikidata svarte ikke under testen) | ⚠️ |
| Nevn en bilmodell | (ny) | `?item wdt:P31/wdt:P279* wd:Q3231690` (3181 treff) | ✅ |

### 3. Popkultur: figurer fra én verden
Krillion bruker mange «figur fra X»-kategorier. Det fungerer godt i Boblebomben fordi kategorien er smal, men alle kjenner noen.

| Norsk spørsmål | Inspirert av | Kilde / spørring | Status |
|---|---|---|---|
| Nevn en Pixar-figur | Pixar character | `?item wdt:P1441 ?w . ?w wdt:P272 wd:Q127552` (45 treff) | ✅ |
| Nevn en Disney-figur | (ny) | Figur i verk fra Walt Disney Pictures (160 treff) | ✅ |
| Nevn en Harry Potter-figur | (ny) | `?item wdt:P1080 wd:Q5410773` (469 treff) | ✅ |
| Nevn en Simpsons-figur | (ny) | `?item wdt:P1441 wd:Q886` (211 treff) | ✅ |
| Nevn en Sonic-figur | Sonic character | Spørringen må skrives om (feil i testen) | ⚠️ |
| Nevn en Marvel-figur | (ny) | P1080 Q931597 ga bare 1. Riktig «fictional universe» må finnes | ⚠️ |
| Nevn en Star Wars-figur | (ny) | Q13442814 var feil QID | ⚠️ |
| Nevn en Pokémon | (ny) | Q3966183 ga 0. Riktig klasse må finnes | ⚠️ |
| Nevn en figur fra Donald Duck & Co | (norsk vri) | Wikidata (Disney-tegneserier) + kuratert norske navn (Onkel Skrue, Fetter Anton) | ⚠️ |
| Nevn en norsk tegneseriefigur | (norsk vri) | Kuratert: Nemi, Pondus, Lunch, Pelle Parafin … | 📝 |

### 4. Sport
| Norsk spørsmål | Inspirert av | Kilde / spørring | Status |
|---|---|---|---|
| Nevn en klubb som har vunnet Champions League / Europacupen | European Cup winner | `?s wdt:P3450 wd:Q18756 ; wdt:P1346 ?item` (24 vinnere) | ✅ |
| Nevn en vinner av Ballon d'Or | (ny) | `?item wdt:P166 wd:Q166177` (48 treff) | ✅ |
| Nevn en seriemester i norsk fotball | (norsk vri) | Wikidata-sesonger for Eliteserien | ⚠️ |
| Nevn en by som har arrangert OL | (ny) | Spørringen ga 0. Kan bruke P276 eller P17 på hvert enkelt OL | ⚠️ |
| Nevn et NHL-, NBA- eller NFL-lag | (ny) | P118-liga. Wikidata begrenset antall forespørsler under testen | ⚠️ |

### 5. Geografi og historie
| Norsk spørsmål | Inspirert av | Kilde / spørring | Status |
|---|---|---|---|
| Nevn en by i England | city in England | Snevre inn `britiske-byer` til England (Q21) | 🟦 → variant |
| Nevn en amerikansk president | US president | Finnes som `us-presidenter` | 🟦 |
| Nevn en norsk statsminister | (norsk vri) | Q1061829 var feil QID for vervet | ⚠️ |
| Nevn en norsk konge eller dronning | (norsk vri) | Kuratert (kort liste, sjeldenhet manuelt) | 📝 |

### 6. Språk
| Norsk spørsmål | Inspirert av | Kilde | Status |
|---|---|---|---|
| Nevn et kjælenavn (vennen, skatten, pusen …) | term of endearment | Kuratert | 📝 |
| Nevn et ord som slutter på «-sjon» / begynner på «sk-» | (ny) | Norsk ordbank (Språkbanken, CC BY) | 📝 |
| Nevn et palindrom | (ny) | Norsk ordbank, filtrert | 📝 |
| Nevn et dialektord | (ny) | Kuratert | 📝 |

## Arbeidsplan

1. **Wikidata-kategorier merket ✅** (15 stk.) legges i `KATALOG` i `tools/make_configs.py`, med kontrollsvar. Importen på GitHub publiserer dem.
2. **Wikidata-kategorier merket ⚠️:** finn riktig klasse eller egenskap, test med en tellespørring, og flytt dem deretter til ✅.
3. **Kuraterte lister (📝):** en ny kildetype `"type": "liste"` i datainnsamlingen. Den leser `data/kuratert/<id>.json` med svar, alias og sjeldenhet fra 0 til 5. Lisens og kilde føres i filen.
4. **Merk kategorier som passer i Boblebomben:** feltet `"modes"` får `"party"` for de raske hverdagskategoriene. Smale lister som Pixar-figurer passer bedre i Boblebomben enn i dagens dykk.
5. **Lunta:** vurder Krillions modell med én felles lunte som overtas, og minst 8 sekunder til den som tar over. Den kan bli et valg i romreglene.

## Kilder
- Krillion Puffer Party, observert spill 17.11.2026, og FAQ på krillion.io/faq (tekst parafrasert).
- Wikidata (CC0). Tellespørringene ble kjørt 18.11.2026.
- Norsk ordbank / Språkbanken (CC BY 4.0) for ordkategorier.
- Unicode CLDR (Unicode-lisens) for emoji- og symbolnavn.
