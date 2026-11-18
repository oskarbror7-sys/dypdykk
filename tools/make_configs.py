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
     "?item wdt:P106 wd:Q937857 ; wdt:P31 wd:Q5 ; wdt:P1532|wdt:P27 wd:Q20 .", 0, "l", NB, rank(5000),
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
     "?item wdt:P106 wd:Q628099 ; wdt:P31 wd:Q5 .", 3, "xl", NB, rank(30000),
     ["José Mourinho", "Alex Ferguson", "Ståle Solbakken", "Pep Guardiola"], ["Lionel Messi", "Magnus Carlsen"], 3000),
    ("f1-forere", "Nevn en Formel 1-fører", "Sport", False,
     "?item wdt:P106 wd:Q10841764 ; wdt:P31 wd:Q5 .", 0, "s", NB, PCT,
     ["Michael Schumacher", "Lewis Hamilton", "Ayrton Senna", "Max Verstappen"], ["Lionel Messi", "Petter Northug"], 300),
    ("langrenn", "Nevn en norsk langrennsløper", "Sport", True,
     "?item wdt:P106 wd:Q13382608 ; wdt:P27 wd:Q20 .", 0, "s", NB, PCT,
     ["Bjørn Dæhlie", "Marit Bjørgen", "Petter Northug", "Johannes Høsflot Klæbo"], ["Erling Haaland", "Magnus Carlsen"], 200),
    ("skiskyttere", "Nevn en skiskytter", "Sport", False,
     "?item wdt:P106 wd:Q16029547 ; wdt:P31 wd:Q5 .", 0, "l", NB, PCT,
     ["Ole Einar Bjørndalen", "Johannes Thingnes Bø", "Martin Fourcade"], ["Bjørn Dæhlie", "Erling Haaland"], 300),
    ("tennisspillere", "Nevn en tennisspiller", "Sport", False,
     "?item wdt:P106 wd:Q10833314 ; wdt:P31 wd:Q5 .", 2, "l", NB, rank(15000),
     ["Roger Federer", "Serena Williams", "Casper Ruud", "Rafael Nadal"], ["Lionel Messi", "Magnus Carlsen"], 2000),
    ("sjakkspillere", "Nevn en sjakkspiller", "Sport", False,
     "?item wdt:P106 wd:Q10873124 ; wdt:P31 wd:Q5 .", 2, "l", NB, rank(5000),
     ["Magnus Carlsen", "Garri Kasparov", "Bobby Fischer"], ["Lionel Messi", "Roger Federer"], 500),
    # --- Underholdning ---
    ("filmer", "Nevn en film", "Underholdning", False,
     "?item wdt:P31 wd:Q11424 .", 8, "xl", NB, rank(60000),
     ["Titanic", "Avatar", "Kon-Tiki", "Star Wars"], ["Norge", "Leonardo DiCaprio"], 10000),
    ("filmer-1990", "Nevn en film fra 1990-tallet", "Underholdning", False,
     "?item wdt:P31 wd:Q11424 ; wdt:P577 ?d . FILTER(YEAR(?d) >= 1990 && YEAR(?d) <= 1999)", 3, "l", NB, rank(15000),
     ["Titanic", "Pulp Fiction", "Jurassic Park", "Forrest Gump"], ["Avatar", "Star Wars"], 2000),
    ("norske-filmer", "Nevn en norsk film", "Underholdning", True,
     "?item wdt:P31 wd:Q11424 ; wdt:P495 wd:Q20 .", 0, "l", NB, PCT,
     ["Kon-Tiki", "Max Manus", "Bølgen", "Flåklypa Grand Prix"], ["Titanic", "Norge"], 500),
    ("tv-serier", "Nevn en TV-serie", "Underholdning", False,
     "?item wdt:P31 wd:Q5398426 .", 3, "xl", NB, rank(30000),
     ["Friends", "Skam", "Breaking Bad", "Game of Thrones"], ["Titanic", "Norge"], 5000),
    ("norske-tv-serier", "Nevn en norsk TV-serie", "Underholdning", True,
     "?item wdt:P31 wd:Q5398426 ; wdt:P495 wd:Q20 .", 0, "l", NB, PCT,
     ["Skam", "Lilyhammer", "Exit", "Okkupert"], ["Friends", "Titanic"], 200),
    ("skuespillere", "Nevn en skuespiller", "Underholdning", False,
     "?item wdt:P106 wd:Q33999 ; wdt:P31 wd:Q5 .", 20, "xl", NB, rank(40000),
     ["Leonardo DiCaprio", "Meryl Streep", "Aksel Hennie", "Tom Hanks"], ["Lionel Messi", "Norge"], 5000),
    ("norske-skuespillere", "Nevn en norsk skuespiller", "Underholdning", True,
     "?item wdt:P106 wd:Q33999 ; wdt:P27 wd:Q20 .", 0, "l", NB, rank(6000),
     ["Aksel Hennie", "Liv Ullmann", "Kristoffer Joner"], ["Leonardo DiCaprio", "Erling Haaland"], 800),
    ("artister", "Nevn en sanger eller artist", "Underholdning", False,
     "?item wdt:P106 wd:Q177220 ; wdt:P31 wd:Q5 .", 10, "xl", NB, rank(40000),
     ["Michael Jackson", "Taylor Swift", "Sissel Kyrkjebø", "Madonna"], ["Lionel Messi", "Norge"], 5000),
    ("norske-artister", "Nevn en norsk sanger eller artist", "Underholdning", True,
     "?item wdt:P106 wd:Q177220 ; wdt:P27 wd:Q20 .", 0, "l", NB, rank(4000),
     ["Sissel Kyrkjebø", "Alan Walker", "Sigrid", "Aurora"], ["Taylor Swift", "Erling Haaland"], 500),
    ("band", "Nevn et band eller en musikkgruppe", "Underholdning", False,
     "VALUES ?t { wd:Q215380 wd:Q5741069 } ?item wdt:P31 ?t .", 5, "xl", NB, rank(30000),
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
     "?item wdt:P105 wd:Q7432 ; wdt:P171+ wd:Q7377 ; wdt:P1843 ?nb . FILTER(LANG(?nb) = \"nb\")", 0, "l", NB_ONLY, PCT,
     ["Elg", "Ulv", "Isbjørn", "Blåhval"], ["Laks", "Ørn"], 300),
    ("fugler", "Nevn en fugl", "Natur", False,
     "?item wdt:P105 wd:Q7432 ; wdt:P171+ wd:Q5113 ; wdt:P1843 ?nb . FILTER(LANG(?nb) = \"nb\")", 0, "l", NB_ONLY, PCT,
     ["Kjøttmeis", "Gråspurv", "Havørn", "Pingvin"], ["Elg", "Laks"], 400),
    ("nobelprisvinnere", "Nevn en nobelprisvinner", "Vitenskap", False,
     "?item wdt:P166/wdt:P279* wd:Q7191 ; wdt:P31 wd:Q5 .", 0, "s", NB, PCT,
     ["Albert Einstein", "Marie Curie", "Fridtjof Nansen", "Jon Fosse"], ["Isaac Newton", "Lionel Messi"], 700),
    ("fysikere", "Nevn en fysiker", "Vitenskap", False,
     "?item wdt:P106 wd:Q169470 ; wdt:P31 wd:Q5 .", 10, "l", NB, rank(15000),
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
     "?item wdt:P106 wd:Q82955 ; wdt:P27 wd:Q20 .", 0, "l", NB, rank(10000),
     ["Jonas Gahr Støre", "Erna Solberg", "Gro Harlem Brundtland", "Jens Stoltenberg"], ["Barack Obama", "Erling Haaland"], 2000),
    ("forfattere", "Nevn en forfatter", "Kultur", False,
     "?item wdt:P106 wd:Q36180 ; wdt:P31 wd:Q5 .", 25, "xl", NB, rank(30000),
     ["Henrik Ibsen", "William Shakespeare", "Jo Nesbø", "Astrid Lindgren"], ["Lionel Messi", "Norge"], 5000),
    ("norske-forfattere", "Nevn en norsk forfatter", "Kultur", True,
     "?item wdt:P106 wd:Q36180 ; wdt:P27 wd:Q20 .", 0, "l", NB, rank(6000),
     ["Henrik Ibsen", "Jo Nesbø", "Sigrid Undset", "Knut Hamsun"], ["William Shakespeare", "Erling Haaland"], 1000),
    ("boker", "Nevn en bok, roman eller et skuespill (tittel)", "Kultur", False,
     "VALUES ?t { wd:Q7725634 wd:Q8261 wd:Q25379 wd:Q47461344 wd:Q571 } ?item wdt:P31 ?t .", 12, "l", NB, rank(20000),
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
     "?item wdt:P106 wd:Q1028181 ; wdt:P31 wd:Q5 .", 20, "l", NB, rank(8000),
     ["Edvard Munch", "Pablo Picasso", "Vincent van Gogh", "Leonardo da Vinci"], ["Lionel Messi", "Henrik Ibsen"], 1000),
    ("komponister", "Nevn en komponist", "Kultur", False,
     "?item wdt:P106 wd:Q36834 ; wdt:P31 wd:Q5 .", 20, "l", NB, rank(8000),
     ["Edvard Grieg", "Wolfgang Amadeus Mozart", "Ludwig van Beethoven", "Johann Sebastian Bach"], ["Lionel Messi", "Henrik Ibsen"], 1000),
    ("filosofer", "Nevn en filosof", "Kultur", False,
     "?item wdt:P106 wd:Q4964182 ; wdt:P31 wd:Q5 .", 25, "l", NB, rank(5000),
     ["Platon", "Aristoteles", "Immanuel Kant", "Arne Næss"], ["Lionel Messi", "Edvard Munch"], 500),
    ("oppfinnere", "Nevn en oppfinner", "Vitenskap", False,
     "?item wdt:P106 wd:Q205375 ; wdt:P31 wd:Q5 .", 15, "l", NB, rank(3000),
     ["Thomas Edison", "Nikola Tesla", "Alexander Graham Bell", "Alfred Nobel"], ["Lionel Messi", "Edvard Munch"], 300),
    ("astronauter", "Nevn en astronaut eller kosmonaut", "Vitenskap", False,
     "?item wdt:P106 wd:Q11631 ; wdt:P31 wd:Q5 .", 0, "s", NB, PCT,
     ["Neil Armstrong", "Jurij Gagarin", "Juri Gagarin", "Buzz Aldrin"], ["Lionel Messi", "Albert Einstein"], 300),
    ("ishockeyspillere", "Nevn en ishockeyspiller", "Sport", False,
     "?item wdt:P106 wd:Q11774891 ; wdt:P31 wd:Q5 .", 4, "l", NB, rank(10000),
     ["Wayne Gretzky", "Mats Zuccarello", "Sidney Crosby"], ["Lionel Messi", "Petter Northug"], 1000),
    ("handballspillere", "Nevn en håndballspiller", "Sport", False,
     "?item wdt:P106 wd:Q12840545 ; wdt:P31 wd:Q5 .", 3, "l", NB, rank(6000),
     ["Sander Sagosen", "Nora Mørk", "Mikkel Hansen"], ["Lionel Messi", "Petter Northug"], 800),
    ("alpinister", "Nevn en alpinist", "Sport", False,
     "?item wdt:P106 wd:Q4144610 ; wdt:P31 wd:Q5 .", 2, "l", NB, rank(4000),
     ["Aksel Lund Svindal", "Kjetil André Aamodt", "Mikaela Shiffrin", "Lindsey Vonn"], ["Bjørn Dæhlie", "Lionel Messi"], 500),
    ("skihoppere", "Nevn en skihopper", "Sport", False,
     "?item wdt:P106 wd:Q13382603 ; wdt:P31 wd:Q5 .", 2, "l", NB, rank(3000),
     ["Halvor Egner Granerud", "Matti Nykänen", "Anders Jacobsen", "Maren Lundby"], ["Bjørn Dæhlie", "Lionel Messi"], 400),
    ("boksere", "Nevn en bokser", "Sport", False,
     "?item wdt:P106 wd:Q11338576 ; wdt:P31 wd:Q5 .", 5, "l", NB, rank(5000),
     ["Muhammad Ali", "Mike Tyson", "Cecilia Brækhus"], ["Lionel Messi", "Petter Northug"], 500),
    ("basketballspillere", "Nevn en basketballspiller", "Sport", False,
     "?item wdt:P106 wd:Q3665646 ; wdt:P31 wd:Q5 .", 5, "l", NB, rank(10000),
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
]


