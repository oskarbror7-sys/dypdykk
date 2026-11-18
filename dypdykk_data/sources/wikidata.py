"""Wikidata via SPARQL (query.wikidata.org).

Store kategorier (f.eks. 150 000 fotballspillere) kan ikke hentes i én spørring
uten tidsavbrudd (grensen er 60 s). Derfor deles uttrekket i «bånd» etter antall
sitelinks (hvor mange Wikipedia-utgaver objektet har). Feiler et bånd, deles det
automatisk videre etter Q-nummer.

Konfig (i config/questions/<id>.json, under "source"):
  "type": "wikidata",
  "where": "?item wdt:P31 wd:Q5 ; wdt:P106 wd:Q937857 .",   # hvem som hører til kategorien
  "min_sitelinks": 3,
  "bands": [[3,3],[4,5],[6,9],[10,19],[20,100000]],
  "label_langs": ["nb","nn","no","mul","en"],
  "alias_langs": ["nb","nn","mul","en"],
  "population": false                                       # hent P1082 (folketall)
"""
import urllib.parse

from ..http import fetch_json, FetchError

ENDPOINT = "https://query.wikidata.org/sparql"
QRANGES = [(0, 2_000_000), (2_000_000, 10_000_000), (10_000_000, 30_000_000),
           (30_000_000, 60_000_000), (60_000_000, 10**10)]


def _langs(langs):
    return ",".join(f'"{l}"' for l in langs)


def _query(cfg, lo, hi, kind, qr=None):
    pred = "rdfs:label" if kind == "label" else "skos:altLabel"
    langs = cfg["label_langs"] if kind == "label" else cfg["alias_langs"]
    qfilter = ""
    if qr:
        qfilter = (f'BIND(xsd:integer(STRAFTER(STR(?item), "/entity/Q")) AS ?qn) '
                   f'FILTER(?qn >= {qr[0]} && ?qn < {qr[1]})')
    pop = ""
    if kind == "label" and cfg.get("population"):
        pop = "OPTIONAL { ?item wdt:P1082 ?pop . }"
    extra_sel = " ?pop" if pop else ""
    return f"""SELECT ?item ?sl ?txt ?lang{extra_sel} WHERE {{
  {cfg['where']}
  ?item wikibase:sitelinks ?sl .
  FILTER(?sl >= {lo} && ?sl <= {hi})
  {qfilter}
  ?item {pred} ?txt . BIND(LANG(?txt) AS ?lang)
  FILTER(?lang IN ({_langs(langs)}))
  {pop}
}}"""


def _run(q, log, refresh, retries=3):
    res = fetch_json(ENDPOINT, data="query=" + urllib.parse.quote(q) + "&format=json",
                     refresh=refresh, log=log, timeout=75, retries=retries)
    return res["results"]["bindings"]


def _fetch_band(cfg, lo, hi, kind, log, refresh):
    try:
        return _run(_query(cfg, lo, hi, kind), log, refresh, retries=2)
    except FetchError as e:
        log(f"Bånd {lo}-{hi} ({kind}) feilet ({e}); deler opp etter Q-nummer")
    rows = []
    for a, b in QRANGES:
        rows += _split(cfg, lo, hi, kind, a, b, log, refresh, depth=0)
    return rows


def _split(cfg, lo, hi, kind, a, b, log, refresh, depth):
    """Henter Q-intervallet [a,b); halverer intervallet rekursivt hvis det fortsatt er for stort."""
    try:
        return _run(_query(cfg, lo, hi, kind, (a, b)), log, refresh, retries=2)
    except FetchError as e:
        if depth >= 6 or b - a < 2000:
            raise
        m = (a + b) // 2
        log(f"  Q{a}-Q{b} for stort ({e}); deler i to")
        return (_split(cfg, lo, hi, kind, a, m, log, refresh, depth + 1) +
                _split(cfg, lo, hi, kind, m, b, log, refresh, depth + 1))


