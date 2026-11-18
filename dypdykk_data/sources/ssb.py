"""SSB KLASS – offisielle norske standarder (kommuner, fylker osv.).

KLASS er SSBs klassifikasjonsdatabase. Kommuneinndelingen er klassifikasjon 131.
Lisens: NLOD 2.0 – krever kildehenvisning («Kilde: Statistisk sentralbyrå»).

Konfig (under "source"):
  "type": "ssb_klass",
  "classification": 131,
  "date": "2026-01-01",            # gyldig per dato (tom = dagens dato)
  "id_prefix": "kommune",
  "exclude_codes": ["9999"],       # f.eks. «Uoppgitt»
  "wikidata_join": {"property": "P2504"}   # valgfritt: hent sitelinks/folketall/alias fra Wikidata
"""
import datetime
import re
import urllib.parse

from ..http import fetch_json, FetchError

BASE = "https://data.ssb.no/api/klass/v1/classifications/{c}/codesAt.json"
WD = "https://query.wikidata.org/sparql"


def collect(cfg, log, refresh=False, fixture=None):
    date = cfg.get("date") or datetime.date.today().isoformat()
    if fixture is not None:
        codes = fixture["codes"]["codes"]
    else:
        res = fetch_json(BASE.format(c=cfg["classification"]), {"date": date}, refresh=refresh, log=log)
        codes = res["codes"]
    excl = set(cfg.get("exclude_codes", []))
    codes = [c for c in codes if c["code"] not in excl and not re.fullmatch(r"\d*9999", c["code"])]
    log(f"SSB KLASS {cfg['classification']} per {date}: {len(codes)} koder")

    join = {}
    wj = cfg.get("wikidata_join")
    if wj:
        try:
            if fixture is not None:
                rows = fixture["wikidata"]["results"]["bindings"]
            else:
                # Store byer (Oslo, Bergen …) har ofte et eget by-objekt med langt flere sitelinks enn
                # kommune-objektet. Vi tar derfor også med objekter som er «hovedstad i» (P1376) kommunen.
                q = f"""SELECT ?item ?nr ?sl ?pop ?alias WHERE {{
  ?item wdt:{wj['property']} ?nr .
  FILTER NOT EXISTS {{ ?item wdt:P576 ?slutt . }}
  {{ ?item wikibase:sitelinks ?sl . }} UNION {{ ?by wdt:P1376 ?item ; wikibase:sitelinks ?sl . }}
  OPTIONAL {{ ?item wdt:P1082 ?pop . }}
  OPTIONAL {{ ?item skos:altLabel ?alias . FILTER(LANG(?alias) IN ("nb","nn","se","sma","smj","fkv")) }}
}}"""
                rows = fetch_json(WD, data="query=" + urllib.parse.quote(q) + "&format=json",
                                  refresh=refresh, log=log)["results"]["bindings"]
            for r in rows:
                nr = r["nr"]["value"]
                j = join.setdefault(nr, {"qid": r["item"]["value"].rsplit("/", 1)[-1], "sitelinks": 0,
                                         "population": None, "aliases": set()})
                j["sitelinks"] = max(j["sitelinks"], int(r["sl"]["value"]))
                if "pop" in r:
                    try:
                        j["population"] = max(float(r["pop"]["value"]), j["population"] or 0)
                    except ValueError:
                        pass
                if "alias" in r:
                    j["aliases"].add(r["alias"]["value"])
            log(f"Wikidata-kobling ({wj['property']}): {len(join)} treff")
        except (FetchError, KeyError) as e:
            log(f"ADVARSEL: Wikidata-kobling feilet ({e}). Fortsetter uten popularitetsdata.")
    return {"date": date, "codes": codes, "join": join}


def to_entities(data, cfg):
    out = []
    pre = cfg.get("id_prefix", "klass")
    for c in data["codes"]:
        name = c["name"].strip()
        # SSB bruker « - » mellom parallelle navn, f.eks. «Kárášjohka - Karasjok».
        parts = [p.strip() for p in re.split(r"\s+-\s+", name) if p.strip()]
        norsk = [p for p in parts if not re.search(r"[áčđŋšŧžÁČĐŊŠŦŽ]", p)]
        label = (norsk or parts)[0]
        aliases = [p for p in parts if p != label]
        j = data["join"].get(c["code"])
        metrics = {"sitelinks": None, "population": None}
        if j:
            aliases += sorted(j["aliases"])
            metrics = {"sitelinks": j["sitelinks"], "population": j["population"]}
        out.append({"id": f"{pre}:{c['code']}", "label": label, "aliases": aliases,
                    "metrics": metrics, "source": "ssb", "wikidata": j["qid"] if j else None})
    return out