def make():
    os.makedirs(OUT, exist_ok=True)
    made = 0
    for row in KATALOG:
        qid = row[0]
        if row[1] is None:
            continue
        _, q, cat, norsk, where, minsl, size, langs, cuts, inn, ut, minc = row
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
        if qid in ("norske-fotballklubber", "fotballklubber"):
            cfg["strip_suffixes"] = ["FK", "Fotballklubb", "Fotball", "IL", "BK", "SK", "IF", "FC", "F.C.", "AFC", "CF",
                                     "Toppfotball", "Elite", "Fotballforening"]
            cfg["strip_prefixes"] = ["SK", "IL", "FK", "IK", "BK", "FC", "AFC", "AC", "AS", "SS", "SSC", "SV", "VfB",
                                     "VfL", "TSG", "RC", "CF", "CD", "UD", "SD", "Sportsklubben", "Idrettslaget"]
        if "?item wdt:P31 wd:Q5" in where or "P106" in where:
            cfg["derive"] = {"surname": {"top": 2000, "min_len": 4, "dominance": 1.5, "metric": "sitelinks"}}
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
                   "rarity": {"weights": {"population": 0.6, "sitelinks": 0.4}, "cuts": PCT},
                   "validate": {"min_count": 15, "expected_count": 15, "max_shrink": 0.0,
                                "must_include": ["Vestland", "Trøndelag", "Akershus"], "must_exclude": ["Oslo kommune", "Bergen"]}},
                  f, ensure_ascii=False, indent=2)
    return made + 1


if __name__ == "__main__":
    print(make(), "konfigurasjoner skrevet")
