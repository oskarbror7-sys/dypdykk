# Dypdykk – utviklingsstatus

Sist oppdatert: 2026-11-18 (økt 2). En ny økt kan fortsette herfra.

## Prosjektstruktur
- `dypdykk/` (spillkilde): `template.html`, `extra.js`, `modes.js`, `icons.js`, `questions_all.js`, `q_ekstra.js`, `q_ekstra2.js`, `build_site.py`
- `dypdykk-data/` (data): `dypdykk_data/` (kode), `config/questions/` (spørsmål), `site/` (nettsiden som lastes opp)
- Bygg nettsiden: `python3 dypdykk/build_site.py` → `dypdykk-data/site/index.html`
- Datasett: `cd dypdykk-data && python3 -m dypdykk_data queue` → `site/data/*.json`

## Fullført
- [x] Innsamlingssystem: Wikidata (SPARQL, bånd + automatisk oppdeling), SSB KLASS, statiske lister
- [x] Rensing, alias, ID-basert duplikatfjerning, kollisjonsregler, «kjent alias stjeler ukjent hovednavn»
- [x] Nedgradering av «kjent for noe annet» (f.eks. Albert Camus som fotballspiller → Kjempeblekksprut)
- [x] Sjeldenhet: vektede persentiler, justerbare grenser, observerte frekvenser holdt adskilt
- [x] Sikker publisering: kontrollsvar, krympevakt, testdata-sperre, arkiv og rollback
- [x] Importkø med lagret fremdrift (`state/jobs.json`), fortsetter etter avbrudd, cache av alle kall
- [x] 21 tester (normalisering mot spillets JS, alias, duplikater, sjeldenhet, rettelser, 150k svar)
- [x] Spillet leser `data/index.json`, laster datasett ved behov, rask oppslag (Map), strengere «Mente du …?» for store lister
- [x] Fast dagskalender: hvert spørsmål har en startdag (`from`), så nye spørsmål aldri endrer tidligere dager; ingen gjentakelse innen ca. 3 uker (testet 60 dager)
- [x] Startdager lagres varig i `state/first_day.json`; nye datasett kommer med i dagens dykk fra dagen etter publisering
- [x] Ferdig normaliserte nøkler i datasettene (`k`) – raskere innlasting på mobil
- [x] Uendelig dykk og Boblebomben henter neste spørsmål i bakgrunnen (ingen ventetid mellom spørsmål/runder)
- [x] Etiketter med liten forbokstav (arter) vises med stor forbokstav; titler med årstall («1984») godtas
- [x] Kortformer for klubber («SK Brann» → «Brann», «FC Barcelona» → «Barcelona»)
- [x] 117 håndlagde spørsmål (16 nye i `q_ekstra2.js`, med i dagens dykk fra 19. november)