def collect(cfg, log, refresh=False, fixture=None):
    """Returnerer {qid: {"labels":{lang:txt}, "aliases":[(lang,txt)], "sitelinks":n, "population":n|None}}."""
    if fixture is not None:
        label_rows, alias_rows = fixture["labels"]["results"]["bindings"], fixture["aliases"]["results"]["bindings"]
    else:
        label_rows, alias_rows = [], []
        for lo, hi in cfg["bands"]:
            if hi < cfg.get("min_sitelinks", 0):
                continue   # båndet ligger under minstekravet og ville gitt 0 treff
            lo = max(lo, cfg.get("min_sitelinks", 0))
            lr = _fetch_band(cfg, lo, hi, "label", log, refresh)
            ar = _fetch_band(cfg, lo, hi, "alias", log, refresh)
            log(f"Wikidata bånd sitelinks {lo}-{hi}: {len(lr)} etikettrader, {len(ar)} aliasrader")
            label_rows += lr
            alias_rows += ar
    demote = collect_demote(cfg, log, refresh) if fixture is None else fixture.get("demote", {})
    if fixture is not None:
        demote = fixture.get("demote", {})
    items = {}
    for r in label_rows:
        qid = r["item"]["value"].rsplit("/", 1)[-1]
        it = items.setdefault(qid, {"labels": {}, "aliases": [], "sitelinks": 0, "population": None})
        it["sitelinks"] = max(it["sitelinks"], int(r["sl"]["value"]))
        it["labels"][r["lang"]["value"]] = r["txt"]["value"]
        if "pop" in r:
            try:
                p = float(r["pop"]["value"])
                it["population"] = max(p, it["population"] or 0)
            except ValueError:
                pass
    for r in alias_rows:
        qid = r["item"]["value"].rsplit("/", 1)[-1]
        if qid in items:
            items[qid]["aliases"].append((r["lang"]["value"], r["txt"]["value"]))
    for qid in demote:
        if qid in items:
            items[qid]["demoted"] = True
    return items


def collect_demote(cfg, log, refresh=False):
    """Kjente personer der kategorien ikke er det de er kjent for (f.eks. Albert Camus som
    fotballspiller). Kjennetegn: mange sitelinks, men få eller ingen lag (P54).
    Slike svar er gyldige, men sjeldne å tenke på, og får derfor et høyt nivå."""
    d = cfg.get("demote")
    if not d:
        return {}
    q = f"""SELECT ?item (COUNT(DISTINCT ?x) AS ?n) WHERE {{
  {cfg['where']}
  ?item wikibase:sitelinks ?sl . FILTER(?sl >= {d['min_sitelinks']})
  OPTIONAL {{ ?item p:{d["property"]} ?x . }}
}} GROUP BY ?item HAVING(COUNT(DISTINCT ?x) <= {d['max_count']})"""
    rows = _run(q, log, refresh)
    out = {r["item"]["value"].rsplit("/", 1)[-1]: int(r["n"]["value"]) for r in rows}
    log(f"Kjente for noe annet ({d['property']} ≤ {d['max_count']}, sitelinks ≥ {d['min_sitelinks']}): {len(out)}")
    return out


def to_entities(items, cfg):
    """Gjør Wikidata-objekter om til felles format for rørledningen."""
    out = []
    for qid, it in items.items():
        label = None
        for lang in cfg["label_langs"]:
            if lang in it["labels"]:
                label = it["labels"][lang]
                break
        if not label:
            continue
        aliases = [t for l, t in sorted(it["labels"].items()) if t != label]
        aliases += [t for _, t in it["aliases"]]
        e = {"id": qid, "label": label, "aliases": aliases,
             "metrics": {"sitelinks": it["sitelinks"], "population": it["population"]}, "source": "wikidata"}
        if it.get("demoted"):
            e["pinned_tier"] = cfg["demote"].get("tier", 5)
            e["note"] = "kjent for noe annet"
        out.append(e)
    return out
