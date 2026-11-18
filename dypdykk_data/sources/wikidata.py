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
        # «extra»: ekstra utvalg med egen spørring og eget minstekrav, f.eks. alle norske artister uansett hvor
        # kjente de er internasjonalt, i tillegg til verdens artister med minst 10 Wikipedia-utgaver.
        for sub in [cfg] + [dict(cfg, **x) for x in cfg.get("extra", [])]:
            for lo, hi in sub["bands"]:
                if hi < sub.get("min_sitelinks", 0):
                    continue   # båndet ligger under minstekravet og ville gitt 0 treff
                lo = max(lo, sub.get("min_sitelinks", 0))
                lr = _fetch_band(sub, lo, hi, "label", log, refresh)
                ar = _fetch_band(sub, lo, hi, "alias", log, refresh)
                log(f"Wikidata bånd sitelinks {lo}-{hi}: {len(lr)} etikettrader, {len(ar)} aliasrader")
                label_rows += lr
                alias_rows += ar
    d_cfg = cfg.get("demote") or {}
    demote = (collect_demote(cfg, log, refresh) if not d_cfg.get("occupations") else {}) if fixture is None else fixture.get("demote", {})
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
    if fixture is None and cfg.get("pageviews"):
        try:
            collect_nowiki_views(items, cfg["pageviews"], log, refresh)
        except Exception as ex:   # sidevisninger er et tillegg: feiler de, rangeres det på Wikipedia-utgaver som før
            log(f"Sidevisninger fra norsk Wikipedia utilgjengelig ({ex}); bruker bare Wikipedia-utgaver")
    if fixture is None and d_cfg.get("occupations"):
        cand = [q for q, it in items.items() if it["sitelinks"] >= d_cfg["min_sitelinks"]]
        demote = _demote_by_occupation(cfg, d_cfg, log, refresh, cand)
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
    if d.get("occupations"):
        return _demote_by_occupation(cfg, d, log, refresh)
    q = f"""SELECT ?item (COUNT(DISTINCT ?x) AS ?n) WHERE {{
  {cfg['where']}
  ?item wikibase:sitelinks ?sl . FILTER(?sl >= {d['min_sitelinks']})
  OPTIONAL {{ ?item p:{d["property"]} ?x . }}
}} GROUP BY ?item HAVING(COUNT(DISTINCT ?x) <= {d['max_count']})"""
    rows = _run(q, log, refresh)
    out = {r["item"]["value"].rsplit("/", 1)[-1]: int(r["n"]["value"]) for r in rows}
    log(f"Kjente for noe annet ({d['property']} ≤ {d['max_count']}, sitelinks ≥ {d['min_sitelinks']}): {len(out)}")
    return out


NOWIKI_API = "https://no.wikipedia.org/w/api.php"


def collect_nowiki_views(items, pv, log, refresh):
    """Hvor mye artikkelen på norsk (bokmål) Wikipedia leses de siste 60 dagene.
    Et mye bedre mål enn antall språkutgaver på hva nordmenn faktisk kjenner til: Svalbard-topper og
    black metal-band har mange bot-artikler på andre språk, men få norske lesere.
    Bare de «top» mest kjente (etter språkutgaver) slås opp; resten får 0. Objekter uten norsk artikkel får 0."""
    top = sorted(items, key=lambda q: -items[q]["sitelinks"])[:int(pv.get("top", 3000))]
    titles = {}
    for i in range(0, len(top), 250):
        vals = " ".join("wd:" + q for q in top[i:i + 250])
        for r in _run(f"""SELECT ?item ?t WHERE {{ VALUES ?item {{ {vals} }}
  ?a schema:about ?item ; schema:isPartOf <https://no.wikipedia.org/> ; schema:name ?t . }}""", log, refresh):
            titles[r["t"]["value"]] = r["item"]["value"].rsplit("/", 1)[-1]
    for q in items:
        items[q]["nowiki_views"] = 0 if q in top else None
    names = list(titles)
    got = 0
    for i in range(0, len(names), 50):
        batch = names[i:i + 50]
        base = {"action": "query", "prop": "pageviews", "pvipdays": 60, "titles": "|".join(batch),
                "format": "json", "formatversion": 2}
        cont = {}
        # prop=pageviews gir bare tall for et begrenset antall sider per svar (alfabetisk!) og krever
        # «continue» for resten. Uten dette fikk bare sidene tidlig i alfabetet sidevisninger.
        for _ in range(20):
            res = fetch_json(NOWIKI_API, params=dict(base, **cont), refresh=refresh, log=log)
            q_ = res.get("query", {})
            back = {n["to"]: n["from"] for n in q_.get("normalized", [])}
            for page in q_.get("pages", []):
                if "pageviews" not in page:
                    continue
                t = back.get(page["title"], page["title"])
                qid = titles.get(t)
                if qid:
                    items[qid]["nowiki_views"] = sum(v or 0 for v in (page.get("pageviews") or {}).values())
                    got += 1
            if "continue" not in res:
                break
            cont = res["continue"]
    log(f"Sidevisninger norsk Wikipedia: {got} artikler av {len(top)} kjente")