## Faktisk importert og publisert (ekte data, 17.–18. nov. 2026)
| ID | Spørsmål | Kategori | Svar | Skrivemåter |
|---|---|---|---|---|
| alpinister | Nevn en alpinist | Sport | 4 542 | 7 307 |
| artister | Nevn en sanger eller artist | Underholdning | 16 804 | 43 097 |
| astronauter | Nevn en astronaut eller kosmonaut | Vitenskap | 870 | 2 896 |
| aviser | Nevn en norsk avis | Samfunn | 821 | 1 157 |
| band | Nevn et band eller en musikkgruppe | Underholdning | 11 841 | 15 652 |
| basketballspillere | Nevn en basketballspiller | Sport | 15 467 | 27 250 |
| bilmerker | Nevn et bilmerke | Samfunn | 3 536 | 5 403 |
| boker | Nevn en bok  roman eller et skuespill (tittel) | Kultur | 5 316 | 11 952 |
| boksere | Nevn en bokser | Sport | 5 015 | 9 758 |
| britiske-statsministre | Nevn en britisk statsminister | Samfunn | 60 | 407 |
| cocktailer | Nevn en cocktail | Kultur | 171 | 224 |
| f1-forere | Nevn en Formel 1-fører | Sport | 1 076 | 2 727 |
| filmer-1990 | Nevn en film fra 1990-tallet | Underholdning | 11 075 | 16 025 |
| filmer | Nevn en film | Underholdning | 33 789 | 55 033 |
| filosofer | Nevn en filosof | Kultur | 1 917 | 9 047 |
| fjell-4000 | Nevn et fjell over 4000 meter | Geografi | 4 895 | 6 248 |
| flyplasser-norge | Nevn en flyplass i Norge | Geografi | 104 | 695 |
| forfattere | Nevn en forfatter | Kultur | 8 952 | 33 833 |
| fotballklubber | Nevn en fotballklubb | Sport | 15 287 | 28 467 |
| fotballspillere | Nevn en fotballspiller | Annet | 225 123 | 312 037 |
| fotballstadioner | Nevn en fotballstadion | Sport | 2 175 | 3 728 |
| fotballtrenere | Nevn en fotballtrener | Sport | 31 712 | 49 147 |
| franske-byer | Nevn en by i Frankrike | Geografi | 2 327 | 4 005 |
| fugler | Nevn en fugl | Natur | 10 409 | 24 923 |
| fylker | Nevn et norsk fylke | Geografi | 15 | 22 |
| fysikere | Nevn en fysiker | Vitenskap | 2 976 | 9 764 |
| grunnstoffer | Nevn et grunnstoff | Vitenskap | 118 | 720 |
| handballspillere | Nevn en håndballspiller | Sport | 6 135 | 10 369 |
| hesteraser | Nevn en hesterase | Natur | 520 | 806 |
| hovedsteder | Nevn en hovedstad | Geografi | 204 | 952 |
| hunderaser | Nevn en hunderase | Natur | 715 | 1 864 |
| idretter | Nevn en idrett | Sport | 387 | 1 137 |
| instrumenter | Nevn et musikkinstrument | Kultur | 565 | 2 050 |
| ishockeyspillere | Nevn en ishockeyspiller | Sport | 14 268 | 23 870 |
| italienske-byer | Nevn en by i Italia (kommune) | Geografi | 7 825 | 8 906 |
| katteraser | Nevn en katterase | Natur | 126 | 279 |
| kommuner | Nevn en norsk kommune | Annet | 357 | 653 |
| komponister | Nevn en komponist | Kultur | 4 551 | 16 297 |
| land | Nevn et land | Geografi | 197 | 1 606 |
| langrenn | Nevn en norsk langrennsløper | Sport | 751 | 1 564 |
| malere | Nevn en maler | Kultur | 2 474 | 32 806 |
| merkevarer | Nevn et merke (brand) | Samfunn | 4 470 | 8 671 |
| museer-norge | Nevn et museum i Norge | Kultur | 625 | 1 344 |
| nobelprisvinnere | Nevn en nobelprisvinner | Vitenskap | 898 | 3 399 |
| norske-artister | Nevn en norsk sanger eller artist | Underholdning | 1 841 | 4 516 |
| norske-band | Nevn et norsk band | Underholdning | 1 831 | 2 232 |
| norske-elver | Nevn en norsk elv | Geografi | 2 604 | 3 212 |
| norske-filmer | Nevn en norsk film | Underholdning | 1 590 | 2 653 |
| norske-fjell | Nevn et norsk fjell | Geografi | 16 440 | 17 715 |
| norske-forfattere | Nevn en norsk forfatter | Kultur | 4 416 | 8 410 |
| norske-fotballklubber | Nevn en norsk fotballklubb | Sport | 515 | 1 690 |
| norske-fotballspillere | Nevn en norsk fotballspiller | Sport | 5 886 | 8 904 |
| norske-innsjoer | Nevn en norsk innsjø | Geografi | 4 464 | 5 767 |
| norske-oyer | Nevn en norsk øy | Geografi | 9 348 | 10 117 |
| norske-politikere | Nevn en norsk politiker | Samfunn | 14 673 | 21 164 |
| norske-selskaper | Nevn et norsk selskap | Samfunn | 2 537 | 5 017 |
| norske-skuespillere | Nevn en norsk skuespiller | Underholdning | 2 680 | 5 465 |
| norske-tv-serier | Nevn en norsk TV-serie | Underholdning | 516 | 928 |
| nyhetsbyraer | Nevn et nyhetsbyrå | Samfunn | 537 | 989 |
| oppfinnere | Nevn en oppfinner | Vitenskap | 1 084 | 4 172 |
| oscarfilmer | Nevn en film som har vunnet Oscar for beste film | Underholdning | 98 | 206 |
| oster-verden | Nevn en ostesort | Kultur | 567 | 846 |
| paver | Nevn en pave | Kultur | 266 | 1 827 |
| romerske-keisere | Nevn en romersk keiser | Kultur | 103 | 625 |
| sanger | Nevn en sang (tittel) | Underholdning | 11 121 | 14 982 |
| selskaper-for-2000 | Nevn et selskap grunnlagt før 2000 | Samfunn | 3 281 | 11 058 |
| selskaper | Nevn et selskap | Samfunn | 4 106 | 13 511 |
| sjakkspillere | Nevn en sjakkspiller | Sport | 7 016 | 12 296 |
| skihoppere | Nevn en skihopper | Sport | 2 672 | 5 053 |
| skiskyttere | Nevn en skiskytter | Sport | 3 928 | 7 060 |
| skuespillere | Nevn en skuespiller | Underholdning | 14 051 | 35 926 |
| spillfigurer | Nevn en figur fra et videospill | Underholdning | 1 369 | 2 989 |
| sprak | Nevn et språk | Kultur | 905 | 5 234 |
| stavkirker | Nevn en norsk stavkirke | Kultur | 99 | 319 |
| storbyer | Nevn en by med over 100 000 innbyggere | Geografi | 3 204 | 9 230 |
| tennisspillere | Nevn en tennisspiller | Sport | 10 614 | 16 681 |
| tv-serier | Nevn en TV-serie | Underholdning | 19 953 | 26 309 |
| tyske-byer | Nevn en by i Tyskland | Geografi | 2 088 | 2 867 |
| universiteter | Nevn et universitet | Samfunn | 942 | 4 833 |
| us-presidenter | Nevn en amerikansk president | Samfunn | 45 | 308 |
| usa-byer | Nevn en by i USA | Geografi | 10 097 | 28 660 |
| valutaer | Nevn en valuta | Samfunn | 356 | 1 184 |
| verdens-elver | Nevn en elv (minst 1000 km lang) | Geografi | 323 | 1 343 |
| verdens-innsjoer | Nevn en innsjø (i hele verden) | Geografi | 1 217 | 2 754 |
| verdens-oyer | Nevn en øy (i hele verden) | Geografi | 3 476 | 8 393 |
| videospill | Nevn et videospill | Underholdning | 12 990 | 21 769 |
| vulkaner | Nevn en vulkan | Geografi | 1 215 | 2 438 |

