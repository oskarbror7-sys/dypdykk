"""Lager config/questions/*.json for kategoribiblioteket.

Hver kategori er én linje i KATALOG. Felles standarder fylles inn automatisk.
Kontrollsvarene (inn/ut) er vakter: treffer et Wikidata-oppslag feil kategori,
stopper publiseringen. Kjør på nytt etter endringer: python3 tools/make_configs.py
(Eksisterende filer for kommuner og fotballspillere røres ikke.)
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "config", "questions")
NB = ["nb", "nn", "mul", "en"]
NB_ONLY = ["nb", "nn", "no"]
WD = "Kilde: Wikidata (CC0)"
AUTO = {"mode": "auto"}
# Lavere krav til antall språkutgaver: flere gyldige (sjeldne) svar. Nivåskalaen «auto» sørger for at
# de nye, lite kjente svarene havner som sjeldne, ikke som vanlige.
MINSL = {"arkitekter": 6, "filosofer": 10, "kjemikere": 8, "komikere": 5, "kriger": 8, "kunstmuseer": 5,
         "instrumenter": 5, "malere": 10, "matematikere": 8, "musikksjangere": 6, "oppfinnere": 6,
         "programmeringssprak": 4, "religioner": 4, "retter": 6, "slag": 8, "sprak": 10, "sykdommer": 8,
         "universiteter": 8, "valutaer": 3, "verdens-innsjoer": 6, "skyskrapere": 4, "slott": 5, "idretter": 3,
         "spillkonsoller": 3, "superhelter": 3, "rappere": 4, "oppdagelsesreisende": 5, "operaer": 3,
         "tv-kanaler": 3, "youtubere": 3, "hav": 2, "orkener": 2, "nettlesere": 2, "sosiale-medier": 2,
         "vulkaner": 3, "disney-figurer": 2, "flyselskaper": 3, "brettspill": 2, "fysikere": 6,
         "animasjonsfilmer": 6, "pastatyper": 1, "cocktailer": 1, "kortspill": 1, "hesteraser": 1,
         "hunderaser": 1, "katteraser": 1, "fobier": 1, "japanske-byer": 1, "oster-verden": 2,
         "musikkfestivaler": 1, "golfspillere": 2, "fotballstadioner": 2, "verdensarv": 1}
PCT = {"mode": "percent", "at": [0.04, 0.14, 0.32, 0.56, 0.84]}


def rank(n):
    """Grenser i absolutt plass for store lister (n = omtrentlig antall)."""
    return {"mode": "rank", "at": [max(5, n // 400), max(20, n // 70), max(80, n // 15), max(300, n // 5), max(900, n // 2)]}


def bands(big):
    return ([[0, 1], [2, 2], [3, 4], [5, 9], [10, 29], [30, 100000]] if big == "xl" else
            [[0, 2], [3, 9], [10, 100000]] if big == "l" else [[0, 100000]])


# (id, spørsmål, kategori, norsk, where, minst_sitelinks, størrelse, label_langs, cuts, inn, ut, min_count)
KATALOG = [
    # --- Geografi ---
    ("land", "Nevn et land", "Geografi", False,
     "?item wdt:P31 wd:Q3624078 . FILTER NOT EXISTS { ?item wdt:P576 ?slutt . }", 0, "s", NB, PCT,
     ["Norge", "Sverige", "USA", "Tyskland", "Brasil"], ["Oslo", "Europa"], 180),
    ("hovedsteder", "Nevn en hovedstad", "Geografi", False,
     "?land wdt:P31 wd:Q3624078 ; wdt:P36 ?item . FILTER NOT EXISTS { ?land wdt:P576 ?slutt . }", 0, "s", NB, PCT,
     ["Oslo", "Stockholm", "Paris", "Tokyo"], ["Norge", "Bergen"], 170),
    ("storbyer", "Nevn en by med over 100 000 innbyggere", "Geografi", False,
     "?item wdt:P31/wdt:P279 wd:Q515 ; wdt:P1082 ?pop . FILTER(?pop >= 100000)", 3, "l", NB, rank(4000),
     ["Oslo", "London", "New York", "Bergen"], ["Norge", "Europa"], 1500),
    ("tyske-byer", "Nevn en by i Tyskland", "Geografi", False,
     "VALUES ?t { wd:Q42744322 wd:Q1549591 wd:Q515 } ?item wdt:P31 ?t ; wdt:P17 wd:Q183 .", 0, "s", NB, PCT,
     ["Berlin", "München", "Hamburg", "Köln"], ["Wien", "Tyskland"], 300),
    ("fylker", None, None, None, None, None, None, None, None, None, None, None),  # egen (SSB)
    ("norske-oyer", "Nevn en norsk øy", "Geografi", True,
     "?item wdt:P31/wdt:P279* wd:Q23442 ; wdt:P17 wd:Q20 .", 1, "l", NB_ONLY + ["mul", "en"], PCT,
     ["Senja", "Hitra", "Karmøy", "Svalbard"], ["Oslo", "Island"], 300),
    ("norske-fjell", "Nevn et norsk fjell", "Geografi", True,
     "?item wdt:P31 wd:Q8502 ; wdt:P17 wd:Q20 .", 1, "l", NB_ONLY + ["mul", "en"], PCT,
     ["Galdhøpiggen", "Glittertind", "Snøhetta"], ["Mount Everest", "Oslo"], 500),
    ("norske-innsjoer", "Nevn en norsk innsjø", "Geografi", True,
     "?item wdt:P31 wd:Q23397 ; wdt:P17 wd:Q20 .", 1, "l", NB_ONLY + ["mul", "en"], PCT,
     ["Mjøsa", "Femunden", "Hornindalsvatnet"], ["Vänern", "Oslo"], 300),
    ("norske-elver", "Nevn en norsk elv", "Geografi", True,
     "?item wdt:P31 wd:Q4022 ; wdt:P17 wd:Q20 .", 1, "l", NB_ONLY + ["mul", "en"], PCT,
     ["Glomma", "Numedalslågen", "Altaelva"], ["Donau", "Oslo"], 200),
    ("verdens-elver", "Nevn en elv (minst 1000 km lang)", "Geografi", False,
     "?item wdt:P31 wd:Q4022 ; wdt:P2043 ?len . FILTER(?len >= 1000)", 0, "s", NB, PCT,
     ["Nilen", "Amazonas", "Donau", "Rhinen"], ["Glomma", "Oslo"], 100),
    # --- Sport ---
    ("norske-fotballspillere", "Nevn en norsk fotballspiller", "Sport", True,
     "?item p:P106/ps:P106 wd:Q937857 ; wdt:P31 wd:Q5 ; wdt:P1532|wdt:P27 wd:Q20 .", 0, "l", NB, rank(5000),
     ["Erling Haaland", "Ole Gunnar Solskjær", "Ada Hegerberg"], ["Lionel Messi", "Magnus Carlsen"], 2000),
    ("fotballklubber", "Nevn en fotballklubb", "Sport", False,
     "?item wdt:P31 wd:Q476028 .", 3, "xl", NB, rank(30000),
     ["Rosenborg", "Liverpool", "Real Madrid", "Brann"], ["Lionel Messi", "Norge"], 5000),
    ("norske-fotballklubber", "Nevn en norsk fotballklubb", "Sport", True,
     "?item wdt:P31 wd:Q476028 ; wdt:P17 wd:Q20 .", 0, "l", NB, PCT,
     ["Rosenborg", "Brann", "Molde", "Vålerenga"], ["Liverpool", "Oslo"], 300),
    ("fotballstadioner", "Nevn en fotballstadion", "Sport", False,
     "?item wdt:P31/wdt:P279* wd:Q1154710 .", 3, "l", NB, rank(5000),
     ["Ullevaal stadion", "Wembley Stadium", "Camp Nou", "Lerkendal stadion"], ["Rosenborg", "Oslo"], 500),
    ("fotballtrenere", "Nevn en fotballtrener", "Sport", False,
     "?item p:P106/ps:P106 wd:Q628099 ; wdt:P31 wd:Q5 .", 3, "xl", NB, rank(30000),
     ["José Mourinho", "Alex Ferguson", "Ståle Solbakken", "Pep Guardiola"], ["Lionel Messi", "Magnus Carlsen"], 3000),
    ("f1-forere", "Nevn en Formel 1-fører", "Sport", False,
     "?item p:P106/ps:P106 wd:Q10841764 ; wdt:P31 wd:Q5 .", 0, "s", NB, PCT,
     ["Michael Schumacher", "Lewis Hamilton", "Ayrton Senna", "Max Verstappen"], ["Lionel Messi", "Petter Northug"], 300),
    ("langrenn", "Nevn en norsk langrennsløper", "Sport", True,
     "?item p:P106/ps:P106 wd:Q13382608 ; wdt:P27 wd:Q20 .", 0, "s", NB, PCT,
     ["Bjørn Dæhlie", "Marit Bjørgen", "Petter Northug", "Johannes Høsflot Klæbo"], ["Erling Haaland", "Magnus Carlsen"], 200),
    ("skiskyttere", "Nevn en skiskytter", "Sport", False,
     "?item p:P106/ps:P106 wd:Q16029547 ; wdt:P31 wd:Q5 .", 0, "l", NB, PCT,
     ["Ole Einar Bjørndalen", "Johannes Thingnes Bø", "Martin Fourcade"], ["Bjørn Dæhlie", "Erling Haaland"], 300),
    ("tennisspillere", "Nevn en tennisspiller", "Sport", False,
     "?item p:P106/ps:P106 wd:Q10833314 ; wdt:P31 wd:Q5 .", 2, "l", NB, rank(15000),
     ["Roger Federer", "Serena Williams", "Casper Ruud", "Rafael Nadal"], ["Lionel Messi", "Magnus Carlsen"], 2000),
    ("sjakkspillere", "Nevn en sjakkspiller", "Sport", False,
     "?item p:P106/ps:P106 wd:Q10873124 ; wdt:P31 wd:Q5 .", 2, "l", NB, rank(5000),
     ["Magnus Carlsen", "Garri Kasparov", "Bobby Fischer"], ["Lionel Messi", "Roger Federer"], 500),
    # --- Underholdning ---
    ("filmer", "Nevn en film", "Underholdning", False,
     "?item wdt:P31 wd:Q11424 .", 8, "xl", NB, rank(60000),
     ["Titanic", "Avatar", "Kon-Tiki", "Star Wars"], ["Norge", "Leonardo DiCaprio"], 10000),
    ("filmer-1990", "Nevn en film fra 1990-tallet", "Underholdning", False,
     "?item wdt:P31 wd:Q11424 ; wdt:P577 ?d . FILTER(YEAR(?d) >= 1990 && YEAR(?d) <= 1999)", 3, "l", NB, rank(15000),
     ["Titanic", "Pulp Fiction", "Jurassic Park", "Forrest Gump"], ["Avatar", "Star Wars"], 2000),
    ("norske-filmer", "Nevn en norsk film", "Underholdning", True,
     "?item wdt:P31 wd:Q11424 ; wdt:P495 wd:Q20 . FILTER(EXISTS { VALUES ?nl { wd:Q9043 wd:Q25167 wd:Q25164 } ?item wdt:P364 ?nl . } || NOT EXISTS { ?item wdt:P364 ?ol . })", 0, "l", NB, PCT,
     ["Kon-Tiki", "Max Manus", "Bølgen", "Flåklypa Grand Prix"], ["Titanic", "Norge"], 500),
    ("tv-serier", "Nevn en TV-serie", "Underholdning", False,
     "?item wdt:P31 wd:Q5398426 .", 3, "xl", NB, rank(30000),
     ["Friends", "Skam", "Breaking Bad", "Game of Thrones"], ["Titanic", "Norge"], 5000),
    ("norske-tv-serier", "Nevn en norsk TV-serie", "Underholdning", True,
     "?item wdt:P31 wd:Q5398426 ; wdt:P495 wd:Q20 .", 0, "l", NB, PCT,
     ["Skam", "Lilyhammer", "Exit", "Okkupert"], ["Friends", "Titanic"], 200),
    ("skuespillere", "Nevn en skuespiller", "Underholdning", False,
     "?item p:P106/ps:P106 wd:Q33999 ; wdt:P31 wd:Q5 .", 20, "xl", NB, rank(40000),
     ["Leonardo DiCaprio", "Meryl Streep", "Aksel Hennie", "Tom Hanks"], ["Lionel Messi", "Norge"], 5000),
    ("norske-skuespillere", "Nevn en norsk skuespiller", "Underholdning", True,
     "?item p:P106/ps:P106 wd:Q33999 ; wdt:P27 wd:Q20 .", 0, "l", NB, rank(6000),
     ["Aksel Hennie", "Liv Ullmann", "Kristoffer Joner"], ["Leonardo DiCaprio", "Erling Haaland"], 800),
    # «Artist» på norsk er bredt: sangere, rappere, DJ-er og låtskrivere fra hele verden (minst 10 Wikipedia-utgaver),
    # pluss alle norske musikere og komikere/underholdere uansett hvor kjente de er internasjonalt.
    ("artister", "Nevn en sanger eller artist", "Underholdning", False,
     "VALUES ?occ { wd:Q177220 wd:Q2252262 wd:Q488205 wd:Q130857 } ?item p:P106/ps:P106 ?occ ; wdt:P31 wd:Q5 .", 10, "xl", NB, rank(40000),
     ["Michael Jackson", "Taylor Swift", "Sissel Kyrkjebø", "Madonna", "Herman Flesvig", "Martin Lepperød"], ["Lionel Messi", "Norge"], 5000),
    ("norske-artister", "Nevn en norsk sanger eller artist", "Underholdning", True,
     "VALUES ?occ { wd:Q177220 wd:Q2252262 wd:Q488205 wd:Q130857 wd:Q639669 wd:Q753110 wd:Q855091 wd:Q245068 wd:Q18545066 } ?item p:P106/ps:P106 ?occ ; wdt:P27 wd:Q20 ; wdt:P31 wd:Q5 .", 0, "l", NB, rank(4000),
     ["Sissel Kyrkjebø", "Alan Walker", "Sigrid", "Aurora", "Herman Flesvig", "Martin Lepperød"], ["Taylor Swift", "Erling Haaland"], 500),
    ("band", "Nevn et band eller en musikkgruppe", "Underholdning", False,
     "VALUES ?t { wd:Q215380 wd:Q5741069 wd:Q9212979 wd:Q641066 wd:Q216337 } ?item wdt:P31 ?t .", 5, "xl", NB, rank(30000),
     ["The Beatles", "ABBA", "a-ha", "Queen"], ["Michael Jackson", "Norge"], 3000),
    ("sanger", "Nevn en sang (tittel)", "Underholdning", False,
     "VALUES ?t { wd:Q7366 wd:Q134556 wd:Q105543609 } ?item wdt:P31 ?t .", 8, "xl", NB, rank(20000),
     ["Take On Me", "Bohemian Rhapsody", "Yesterday"], ["The Beatles", "Norge"], 3000),
    ("videospill", "Nevn et videospill", "Underholdning", False,
     "?item wdt:P31 wd:Q7889 .", 5, "xl", NB, rank(30000),
     ["Minecraft", "Tetris", "Fortnite", "Super Mario Bros."], ["Nintendo", "Norge"], 5000),
    ("spillfigurer", "Nevn en figur fra et videospill", "Underholdning", False,
     "?item wdt:P31/wdt:P279* wd:Q1569167 .", 3, "l", NB, rank(5000),
     ["Mario", "Pikachu", "Sonic the Hedgehog", "Lara Croft"], ["Minecraft", "Nintendo"], 300),
    # --- Vitenskap og natur ---
    ("grunnstoffer", "Nevn et grunnstoff", "Vitenskap", False,
     "?item wdt:P31 wd:Q11344 ; wdt:P1086 ?z . FILTER(?z >= 1 && ?z <= 118)", 0, "s", NB, PCT,
     ["Oksygen", "Gull", "Jern", "Hydrogen"], ["Vann", "Stål"], 110),
    ("pattedyr", "Nevn et pattedyr", "Natur", False,
     "?item wdt:P105 wd:Q7432 ; wdt:P171+ wd:Q7377 . FILTER(EXISTS { ?item wdt:P1843 ?nb . FILTER(LANG(?nb) = \"nb\") } || EXISTS { ?item rdfs:label ?nl . FILTER(LANG(?nl) = \"nb\") })", 0, "l", NB_ONLY, PCT,
     ["Elg", "Ulv", "Isbjørn", "Blåhval"], ["Laks", "Ørn"], 300),
    ("fugler", "Nevn en fugl", "Natur", False,
     "?item wdt:P105 wd:Q7432 ; wdt:P171+ wd:Q5113 . FILTER(EXISTS { ?item wdt:P1843 ?nb . FILTER(LANG(?nb) = \"nb\") } || EXISTS { ?item rdfs:label ?nl . FILTER(LANG(?nl) = \"nb\") })", 0, "l", NB_ONLY, PCT,
     ["Kjøttmeis", "Gråspurv", "Havørn", "Pingvin"], ["Elg", "Laks"], 400),
    ("nobelprisvinnere", "Nevn en nobelprisvinner", "Vitenskap", False,
     "?item wdt:P166/wdt:P279* wd:Q7191 ; wdt:P31 wd:Q5 .", 0, "s", NB, PCT,
     ["Albert Einstein", "Marie Curie", "Fridtjof Nansen", "Jon Fosse"], ["Isaac Newton", "Lionel Messi"], 700),
    ("fysikere", "Nevn en fysiker", "Vitenskap", False,
     "?item p:P106/ps:P106 wd:Q169470 ; wdt:P31 wd:Q5 .", 10, "l", NB, rank(15000),
     ["Albert Einstein", "Isaac Newton", "Marie Curie", "Niels Bohr"], ["Lionel Messi", "Charles Darwin"], 1000),
    # --- Samfunn og kultur ---
    ("selskaper", "Nevn et selskap", "Samfunn", False,
     "?item wdt:P31/wdt:P279? wd:Q4830453 .", 15, "xl", NB, rank(20000),
     ["Equinor", "Apple", "IKEA", "Telenor"], ["Norge", "Lionel Messi"], 2000),
    ("norske-selskaper", "Nevn et norsk selskap", "Samfunn", True,
     "?item wdt:P31/wdt:P279? wd:Q4830453 ; wdt:P17 wd:Q20 .", 1, "l", NB, rank(4000),
     ["Equinor", "Telenor", "DNB", "Norsk Hydro"], ["Apple", "IKEA"], 400),
    ("selskaper-for-2000", "Nevn et selskap grunnlagt før 2000", "Samfunn", False,
     "?item wdt:P31/wdt:P279? wd:Q4830453 ; wdt:P571 ?d . FILTER(YEAR(?d) < 2000)", 15, "l", NB, rank(10000),
     ["Apple", "IKEA", "Coca-Cola", "Telenor"], ["Facebook", "Spotify"], 1000),
    ("merkevarer", "Nevn et merke (brand)", "Samfunn", False,
     "?item wdt:P31/wdt:P279* wd:Q431289 .", 5, "l", NB, rank(8000),
     ["Coca-Cola", "Nike", "Freia", "Adidas"], ["Norge", "Lionel Messi"], 500),
    ("norske-politikere", "Nevn en norsk politiker", "Samfunn", True,
     "?item p:P106/ps:P106 wd:Q82955 ; wdt:P27 wd:Q20 .", 0, "l", NB, rank(10000),
     ["Jonas Gahr Støre", "Erna Solberg", "Gro Harlem Brundtland", "Jens Stoltenberg"], ["Barack Obama", "Erling Haaland"], 2000),
    ("forfattere", "Nevn en forfatter", "Kultur", False,
     "?item p:P106/ps:P106 wd:Q36180 ; wdt:P31 wd:Q5 .", 25, "xl", NB, rank(30000),
     ["Henrik Ibsen", "William Shakespeare", "Jo Nesbø", "Astrid Lindgren"], ["Lionel Messi", "Norge"], 5000),
    ("norske-forfattere", "Nevn en norsk forfatter", "Kultur", True,
     "?item p:P106/ps:P106 wd:Q36180 ; wdt:P27 wd:Q20 .", 0, "l", NB, rank(6000),
     ["Henrik Ibsen", "Jo Nesbø", "Sigrid Undset", "Knut Hamsun"], ["William Shakespeare", "Erling Haaland"], 1000),
    ("boker", "Nevn en bok, roman eller et skuespill (tittel)", "Kultur", False,
     "VALUES ?t { wd:Q7725634 wd:Q8261 wd:Q25379 wd:Q47461344 wd:Q571 wd:Q116476516 wd:Q1667921 wd:Q179461 } ?item wdt:P31 ?t .", 12, "l", NB, rank(20000),
     ["Sult", "Peer Gynt", "1984", "Harry Potter og de vises stein"], ["Henrik Ibsen", "Norge"], 2000),
    ("historiske-personer", "Nevn en historisk person (død før 1900)", "Kultur", False,
     "?item wdt:P31 wd:Q5 ; wdt:P570 ?d . FILTER(YEAR(?d) < 1900)", 60, "l", NB, rank(15000),
     ["Napoleon", "Julius Caesar", "Harald Hårfagre", "Leonardo da Vinci"], ["Erling Haaland", "Albert Einstein"], 2000),
    ("aviser", "Nevn en norsk avis", "Samfunn", True,
     "?item wdt:P31/wdt:P279* wd:Q11032 ; wdt:P495|wdt:P17 wd:Q20 .", 0, "s", NB, PCT,
     ["Aftenposten", "VG", "Dagbladet", "Bergens Tidende"], ["The Guardian", "NRK"], 100),
    ("nyhetsbyraer", "Nevn et nyhetsbyrå", "Samfunn", False,
     "?item wdt:P31 wd:Q192283 .", 1, "s", NB, PCT,
     ["Reuters", "Associated Press", "NTB"], ["Aftenposten", "Norge"], 50),
    # --- Utvidelse 2 ---
    ("franske-byer", "Nevn en by i Frankrike", "Geografi", False,
     "?item wdt:P31 wd:Q484170 . FILTER EXISTS { ?item wdt:P1082 ?p . FILTER(?p > 5000) }", 10, "s", NB, PCT,
     ["Paris", "Lyon", "Marseille", "Nice"], ["Berlin", "Frankrike"], 300),
    ("italienske-byer", "Nevn en by i Italia (kommune)", "Geografi", False,
     "?item wdt:P31 wd:Q747074 ; wdt:P17 wd:Q38 .", 8, "s", NB, PCT,
     ["Roma", "Milano", "Napoli", "Firenze"], ["Paris", "Italia"], 300),
    ("usa-byer", "Nevn en by i USA", "Geografi", False,
     "VALUES ?t { wd:Q1093829 wd:Q62049 wd:Q1549591 wd:Q13218357 wd:Q13218391 } ?item wdt:P31 ?t ; wdt:P17 wd:Q30 .", 15, "l", NB, rank(4000),
     ["New York", "Los Angeles", "Chicago", "Boston"], ["Toronto", "USA"], 500),
    ("vulkaner", "Nevn en vulkan", "Geografi", False,
     "?item wdt:P31/wdt:P279* wd:Q8072 .", 5, "s", NB, PCT,
     ["Etna", "Vesuv", "Mount Fuji", "Eyjafjallajökull"], ["Mount Everest", "Island"], 150),
    ("verdens-oyer", "Nevn en øy (i hele verden)", "Geografi", False,
     "?item wdt:P31 wd:Q23442 .", 10, "l", NB, rank(4000),
     ["Grønland", "Madagaskar", "Island", "Sicilia"], ["Australia", "Norge"], 500),
    ("verdens-innsjoer", "Nevn en innsjø (i hele verden)", "Geografi", False,
     "?item wdt:P31 wd:Q23397 .", 12, "s", NB, PCT,
     ["Bajkalsjøen", "Mjøsa", "Victoriasjøen", "Vänern"], ["Nilen", "Norge"], 300),
    ("fjell-4000", "Nevn et fjell over 4000 meter", "Geografi", False,
     "?item wdt:P31/wdt:P279* wd:Q8502 ; wdt:P2044 ?h . FILTER(?h >= 4000)", 2, "s", NB, PCT,
     ["Mount Everest", "K2", "Mont Blanc", "Kilimanjaro"], ["Galdhøpiggen", "Norge"], 150),
    ("museer-norge", "Nevn et museum i Norge", "Kultur", True,
     "?item wdt:P31/wdt:P279* wd:Q33506 ; wdt:P17 wd:Q20 .", 1, "s", NB_ONLY + ["mul", "en"], PCT,
     ["Vikingskipshuset", "Norsk Folkemuseum", "Munchmuseet", "Kon-Tiki Museet"], ["Louvre", "Oslo"], 100),
    ("flyplasser-norge", "Nevn en flyplass i Norge", "Geografi", True,
     "?item wdt:P31/wdt:P279* wd:Q1248784 ; wdt:P17 wd:Q20 .", 0, "s", NB_ONLY + ["mul", "en"], PCT,
     ["Oslo lufthavn, Gardermoen", "Bergen lufthavn, Flesland", "Tromsø lufthavn"], ["Heathrow", "Oslo"], 40),
    ("stavkirker", "Nevn en norsk stavkirke", "Kultur", True,
     "?item wdt:P17 wd:Q20 ; wdt:P31/wdt:P279* wd:Q16970 ; rdfs:label ?nbl . FILTER(LANG(?nbl) = \"nb\" && CONTAINS(LCASE(?nbl), \"stavkirke\"))", 0, "s", NB_ONLY + ["mul", "en"], PCT,
     ["Urnes stavkirke", "Borgund stavkirke", "Heddal stavkirke"], ["Nidarosdomen", "Oslo"], 20),
    ("universiteter", "Nevn et universitet", "Samfunn", False,
     "?item wdt:P31/wdt:P279? wd:Q3918 .", 20, "l", NB, rank(4000),
     ["Universitetet i Oslo", "Harvard University", "University of Oxford", "NTNU"], ["Norge", "Oslo"], 500),
    ("sprak", "Nevn et språk", "Kultur", False,
     "?item wdt:P31/wdt:P279* wd:Q34770 .", 30, "s", NB, PCT,
     ["Norsk", "Engelsk", "Spansk", "Samisk"], ["Norge", "Latin-Amerika"], 200),
    ("valutaer", "Nevn en valuta", "Samfunn", False,
     "?item wdt:P31 wd:Q8142 .", 10, "s", NB, PCT,
     ["Euro", "Norsk krone", "Amerikansk dollar", "Japansk yen"], ["Norge", "Bitcoin-fond"], 100),
    ("hunderaser", "Nevn en hunderase", "Natur", False,
     "?item wdt:P31 wd:Q39367 .", 3, "s", NB, PCT,
     ["Labrador retriever", "Golden retriever", "Schäferhund"], ["Katt", "Ulv"], 150),
    ("katteraser", "Nevn en katterase", "Natur", False,
     "?item wdt:P31 wd:Q43577 .", 2, "s", NB, PCT,
     ["Norsk skogkatt", "Maine coon", "Siameser"], ["Golden retriever", "Løve"], 40),
    ("hesteraser", "Nevn en hesterase", "Natur", False,
     "?item wdt:P31 wd:Q1160573 .", 3, "s", NB, PCT,
     ["Fjordhest", "Islandshest", "Araberhest"], ["Labrador retriever", "Esel"], 80),
    ("instrumenter", "Nevn et musikkinstrument", "Kultur", False,
     "?item wdt:P279+ wd:Q34379 .", 15, "s", NB, PCT,
     ["Gitar", "Piano", "Fiolin", "Hardingfele"], ["Sang", "Norge"], 100),
    ("idretter", "Nevn en idrett", "Sport", False,
     "?item wdt:P31 wd:Q31629 .", 8, "s", NB, PCT,
     ["Fotball", "Langrenn", "Håndball", "Tennis"], ["Premier League", "National Basketball Association", "Lionel Messi"], 150),
    ("cocktailer", "Nevn en cocktail", "Kultur", False,
     "?item wdt:P31/wdt:P279* wd:Q134768 .", 2, "s", NB, PCT,
     ["Mojito", "White Russian"], ["Vodka", "Øl"], 25),
    ("oster-verden", "Nevn en ostesort", "Kultur", False,
     "?item wdt:P279+|wdt:P31/wdt:P279* wd:Q10943 .", 4, "s", NB, PCT,
     ["Brie", "Cheddar", "Mozzarella", "Brunost"], ["Melk", "Smør"], 150),
    ("us-presidenter", "Nevn en amerikansk president", "Samfunn", False,
     "?item wdt:P39 wd:Q11696 ; wdt:P31 wd:Q5 .", 0, "s", NB, PCT,
     ["Abraham Lincoln", "Barack Obama", "George Washington", "Donald Trump"], ["Winston Churchill", "Jens Stoltenberg"], 44),
    ("britiske-statsministre", "Nevn en britisk statsminister", "Samfunn", False,
     "?item wdt:P39 wd:Q14211 ; wdt:P31 wd:Q5 .", 0, "s", NB, PCT,
     ["Winston Churchill", "Margaret Thatcher", "Tony Blair", "Boris Johnson"], ["Abraham Lincoln", "Erna Solberg"], 55),
    ("paver", "Nevn en pave", "Kultur", False,
     "?item wdt:P39 wd:Q19546 ; wdt:P31 wd:Q5 .", 0, "s", NB, PCT,
     ["Frans", "Johannes Paul II", "Benedikt XVI"], ["Martin Luther", "Dalai Lama"], 200),
    ("romerske-keisere", "Nevn en romersk keiser", "Kultur", False,
     "?item wdt:P39 wd:Q842606 ; wdt:P31 wd:Q5 .", 0, "s", NB, PCT,
     ["Augustus", "Nero", "Caligula", "Konstantin den store"], ["Julius Caesar", "Napoleon"], 60),
    ("malere", "Nevn en maler", "Kultur", False,
     "?item p:P106/ps:P106 wd:Q1028181 ; wdt:P31 wd:Q5 .", 20, "l", NB, rank(8000),
     ["Edvard Munch", "Pablo Picasso", "Vincent van Gogh", "Leonardo da Vinci"], ["Lionel Messi", "Henrik Ibsen"], 1000),
    ("komponister", "Nevn en komponist", "Kultur", False,
     "?item p:P106/ps:P106 wd:Q36834 ; wdt:P31 wd:Q5 .", 20, "l", NB, rank(8000),
     ["Edvard Grieg", "Wolfgang Amadeus Mozart", "Ludwig van Beethoven", "Johann Sebastian Bach"], ["Lionel Messi", "Henrik Ibsen"], 1000),
    ("filosofer", "Nevn en filosof", "Kultur", False,
     "?item p:P106/ps:P106 wd:Q4964182 ; wdt:P31 wd:Q5 .", 25, "l", NB, rank(5000),
     ["Platon", "Aristoteles", "Immanuel Kant", "Arne Næss"], ["Lionel Messi", "Edvard Munch"], 500),
    ("oppfinnere", "Nevn en oppfinner", "Vitenskap", False,
     "?item p:P106/ps:P106 wd:Q205375 ; wdt:P31 wd:Q5 .", 15, "l", NB, rank(3000),
     ["Thomas Edison", "Nikola Tesla", "Alexander Graham Bell", "Alfred Nobel"], ["Lionel Messi", "Edvard Munch"], 300),
    ("astronauter", "Nevn en astronaut eller kosmonaut", "Vitenskap", False,
     "?item p:P106/ps:P106 wd:Q11631 ; wdt:P31 wd:Q5 .", 0, "s", NB, PCT,
     ["Neil Armstrong", "Jurij Gagarin", "Juri Gagarin", "Buzz Aldrin"], ["Lionel Messi", "Albert Einstein"], 300),
    ("ishockeyspillere", "Nevn en ishockeyspiller", "Sport", False,
     "?item p:P106/ps:P106 wd:Q11774891 ; wdt:P31 wd:Q5 .", 4, "l", NB, rank(10000),
     ["Wayne Gretzky", "Mats Zuccarello", "Sidney Crosby"], ["Lionel Messi", "Petter Northug"], 1000),
    ("handballspillere", "Nevn en håndballspiller", "Sport", False,
     "?item p:P106/ps:P106 wd:Q12840545 ; wdt:P31 wd:Q5 .", 3, "l", NB, rank(6000),
     ["Sander Sagosen", "Nora Mørk", "Mikkel Hansen"], ["Lionel Messi", "Petter Northug"], 800),
    ("alpinister", "Nevn en alpinist", "Sport", False,
     "?item p:P106/ps:P106 wd:Q4144610 ; wdt:P31 wd:Q5 .", 2, "l", NB, rank(4000),
     ["Aksel Lund Svindal", "Kjetil André Aamodt", "Mikaela Shiffrin", "Lindsey Vonn"], ["Bjørn Dæhlie", "Lionel Messi"], 500),
    ("skihoppere", "Nevn en skihopper", "Sport", False,
     "?item p:P106/ps:P106 wd:Q13382603 ; wdt:P31 wd:Q5 . MINUS { ?item p:P106/ps:P106 wd:Q4144610 . }", 2, "l", NB, rank(3000),
     ["Halvor Egner Granerud", "Matti Nykänen", "Anders Jacobsen", "Maren Lundby"], ["Bjørn Dæhlie", "Lionel Messi"], 400),
    ("boksere", "Nevn en bokser", "Sport", False,
     "?item p:P106/ps:P106 wd:Q11338576 ; wdt:P31 wd:Q5 .", 5, "l", NB, rank(5000),
     ["Muhammad Ali", "Mike Tyson", "Cecilia Brækhus"], ["Lionel Messi", "Petter Northug"], 500),
    ("basketballspillere", "Nevn en basketballspiller", "Sport", False,
     "?item p:P106/ps:P106 wd:Q3665646 ; wdt:P31 wd:Q5 .", 5, "l", NB, rank(10000),
     ["Michael Jordan", "LeBron James", "Kobe Bryant"], ["Lionel Messi", "Petter Northug"], 1000),
    ("malerier", "Nevn et kjent maleri", "Kultur", False,
     "?item wdt:P31 wd:Q3305213 .", 15, "s", NB, PCT,
     ["Skrik", "Mona Lisa", "Stjernenatt"], ["Edvard Munch", "Louvre"], 150),
    ("norske-band", "Nevn et norsk band", "Underholdning", True,
     "VALUES ?t { wd:Q215380 wd:Q5741069 } ?item wdt:P31 ?t ; wdt:P495 wd:Q20 .", 0, "s", NB, PCT,
     ["a-ha", "Kaizers Orchestra", "DumDum Boys", "Madcon"], ["ABBA", "Norge"], 200),
    ("oscarfilmer", "Nevn en film som har vunnet Oscar for beste film", "Underholdning", False,
     "?item wdt:P166 wd:Q102427 ; wdt:P31/wdt:P279* wd:Q11424 .", 0, "s", NB, PCT,
     ["Titanic", "Gudfaren", "Forrest Gump", "Parasite"], ["Avatar", "Kon-Tiki"], 85),
    ("bilmerker", "Nevn et bilmerke", "Samfunn", False,
     "?item wdt:P31 wd:Q786820 .", 1, "s", NB, PCT,
     ["Volvo", "Tesla", "Toyota", "Ford"], ["Norge", "Lionel Messi"], 200),
    # ===== Nye kategorier (18. nov.) =====
    # --- Norge ---
    ("norske-fjorder", "Nevn en norsk fjord", "Geografi", True,
     "?item wdt:P31 wd:Q45776 ; wdt:P17 wd:Q20 .", 0, "l", NB_ONLY + ["mul", "en"], PCT,
     ["Sognefjorden", "Hardangerfjorden", "Geirangerfjorden"], ["Mjøsa", "Oslo"], 300),
    ("norske-isbreer", "Nevn en norsk isbre", "Geografi", True,
     "?item wdt:P31 wd:Q35666 ; wdt:P17 wd:Q20 .", 0, "s", NB_ONLY + ["mul", "en"], PCT,
     ["Jostedalsbreen", "Folgefonna", "Svartisen"], ["Galdhøpiggen", "Oslo"], 60),
    ("norske-fosser", "Nevn en norsk foss", "Geografi", True,
     "?item wdt:P31 wd:Q34038 ; wdt:P17 wd:Q20 .", 0, "s", NB_ONLY + ["mul", "en"], PCT,
     ["Vøringsfossen", "Låtefossen", "Steinsdalsfossen"], ["Glomma", "Oslo"], 60),
    ("norske-nasjonalparker", "Nevn en norsk nasjonalpark", "Geografi", True,
     "?item wdt:P31 wd:Q46169 ; wdt:P17 wd:Q20 .", 0, "s", NB_ONLY + ["mul", "en"], PCT,
     ["Jotunheimen nasjonalpark", "Hardangervidda nasjonalpark", "Rondane nasjonalpark"], ["Galdhøpiggen", "Oslo"], 30),
    ("norske-jernbanestasjoner", "Nevn en norsk jernbanestasjon", "Geografi", True,
     "?item wdt:P31 wd:Q55488 ; wdt:P17 wd:Q20 .", 0, "l", NB_ONLY + ["mul", "en"], PCT,
     ["Oslo S", "Bergen stasjon", "Myrdal stasjon"], ["Gardermoen", "Bergen"], 200),
    ("norske-kirker", "Nevn en norsk kirke", "Kultur", True,
     "VALUES ?t { wd:Q16970 wd:Q2977 } ?item wdt:P31 ?t ; wdt:P17 wd:Q20 .", 0, "l", NB_ONLY + ["mul", "en"], PCT,
     ["Nidarosdomen", "Ishavskatedralen"], ["Notre-Dame de Paris", "Oslo"], 300),
    ("norske-malere", "Nevn en norsk maler", "Kultur", True,
     "?item p:P106/ps:P106 wd:Q1028181 ; wdt:P31 wd:Q5 ; wdt:P27 wd:Q20 .", 0, "l", NB, PCT,
     ["Edvard Munch", "Nikolai Astrup", "Harald Sohlberg", "Theodor Kittelsen"], ["Pablo Picasso", "Henrik Ibsen"], 200),
    ("norske-komponister", "Nevn en norsk komponist", "Kultur", True,
     "?item p:P106/ps:P106 wd:Q36834 ; wdt:P31 wd:Q5 ; wdt:P27 wd:Q20 .", 0, "l", NB, PCT,
     ["Edvard Grieg", "Johan Svendsen", "Christian Sinding"], ["Wolfgang Amadeus Mozart", "Edvard Munch"], 150),
    ("norske-programledere", "Nevn en norsk TV-programleder", "Underholdning", True,
     "?item p:P106/ps:P106 wd:Q947873 ; wdt:P31 wd:Q5 ; wdt:P27 wd:Q20 .", 0, "s", NB, PCT,
     ["Fredrik Skavlan", "Anne Lindmo"], ["Oprah Winfrey", "Erna Solberg"], 100),
    ("norske-journalister", "Nevn en norsk journalist", "Samfunn", True,
     "?item p:P106/ps:P106 wd:Q1930187 ; wdt:P31 wd:Q5 ; wdt:P27 wd:Q20 .", 0, "l", NB, PCT,
     ["Fredrik Skavlan", "Åsne Seierstad", "Anne Lindmo"], ["Bob Woodward", "Edvard Munch"], 300),
    ("norske-handballspillere", "Nevn en norsk håndballspiller", "Sport", True,
     "?item p:P106/ps:P106 wd:Q12840545 ; wdt:P31 wd:Q5 ; wdt:P27 wd:Q20 .", 0, "l", NB, PCT,
     ["Sander Sagosen", "Nora Mørk", "Stine Bredal Oftedal"], ["Mikkel Hansen", "Petter Northug"], 200),
    ("norske-rappere", "Nevn en norsk rapper", "Underholdning", True,
     "?item p:P106/ps:P106 wd:Q2252262 ; wdt:P31 wd:Q5 ; wdt:P27 wd:Q20 .", 0, "s", NB, PCT,
     ["Lars Vaular", "Cezinando"], ["Eminem", "Edvard Grieg"], 30),
    # --- Verden ---
    ("delstater-usa", "Nevn en amerikansk delstat", "Geografi", False,
     "?item wdt:P31 wd:Q35657 .", 0, "s", NB, PCT,
     ["Texas", "California", "Alaska", "Florida"], ["New York City", "Canada"], 50),
    ("britiske-byer", "Nevn en by i Storbritannia", "Geografi", False,
     "VALUES ?t { wd:Q515 wd:Q1637706 wd:Q1549591 wd:Q3957 } ?item wdt:P31 ?t ; wdt:P17 wd:Q145 .", 5, "l", NB, rank(1500),
     ["London", "Liverpool", "Edinburgh"], ["Dublin", "England"], 300),
    ("spanske-byer", "Nevn en by i Spania", "Geografi", False,
     "VALUES ?t { wd:Q515 wd:Q2074737 } ?item wdt:P31 ?t ; wdt:P17 wd:Q29 .", 3, "l", NB, rank(3000),
     ["Madrid", "Barcelona", "Sevilla", "Valencia"], ["Lisboa", "Spania"], 300),
    ("japanske-byer", "Nevn en by i Japan", "Geografi", False,
     "?item wdt:P31/wdt:P279* wd:Q515 ; wdt:P17 wd:Q17 .", 3, "l", NB, PCT,
     ["Tokyo", "Osaka", "Kyoto", "Hiroshima"], ["Seoul", "Japan"], 150),
    ("hav", "Nevn et hav", "Geografi", False,
     "{ ?item wdt:P31/wdt:P279* wd:Q165 . } UNION { ?item wdt:P31 wd:Q9430 . }", 5, "s", NB, PCT,
     ["Nordsjøen", "Middelhavet", "Stillehavet", "Barentshavet"], ["Mjøsa", "Nilen"], 60),
    ("orkener", "Nevn en ørken", "Geografi", False,
     "?item wdt:P31 wd:Q8514 .", 5, "s", NB, PCT,
     ["Sahara", "Gobi", "Atacama", "Kalahari"], ["Amazonas", "Mount Everest"], 50),
    ("verdensarv", "Nevn et sted på UNESCOs verdensarvliste", "Geografi", False,
     "?item wdt:P1435 wd:Q9259 .", 3, "l", NB, rank(1200),
     ["Bryggen", "Taj Mahal"], ["Oslo", "Norge"], 500),
    ("skyskrapere", "Nevn en skyskraper", "Kultur", False,
     "?item wdt:P31 wd:Q11303 .", 8, "s", NB, PCT,
     ["Burj Khalifa", "Empire State Building", "Taipei 101"], ["Eiffeltårnet", "New York"], 100),
    ("slott", "Nevn et slott eller en borg", "Kultur", False,
     "VALUES ?t { wd:Q23413 wd:Q751876 } ?item wdt:P31 ?t .", 10, "l", NB, PCT,
     ["Neuschwanstein", "Windsor Castle", "Akershus festning"], ["Louvre", "Oslo"], 150),
    ("kunstmuseer", "Nevn et kunstmuseum", "Kultur", False,
     "?item wdt:P31 wd:Q207694 .", 15, "s", NB, PCT,
     ["Louvre", "Nasjonalmuseet", "Museum of Modern Art", "Prado"], ["Mona Lisa", "Paris"], 100),
    ("flyselskaper", "Nevn et flyselskap", "Samfunn", False,
     "?item wdt:P31 wd:Q46970 .", 5, "l", NB, rank(2000),
     ["SAS", "Norwegian", "Lufthansa", "Widerøe"], ["Boeing", "Gardermoen"], 200),
    ("tv-kanaler", "Nevn en TV-kanal", "Underholdning", False,
     "?item wdt:P31/wdt:P279* wd:Q2001305 .", 6, "l", NB, rank(3000),
     ["CNN", "TV 2"], ["Netflix", "VG"], 300),
    ("musikkfestivaler", "Nevn en musikkfestival", "Underholdning", False,
     "?item wdt:P31 wd:Q868557 .", 3, "l", NB, PCT,
     ["Roskilde-festivalen", "Øyafestivalen", "Glastonbury Festival", "Coachella"], ["Eurovision Song Contest", "Oslo"], 200),
    ("religioner", "Nevn en religion", "Kultur", False,
     "?item wdt:P31/wdt:P279* wd:Q9174 .", 8, "s", NB, PCT,
     ["Kristendom", "Islam", "Buddhisme", "Hinduisme"], ["Paven", "Jerusalem"], 40),
    ("kriger", "Nevn en krig", "Historie", False,
     "?item wdt:P31/wdt:P279* wd:Q198 .", 25, "l", NB, PCT,
     ["Andre verdenskrig", "Vietnamkrigen", "Hundreårskrigen"], ["Adolf Hitler", "Napoleon"], 300),
    ("slag", "Nevn et kjent slag", "Historie", False,
     "?item wdt:P31 wd:Q178561 .", 20, "l", NB, PCT,
     ["Slaget ved Waterloo", "Slaget ved Stiklestad", "Slaget om Stalingrad"], ["Napoleon", "Andre verdenskrig"], 200),
    ("operaer", "Nevn en opera", "Kultur", False,
     "?item wdt:P136/wdt:P279* wd:Q1344 . FILTER NOT EXISTS { ?item wdt:P31 wd:Q5 . } FILTER NOT EXISTS { ?item wdt:P31 wd:Q215380 . }", 8, "l", NB, rank(3000),
     ["Carmen", "Aida"], ["Giuseppe Verdi", "Operaen i Oslo"], 200),
    ("animasjonsfilmer", "Nevn en animasjonsfilm", "Underholdning", False,
     "VALUES ?t { wd:Q202866 wd:Q29168811 wd:Q20650540 } ?item wdt:P31 ?t .", 12, "l", NB, PCT,
     ["Løvenes konge"], ["Mikke Mus", "Pixar"], 300),
    ("brettspill", "Nevn et brettspill", "Underholdning", False,
     "?item wdt:P31 wd:Q131436 .", 6, "l", NB, PCT,
     ["Monopol", "Sjakk", "Ludo", "Catan"], ["Kortstokk", "Tetris"], 150),
    ("musikksjangere", "Nevn en musikksjanger", "Underholdning", False,
     "?item wdt:P31 wd:Q188451 .", 20, "l", NB, PCT,
     ["Rock", "Jazz", "Hiphop", "Black metal"], ["Gitar", "Elvis Presley"], 200),
    ("superhelter", "Nevn en superhelt", "Underholdning", False,
     "?item p:P106/ps:P106 wd:Q188784 .", 8, "s", NB, PCT,
     ["Batman", "Superman"], ["Joker", "Marvel Comics"], 60),
    ("spillkonsoller", "Nevn en spillkonsoll", "Underholdning", False,
     "?item wdt:P279+ wd:Q8076 .", 8, "s", NB, PCT,
     ["Nintendo Switch", "Game Boy"], ["Super Mario", "Sony"], 60),
    ("programmeringssprak", "Nevn et programmeringsspråk", "Vitenskap", False,
     "?item wdt:P31/wdt:P279* wd:Q9143 .", 10, "l", NB, PCT,
     ["Python", "Java", "C++", "JavaScript"], ["Linux", "Engelsk"], 150),
    ("sykdommer", "Nevn en sykdom", "Vitenskap", False,
     "?item wdt:P279+ wd:Q12136 ; wdt:P31 wd:Q112193867 .", 20, "l", NB, PCT,
     ["Influensa", "Malaria"], ["Paracetamol", "Hjerte"], 300),
    ("stjernebilder", "Nevn et stjernebilde", "Vitenskap", False,
     "?item wdt:P31 wd:Q8928 .", 0, "s", NB, PCT,
     ["Orion", "Store bjørn", "Kassiopeia", "Skorpionen"], ["Sirius", "Månen"], 80),
    ("maaner", "Nevn en måne i solsystemet", "Vitenskap", False,
     "VALUES ?p { wd:Q111 wd:Q319 wd:Q193 wd:Q324 wd:Q332 wd:Q339 wd:Q2 } ?item wdt:P397 ?p ; wdt:P31/wdt:P279* wd:Q2537 .", 0, "s", NB, PCT,
     ["Titan", "Europa"], ["Mars", "Sola"], 50),
    ("retter", "Nevn en matrett", "Mat", False,
     "?item wdt:P279* wd:Q746549 .", 15, "l", NB, rank(1700),
     ["Pizza", "Sushi"], ["Italia", "Lionel Messi"], 500),
    ("pastatyper", "Nevn en pastatype", "Mat", False,
     "?item wdt:P279+ wd:Q178 .", 3, "s", NB, PCT,
     ["Spaghetti", "Penne"], ["Pizza", "Ris"], 40),
    # --- Personer ---
    ("regissorer", "Nevn en filmregissør", "Underholdning", False,
     "?item p:P106/ps:P106 wd:Q2526255 ; wdt:P31 wd:Q5 .", 15, "l", NB, rank(8000),
     ["Steven Spielberg", "Quentin Tarantino", "Christopher Nolan"], ["Lionel Messi", "Edvard Munch"], 800),
    ("rappere", "Nevn en rapper", "Underholdning", False,
     "?item p:P106/ps:P106 wd:Q2252262 ; wdt:P31 wd:Q5 .", 8, "l", NB, rank(5000),
     ["Eminem", "Jay-Z", "Kanye West", "Tupac Shakur"], ["Michael Jackson", "Edvard Grieg"], 500),
    ("komikere", "Nevn en komiker", "Underholdning", False,
     "?item p:P106/ps:P106 wd:Q245068 ; wdt:P31 wd:Q5 .", 10, "l", NB, rank(5000),
     ["Rowan Atkinson", "Charlie Chaplin", "Robin Williams", "Harald Eia"], ["Edvard Munch", "Lionel Messi"], 500),
    ("arkitekter", "Nevn en arkitekt", "Kultur", False,
     "?item p:P106/ps:P106 wd:Q42973 ; wdt:P31 wd:Q5 .", 15, "l", NB, rank(5000),
     ["Le Corbusier", "Frank Lloyd Wright", "Zaha Hadid", "Antoni Gaudí"], ["Pablo Picasso", "Lionel Messi"], 500),
    ("matematikere", "Nevn en matematiker", "Vitenskap", False,
     "?item p:P106/ps:P106 wd:Q170790 ; wdt:P31 wd:Q5 .", 20, "l", NB, rank(6000),
     ["Pythagoras", "Isaac Newton", "Niels Henrik Abel", "Leonhard Euler"], ["Lionel Messi", "Edvard Munch"], 600),
    ("kjemikere", "Nevn en kjemiker", "Vitenskap", False,
     "?item p:P106/ps:P106 wd:Q593644 ; wdt:P31 wd:Q5 .", 20, "l", NB, rank(5000),
     ["Marie Curie", "Dmitrij Mendelejev", "Alfred Nobel", "Linus Pauling"], ["Lionel Messi", "Edvard Munch"], 400),
    ("oppdagelsesreisende", "Nevn en oppdagelsesreisende", "Historie", False,
     "?item p:P106/ps:P106 wd:Q11900058 ; wdt:P31 wd:Q5 .", 8, "l", NB, rank(3000),
     ["Roald Amundsen", "Thor Heyerdahl"], ["Lionel Messi", "Edvard Munch"], 300),
    ("syklister", "Nevn en syklist", "Sport", False,
     "?item p:P106/ps:P106 wd:Q2309784 ; wdt:P31 wd:Q5 .", 4, "l", NB, rank(10000),
     ["Thor Hushovd", "Eddy Merckx", "Lance Armstrong", "Tadej Pogačar"], ["Lionel Messi", "Petter Northug"], 1000),
    ("golfspillere", "Nevn en golfspiller", "Sport", False,
     "VALUES ?o { wd:Q11303721 wd:Q490253 } ?item p:P106/ps:P106 ?o ; wdt:P31 wd:Q5 .", 4, "l", NB, rank(4000),
     ["Tiger Woods", "Viktor Hovland", "Suzann Pettersen", "Rory McIlroy"], ["Lionel Messi", "Petter Northug"], 400),
    ("svommere", "Nevn en svømmer", "Sport", False,
     "?item p:P106/ps:P106 wd:Q10843402 ; wdt:P31 wd:Q5 .", 6, "l", NB, rank(8000),
     ["Michael Phelps", "Alexander Dale Oen", "Ian Thorpe"], ["Lionel Messi", "Petter Northug"], 800),
    ("friidrettsutovere", "Nevn en friidrettsutøver", "Sport", False,
     "?item p:P106/ps:P106 wd:Q11513337 ; wdt:P31 wd:Q5 .", 8, "xl", NB, rank(20000),
     ["Usain Bolt", "Karsten Warholm", "Jakob Ingebrigtsen", "Grete Waitz"], ["Lionel Messi", "Petter Northug"], 2000),
    ("skoyteloper", "Nevn en skøyteløper", "Sport", False,
     "?item p:P106/ps:P106 wd:Q10866633 ; wdt:P31 wd:Q5 .", 3, "l", NB, rank(3000),
     ["Johann Olav Koss", "Sverre Lunde Pedersen", "Hjalmar Andersen", "Sven Kramer"], ["Lionel Messi", "Petter Northug"], 300),
    ("youtubere", "Nevn en YouTuber", "Underholdning", False,
     "?item p:P106/ps:P106 wd:Q17125263 ; wdt:P31 wd:Q5 .", 5, "l", NB, rank(3000),
     ["PewDiePie", "MrBeast", "Markiplier"], ["Lionel Messi", "Edvard Munch"], 200),
    # ===== Puffer Party-inspirerte kategorier (issue #1) =====
    ("sosiale-medier", "Nevn et sosialt medium", "Samfunn", False,
     "?item wdt:P31/wdt:P279* wd:Q3220391 .", 5, "s", NB, PCT,
     ["Facebook", "TikTok"], ["Apple", "Microsoft"], 100),
    ("nettlesere", "Nevn en nettleser", "Vitenskap", False,
     "{ ?item wdt:P31/wdt:P279* wd:Q6368 . } UNION { VALUES ?item { wd:Q777 } }", 5, "s", NB, PCT,
     ["Google Chrome", "Safari"], ["Google", "Windows"], 60),
    ("kortspill", "Nevn et kortspill", "Underholdning", False,
     "?item wdt:P31/wdt:P279* wd:Q142714 .", 3, "l", NB, PCT,
     ["Blackjack"], ["Sjakk", "Monopol"], 200),
    ("fobier", "Nevn en fobi", "Vitenskap", False,
     "?item wdt:P279+ wd:Q175854 .", 3, "s", NB, PCT,
     [], ["Angst", "Edderkopp"], 50),
    ("sjakkapninger", "Nevn en sjakkåpning", "Sport", False,
     "?item wdt:P31 wd:Q103632 .", 1, "s", NB, PCT,
     [], ["Magnus Carlsen", "Sjakk"], 150),
    ("eddik", "Nevn en type eddik", "Mat", False,
     "?item wdt:P279+ wd:Q41354 .", 0, "s", NB, PCT,
     [], ["Olivenolje", "Salt"], 25),
    ("bilmodeller", "Nevn en bilmodell", "Samfunn", False,
     "?item wdt:P31/wdt:P279* wd:Q3231690 .", 10, "l", NB, rank(3000),
     ["Tesla Model 3"], ["Tesla", "Volvo"], 1000),
    ("pixar-figurer", "Nevn en Pixar-figur", "Underholdning", False,
     "?item wdt:P1441 ?w ; wdt:P31/wdt:P279* wd:Q95074 . ?w wdt:P272 wd:Q127552 .", 3, "s", NB, PCT,
     ["Woody", "Buzz Lightyear"], ["Mikke Mus", "Pixar"], 30),
    ("disney-figurer", "Nevn en Disney-figur", "Underholdning", False,
     "?item wdt:P31/wdt:P279* wd:Q95074 ; wdt:P1441 ?w . ?w wdt:P272 wd:Q191224 .", 5, "s", NB, PCT,
     ["Mikke Mus", "Donald Duck"], ["Walt Disney", "Pixar"], 100),
    ("harry-potter-figurer", "Nevn en figur fra Harry Potter", "Underholdning", False,
     "?item wdt:P1080 wd:Q5410773 ; wdt:P31/wdt:P279* wd:Q95074 .", 3, "l", NB, PCT,
     ["Harry Potter"], ["J.K. Rowling", "Galtvort"], 200),
    ("simpsons-figurer", "Nevn en figur fra The Simpsons", "Underholdning", False,
     "?item wdt:P1441 wd:Q886 ; wdt:P31/wdt:P279* wd:Q95074 .", 1, "s", NB, PCT,
     ["Homer Simpson"], ["Matt Groening", "Springfield"], 100),
    ("cl-vinnere", "Nevn en klubb som har vunnet Champions League eller Europacupen", "Sport", False,
     "?s wdt:P3450 wd:Q18756 ; wdt:P1346 ?item .", 0, "s", NB, PCT,
     ["Liverpool"], ["Rosenborg", "Brann"], 20),
    # --- Nye kategorier (november 2026) ---
    ("norske-komikere", "Nevn en norsk komiker", "Underholdning", True,
     "VALUES ?occ { wd:Q245068 wd:Q18545066 } ?item p:P106/ps:P106 ?occ ; wdt:P27 wd:Q20 ; wdt:P31 wd:Q5 .", 0, "s", NB, PCT,
     ["Atle Antonsen", "Harald Eia", "Herman Flesvig"], ["Taylor Swift", "Erling Haaland"], 150),
    ("land-europa", "Nevn et land i Europa", "Geografi", False,
     "?item wdt:P31 wd:Q3624078 ; wdt:P30 wd:Q46 . FILTER NOT EXISTS { ?item wdt:P576 ?slutt . }", 0, "s", NB, PCT,
     ["Norge", "Sverige", "Frankrike", "Moldova"], ["Japan", "Brasil"], 40),
    ("land-afrika", "Nevn et land i Afrika", "Geografi", False,
     "?item wdt:P31 wd:Q3624078 ; wdt:P30 wd:Q15 . FILTER NOT EXISTS { ?item wdt:P576 ?slutt . }", 0, "s", NB, PCT,
     ["Egypt", "Nigeria", "Kenya", "Sør-Afrika"], ["Norge", "India"], 45),
    ("land-asia", "Nevn et land i Asia", "Geografi", False,
     "?item wdt:P31 wd:Q3624078 ; wdt:P30 wd:Q48 . FILTER NOT EXISTS { ?item wdt:P576 ?slutt . }", 0, "s", NB, PCT,
     ["Japan", "Kina", "India", "Thailand"], ["Norge", "Brasil"], 40),
    ("land-sor-amerika", "Nevn et land i Sør-Amerika", "Geografi", False,
     "?item wdt:P31 wd:Q3624078 ; wdt:P30 wd:Q18 . FILTER NOT EXISTS { ?item wdt:P576 ?slutt . }", 0, "s", NB, PCT,
     ["Brasil", "Argentina", "Chile", "Peru"], ["Mexico", "Spania"], 10),
    ("norske-partier", "Nevn et norsk politisk parti", "Samfunn", True,
     "?item wdt:P31/wdt:P279* wd:Q7278 ; wdt:P17 wd:Q20 . FILTER NOT EXISTS { ?item wdt:P576 ?slutt . }", 0, "s", NB, PCT,
     ["Arbeiderpartiet", "Høyre", "Fremskrittspartiet", "Senterpartiet"], ["Demokratene i USA", "Erna Solberg"], 20),
    ("ballondor", "Nevn en vinner av Ballon d'Or", "Sport", False,
     "?item wdt:P166 wd:Q166177 ; wdt:P31 wd:Q5 .", 0, "s", NB, PCT,
     ["Lionel Messi"], ["Ole Gunnar Solskjær", "Petter Northug"], 40),
]


# Kjente personer der kategorien ikke er det de er kjent for: gyldige svar, men legges på øverste nivå (sjeldne).
# Regel: personen har også et av yrkene i «occupations», men ingen av kjennetegnene i «keep_props»/«keep_occupations»
# på at de faktisk er kjent for kategorien. Eksempel: Charlie Chaplin står som sanger, men er kjent som filmskaper.
# Kjennetegn: «P264» = har egenskapen, «P54:3» = minst 3 verdier, «^P86:15» = minst 15 verk peker hit, «P101=Q395» = fagfelt.
ACT = ["Q33999", "Q10800557", "Q2405480", "Q2259451", "Q4610556", "Q488111"]
POL = ["Q82955", "Q116", "Q2478141", "Q193391", "Q30461", "Q372436", "Q189290", "Q47064", "Q40348", "Q16533", "Q15253558", "Q15995642", "Q1234713"]
WRI = ["Q36180", "Q49757", "Q6625963", "Q214917", "Q482980", "Q18814623", "Q1930187", "Q28389", "Q4853732"]
LIT = ["Q49757", "Q6625963", "Q214917", "Q4853732"]          # skjønnlitterære forfattere
SCI = ["Q901", "Q169470", "Q170790", "Q593644", "Q11063", "Q18805", "Q4964182", "Q201788", "Q81096", "Q205375"]
ART = ["Q1028181", "Q1281618", "Q42973", "Q1114448", "Q2526255", "Q3282637"]
MUS = ["Q177220", "Q639669", "Q36834", "Q855091", "Q1259917", "Q2252262"]
BIZ = ["Q43845", "Q131524", "Q12362622"]
EXP = ["Q11900058", "Q9149093", "Q11631", "Q12634815"]
TV = ["Q947873", "Q2722764", "Q245068", "Q17125263"]
SPORT = ["Q2066131", "Q937857", "Q3665646", "Q11774891", "Q10833314", "Q11338576", "Q10843402", "Q4144610", "Q13382608",
         "Q13382603", "Q10866633", "Q13219587", "Q2309784", "Q378622", "Q11513337", "Q10873124", "Q13474373", "Q12840545",
         "Q12299841", "Q19204627", "Q10871364", "Q14089670", "Q13381376"]


def _no(lst, *own):
    return [x for x in lst if x not in own]


def dem(occ, keep=(), keep_occ=(), minsl=20, **kw):
    d = {"occupations": list(dict.fromkeys(occ)), "min_sitelinks": minsl, "keep_props": list(keep), "tier": 5}
    if keep_occ:
        d["keep_occupations"] = list(keep_occ)
    d.update(kw)
    return d


OTHER_THAN_SPORT = ACT + POL + WRI + SCI + ART + MUS + BIZ + EXP + TV
DEMOTE = {
    "artister": dem(ACT + POL + WRI + SCI + ART + BIZ + EXP + ["Q36834", "Q2066131", "Q937857"], keep=["P264", "P463", "P358"],
                    minsl=30, base="?item p:P106/ps:P106 wd:Q177220 ."),
    "rappere": dem(ACT + POL + SPORT + BIZ, keep=["P264", "P463", "P358"]),
    "komponister": dem(["Q177220", "Q2252262"] + _no(WRI, "Q49757", "Q1930187") + ACT + POL + SCI + ["Q1028181", "Q2526255"] + BIZ + SPORT, keep=["^P86:15"]),
    "forfattere": dem(POL + SCI + ART + MUS + ACT + BIZ + EXP + SPORT, keep_occ=LIT),
    "norske-forfattere": dem(POL + SCI + ART + MUS + ACT + EXP + SPORT, keep_occ=LIT, minsl=8),
    "norske-journalister": dem(LIT + POL + ART + MUS + ACT + EXP + SPORT, minsl=8),
    "norske-politikere": dem(LIT + EXP + ["Q169470", "Q901", "Q1028181"] + SPORT, keep=["P39:3"], minsl=8),
    "filosofer": dem(["Q169470", "Q170790", "Q11063", "Q18805", "Q205375", "Q593644"] + POL + LIT + ART + MUS + ACT,
                     keep=["P101=Q5891"]),
    "fysikere": dem(_no(SCI, "Q169470", "Q901", "Q1622272", "Q1650915") + POL + LIT + ART + MUS + BIZ + ["Q36180"], keep=["P101=Q413"]),
    "kjemikere": dem(_no(SCI, "Q593644", "Q901", "Q1622272", "Q1650915") + POL + LIT + ART + MUS + BIZ, keep=["P101=Q2329"]),
    "matematikere": dem(_no(SCI, "Q170790", "Q901", "Q1622272", "Q1650915") + POL + LIT + ART + MUS + BIZ, keep=["P101=Q395"]),
    "malere": dem(POL + WRI + _no(SCI, "Q42973") + MUS + ACT + BIZ + EXP + ["Q2526255", "Q3282637"], keep=["^P170:12"]),
    "arkitekter": dem(POL + WRI + SCI + MUS + ACT + ["Q1028181", "Q1281618"], keep=["^P84:3"]),
    "regissorer": dem(WRI + MUS + _no(ART, "Q2526255", "Q3282637") + SCI + POL + EXP + SPORT + BIZ, keep=["^P57:3"]),
    "skuespillere": dem(POL + WRI + _no(ART, "Q2526255", "Q3282637") + SCI + MUS + EXP + SPORT + BIZ, keep=["^P161:5"]),
    "norske-skuespillere": dem(MUS + WRI + POL + SPORT + EXP + ART, keep=["^P161:4"], minsl=8),
    "oppfinnere": dem(EXP + POL + ACT + ["Q3282637", "Q2526255", "Q1028181"] + LIT, keep=["^P61:1"]),
    "oppdagelsesreisende": dem(POL + ["Q18805", "Q11631", "Q12634815", "Q169470"] + WRI + ART),
    "youtubere": dem(ACT + POL + ["Q855091", "Q947873", "Q2526255", "Q1259917"] + SCI + WRI),
    "norske-programledere": dem(SPORT, minsl=8),
    "basketballspillere": dem(OTHER_THAN_SPORT + _no(SPORT, "Q3665646", "Q2066131"), keep=["P54:3"]),
    "ishockeyspillere": dem(OTHER_THAN_SPORT + _no(SPORT, "Q11774891", "Q2066131"), keep=["P54:3", "P2481"]),
    "handballspillere": dem(OTHER_THAN_SPORT + _no(SPORT, "Q12840545", "Q2066131"), keep=["P54:3"]),
    "norske-handballspillere": dem(OTHER_THAN_SPORT + _no(SPORT, "Q12840545", "Q2066131"), keep=["P54:3"], minsl=8),
    "norske-fotballspillere": dem(OTHER_THAN_SPORT + _no(SPORT, "Q937857", "Q2066131"), keep=["P54:3"], minsl=8),
    "tennisspillere": dem(OTHER_THAN_SPORT + _no(SPORT, "Q10833314", "Q2066131"), keep=["P536", "P597"]),
    "golfspillere": dem(OTHER_THAN_SPORT + _no(SPORT, "Q2066131"), keep=["P2811", "P8286"]),
    "alpinister": dem(OTHER_THAN_SPORT + _no(SPORT, "Q4144610", "Q2066131", "Q13382608"), keep=["P2772"]),
    "friidrettsutovere": dem(OTHER_THAN_SPORT + _no(SPORT, "Q11513337", "Q2066131", "Q13382460"), keep=["P1146", "P8286"]),
    "svommere": dem(OTHER_THAN_SPORT + _no(SPORT, "Q10843402", "Q2066131"), keep=["P8286"]),
    "skoyteloper": dem(OTHER_THAN_SPORT + _no(SPORT, "Q10866633", "Q13219587", "Q2066131"), keep=["P8286", "P2350"]),
    "skihoppere": dem(OTHER_THAN_SPORT + _no(SPORT, "Q13382603", "Q13382608", "Q2066131"), keep=["P8286"]),
    "boksere": dem(OTHER_THAN_SPORT + _no(SPORT, "Q11338576", "Q2066131", "Q13474373"), keep=["P1967"]),
    # Figurer som også finnes i film/tegneserier (Mikke Mus, Darth Vader): gyldige, men ikke typiske spillfigurer
    "spillfigurer": dem(["Q15773347", "Q15711870", "Q1114461", "Q15773317", "Q3658341", "Q15632617"],
                        keep=["P31=Q1569167"], minsl=10, prop="P31"),
}


NORSKE_UTOVERE = ("VALUES ?occ { wd:Q177220 wd:Q2252262 wd:Q488205 wd:Q130857 wd:Q639669 wd:Q753110 wd:Q855091 wd:Q245068 wd:Q18545066 } "
                  "?item p:P106/ps:P106 ?occ ; wdt:P27 wd:Q20 ; wdt:P31 wd:Q5 .")
EXTRA = {
    # Alle norske musikere og komikere, også de med få Wikipedia-utgaver (Herman Flesvig, Martin Lepperød)
    "artister": [{"where": NORSKE_UTOVERE, "min_sitelinks": 0, "bands": [[0, 100000]]}],
}
PV_EXTRA = {"artister", "band", "filmer", "filmer-1990", "tv-serier", "videospill", "fotballklubber", "fotballspillere",
            "skuespillere", "forfattere", "komikere", "rappere", "youtubere", "merkevarer", "bilmerker", "idretter", "retter",
            "boker", "superhelter", "disney-figurer", "spillfigurer", "animasjonsfilmer", "tv-kanaler", "musikksjangere",
            "hunderaser", "fugler", "instrumenter", "kunstmuseer", "musikkfestivaler", "flyselskaper", "aviser",
            "kriger", "hovedsteder", "land", "land-europa", "land-asia", "land-afrika", "sanger", "komponister", "malere"}
CITY_POP = {"tyske-byer", "franske-byer", "italienske-byer", "usa-byer", "britiske-byer", "spanske-byer", "japanske-byer", "storbyer"}


def make():
    os.makedirs(OUT, exist_ok=True)
    made = 0
    for row in KATALOG:
        qid = row[0]
        if row[1] is None:
            continue
        _, q, cat, norsk, where, minsl, size, langs, cuts, inn, ut, minc = row
        minsl = MINSL.get(qid, minsl)
        where_full = where   # minstekravet til sitelinks håndteres av båndene (min_sitelinks)
        cfg = {
            "question": q, "category": cat, "norsk": norsk, "status": "godkjent",
            "modes": ["daily", "endless", "packs", "party"], "attribution": WD,
            "source": {"type": "wikidata", "where": where_full, "bands": bands(size), "min_sitelinks": minsl,
                       "label_langs": langs, "alias_langs": ["nb", "nn", "mul", "en"]},
            "rarity": {"weights": {"sitelinks": 1.0}, "cuts": cuts},
            "validate": {"min_count": minc, "max_shrink": 0.10, "must_include": inn, "must_exclude": ut},
        }
        if qid in ("bilmerker", "selskaper", "norske-selskaper", "selskaper-for-2000", "merkevarer"):
            cfg["strip_suffixes"] = ["Inc", "Inc.", "Corporation", "Corp", "Motor Company", "Motor Corporation", "Motors",
                                     "Company", "Group", "AG", "AB", "ASA", "AS", "SE", "S.p.A.", "SpA", "GmbH", "Ltd", "plc",
                                     "Holding", "Holdings", "Automobiles", "Automobile", "Cars", "Auto"]
        if qid == "nettlesere":
            cfg["strip_prefixes"] = ["Nettlesaren", "Nettleseren"]
        if qid in ("norske-fotballklubber", "fotballklubber", "cl-vinnere"):
            cfg["strip_suffixes"] = ["FK", "Fotballklubb", "Fotball", "IL", "BK", "SK", "IF", "FC", "F.C.", "AFC", "CF",
                                     "Toppfotball", "Elite", "Fotballforening"]
            cfg["strip_prefixes"] = ["SK", "IL", "FK", "IK", "BK", "FC", "AFC", "AC", "AS", "SS", "SSC", "SV", "VfB",
                                     "VfL", "TSG", "RC", "CF", "CD", "UD", "SD", "Sportsklubben", "Idrettslaget"]
        if "?item wdt:P31 wd:Q5" in where or "P106" in where:
            cfg["derive"] = {"surname": {"top": 2000, "min_len": 4, "dominance": 1.5, "metric": "sitelinks"}}
        # Hva nordmenn kjenner: lesing av artikkelen på norsk Wikipedia veier tyngre enn antall språkutgaver.
        # Gjelder alle kategorier (spillet er norsk).
        cfg["source"]["pageviews"] = {"top": 2500 if (norsk or qid in PV_EXTRA) else 1200}
        cfg["rarity"]["weights"] = {"sitelinks": 0.45, "nowiki_views": 0.55}
        # Samme nivåskala for alle: små lister deles etter andel, store får faste tak (se rarity.auto_cuts)
        cfg["rarity"]["cuts"] = AUTO
        if qid in CITY_POP:
            # Byer: små steder med mange bot-artikler (Siligo, Uetersen) skal ikke regnes som kjente.
            cfg["source"]["population"] = True
            cfg["rarity"]["weights"] = {"sitelinks": 0.2, "population": 0.45, "nowiki_views": 0.35}
        if qid in EXTRA:
            cfg["source"]["extra"] = EXTRA[qid]
        if qid in DEMOTE:
            cfg["source"]["demote"] = DEMOTE[qid]
        if qid in ("historiske-personer", "malerier", "pattedyr"):
            cfg["aktiv"] = False   # for tunge spørringer / for få svar; kjøres bare ved behov: queue <id>
        with open(os.path.join(OUT, qid + ".json"), "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
        made += 1
    # fylker fra SSB
    with open(os.path.join(OUT, "fylker.json"), "w", encoding="utf-8") as f:
        json.dump({"question": "Nevn et norsk fylke", "category": "Geografi", "norsk": True, "status": "godkjent",
                   "modes": ["daily", "endless", "packs", "party"],
                   "attribution": "Kilde: Statistisk sentralbyrå (KLASS, NLOD 2.0) og Wikidata (CC0)",
                   "alias_exclude_regex": "(?i)(\\bfylke\\b|^fylket\\b)",
                   "source": {"type": "ssb_klass", "classification": 104, "date": "2026-01-01", "id_prefix": "fylke",
                              "exclude_codes": ["99"], "wikidata_join": {"property": "P2504"}},
                   "rarity": {"weights": {"population": 0.6, "sitelinks": 0.4}, "cuts": AUTO},
                   "validate": {"min_count": 15, "expected_count": 15, "max_shrink": 0.0,
                                "must_include": ["Vestland", "Trøndelag", "Akershus"], "must_exclude": ["Oslo kommune", "Bergen"]}},
                  f, ensure_ascii=False, indent=2)
    return made + 1


if __name__ == "__main__":
    print(make(), "konfigurasjoner skrevet")