def _keep_spec(spec):
    """«P264» = har egenskapen, «P54:3» = minst 3 verdier, «^P86:15» = minst 15 objekter peker hit med P86,
    «P101=Q395» = har akkurat denne verdien."""
    inv = spec.startswith("^")
    spec = spec.lstrip("^")
    val = None
    if "=" in spec:
        spec, val = spec.split("=", 1)
    prop, _, n = spec.partition(":")
    return inv, prop, val, int(n or 1)


def _demote_by_occupation(cfg, d, log, refresh, cand):
    """Personer i kategorien som OGSÅ har et av yrkene i «occupations» (f.eks. skuespiller, politiker),
    men ingen av kjennetegnene i «keep_props» / «keep_occupations» på at de faktisk er kjent for kategorien.
    Eksempel: Charlie Chaplin står som sanger, men er kjent som filmskaper. Gyldig svar, men sjeldent å tenke på,
    så det får nivået «tier» (standard 5). Kandidatene er de kjente objektene vi allerede har hentet; de sjekkes
    i små bolker, så Wikidata aldri får én tung spørring."""
    prop = d.get("prop", "P106")
    occ = " ".join("wd:" + o for o in d["occupations"])
    hit = []
    for i in range(0, len(cand), 250):
        vals = " ".join("wd:" + c for c in cand[i:i + 250])
        rows = _run(f"SELECT DISTINCT ?item WHERE {{ VALUES ?item {{ {vals} }} VALUES ?o2 {{ {occ} }} ?item wdt:{prop} ?o2 . }}",
                    log, refresh)
        hit += [r["item"]["value"].rsplit("/", 1)[-1] for r in rows]
    specs = list(d.get("keep_props", [])) + ["P106=" + o for o in d.get("keep_occupations", [])]
    keep = set()
    for spec in specs:
        inv, kprop, val, n = _keep_spec(spec)
        for i in range(0, len(hit), 250):
            vals = " ".join("wd:" + c for c in hit[i:i + 250])
            if val:
                body = f"?item wdt:{kprop} wd:{val} ."
            else:
                body = f"?x wdt:{kprop} ?item ." if inv else f"?item wdt:{kprop} ?x ."
            if n <= 1:
                qq = f"SELECT DISTINCT ?item WHERE {{ VALUES ?item {{ {vals} }} {body} }}"
            else:
                qq = (f"SELECT ?item (COUNT(DISTINCT ?x) AS ?n) WHERE {{ VALUES ?item {{ {vals} }} {body} }} "
                      f"GROUP BY ?item HAVING(COUNT(DISTINCT ?x) >= {n})")
            for r in _run(qq, log, refresh):
                keep.add(r["item"]["value"].rsplit("/", 1)[-1])
    out = {c: 0 for c in hit if c not in keep}
    log(f"Kjente for noe annet: {len(out)} av {len(hit)} med annet yrke (av {len(cand)} kjente; behold: {', '.join(specs) or '–'})")
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
             "metrics": {"sitelinks": it["sitelinks"], "population": it["population"], "nowiki_views": it.get("nowiki_views")},
             "source": "wikidata"}
        if it.get("demoted"):
            e["pinned_tier"] = cfg["demote"].get("tier", 5)
            e["note"] = "kjent for noe annet"
        out.append(e)
    return out