**Sum: 87 datasett  648 525 godkjente svar  1 139 749 godkjente skrivemåter.**

## Pågår / gjenstår
- Importkøen ble kjørt i Claude-miljøet 18. nov. Gjenstående eller avbrutte kategorier fortsetter med `./automation/nattlig-import.sh` (køen husker hvor den slapp).
- Utelatt foreløpig (for tunge spørringer for Wikidata): `historiske-personer`, `malerier`. `pattedyr` (113 arter) ble stoppet – det håndlagde pattedyr-spørsmålet brukes.
- Datasett med mange oppføringer «til manuell kontroll» (f.eks. norske-oyer: like navn på flere øyer) er publisert, men bør gås gjennom i `review/`.

## Spillmoduser
| Modus | Status |
|---|---|
| Dagens dykk | ferdig |
| Uendelig dykk (øving) | ferdig |
| Uendelig dykk | ferdig (3 liv, tilfeldige spørsmål, egen rekord) – testet |
| Arkiv | ferdig (alle tidligere dagens dykk, samme spørsmål som dagen, teller ikke på rekken) – testet |
| Temapakker | alle seks pakker åpne (Ord og myter, Film, Sport, Geografi, Musikk, Norge) – testet |
| Boblebomben | ferdig lokalt (2–8 spillere på én enhet + datamotstandere, skjult lunte, sjeldne svar gir mer tid, duplikatsperre) – testet. Online-rom krever server |
| Venner | ferdig via lenke/kode (`?venn=`), dagens tavle – testet. Server-tavle krever server |
| Garderobe / dykkekompis | ferdig (velg opptjent kompis, svømmer ved dykkeren) – testet |
| Sammenlign med andre / andel spillere per svar | krever server – fortsatt «Kommer snart» |
| Innlogging/synk | krever server – fortsatt «Kommer snart» |

## Testresultater
- 21 Python-tester OK (inkl. 3 mot ekte data: Messi/Ronaldo/Haaland/Mbappé = Tare, Camus = Kjempeblekksprut, alle 6 nivåer i bruk, 357 kommuner)
- Nettlesertest av alle moduser på PC (1400×860) og mobil (390×760): ingen JS-feil
- Feiltilstander: datasett som ikke lastes/er ødelagt byttes ut; uten index.json virker 89 innebygde spørsmål; tomme og ugyldige svar avvises

## Oppdagede og rettede feil
- «Messi» ga ukjent spiller med hovednavn «Messi» → kjent alias vinner nå over ukjent hovednavn
- `wdt:P54` ga bare nåværende klubb → bruker `p:P54` (alle lag)
- Wikidata avbrøt store svar midt i (ugyldig JSON/IncompleteRead) → automatisk oppdeling
- C, C++ og C# ble samme svar → egen normalisering
- To håndlagde spørsmål hadde 7 nivågrupper → sperre i spillet + rettet data
- Kappløp ved start av dykk fra en side → rettet
- NRK registrert som avis, Tesla ikke som bilprodusent → overstyringer
- Dobbelt sitelink-filter gjorde spørringer tregere → fjernet (båndene håndterer minimum)
- USA-byer: Los Angeles har typen «charter city» → lagt til; småsteder som «Toronto, Ohio» ga Kjempeblekksprut for «Toronto» → kortnavnet fjernet
- Franske byer: spørringen var for stor → bare kommuner over 5000 innbyggere + Paris
- Øyer, universiteter, selskaper: for snevre typekjeder (manglet Island, NTNU, Telenor) → rettet
- Fysikere: Newton manglet, «Charles Darwin» ga fysikeren C. G. Darwin → rettet
- Merkevarer, bøker, stadioner, spillfigurer, fugler, norske øyer/artister/filmer/klubber: kontrollsvar manglet → overstyringer

## Kjente begrensninger
- Claude-miljøet stopper bakgrunnsprosesser kort tid etter at en økt avsluttes. Langvarige importer må kjøres på egen maskin/server (se README «Kjøre automatisk»).
- Wikipedia-sidevisninger: API svarte 429; ikke brukt ennå. no.wikipedia.org er ikke tillatt i miljøet.
- Fotballdatasettet er 10 MB (3,5 MB komprimert), lastes bare når spørsmålet trengs. Bør deles opp ved behov.

## Neste anbefalte handling
Se «Pågår». Etter køen: kontroller `review/`, publiser, bygg nettsiden og last opp `site/` til Netlify.
