"""Sjeldenhet: fra objektive indikatorer til Dypdykks seks nivåer.

Metode (dokumentert og justerbar per spørsmål under "rarity" i konfigen):

1. Hver indikator (sitelinks, folketall, sidevisninger …) gjøres om til en
   persentil-rangering innen datasettet (0 = minst kjent, 1 = mest kjent).
   Rangering i stedet for råtall gjør at indikatorer med helt ulik skala kan
   kombineres, og at ekstreme verdier ikke dominerer.
2. Indikatorene vektes: score = Σ vekt_i · persentil_i. Mangler en verdi,
   brukes laveste persentil for den indikatoren (antatt lite kjent).
3. Objektene sorteres etter score. Plassen i rekkefølgen gjøres om til nivå
   via grenser («cuts»), enten som andel av listen ("percent") eller som
   absolutt plass ("rank"). Nivå 0 = Tare (vanligst) … 5 = Kjempeblekksprut.
4. Manuelle nivåer fra overrides vinner alltid.
5. Observerte svar fra spillerne (når de finnes) holdes adskilt: de lagres i
   feltet "observed" og blandes bare inn når et spørsmål har nok svar
   (min_observed), med vekten "observed_weight".

Dette er ESTIMERT sjeldenhet. Popularitet er ikke det samme som sannsynligheten
for at en spiller skriver svaret, og det er derfor grensene kan justeres.
"""
import bisect

DEFAULT = {"weights": {"sitelinks": 1.0}, "cuts": {"mode": "percent", "at": [0.03, 0.12, 0.30, 0.55, 0.85]},
           "min_observed": 500, "observed_weight": 0.7}


def _percentiles(values):
    """values: liste av tall eller None. Returnerer persentiler i [0,1]."""
    present = sorted(v for v in values if v is not None)
    n = len(present)
    out = []
    for v in values:
        if v is None or n == 0:
            out.append(0.0)
        else:
            lo = bisect.bisect_left(present, v)
            hi = bisect.bisect_right(present, v)
            out.append(((lo + hi) / 2) / n)
    return out


def score(entities, cfg):
    weights = cfg.get("weights", DEFAULT["weights"])
    tot = sum(weights.values()) or 1.0
    scores = [0.0] * len(entities)
    for metric, w in weights.items():
        pct = _percentiles([e["metrics"].get(metric) for e in entities])
        for i, p in enumerate(pct):
            scores[i] += w * p / tot
    for e, s in zip(entities, scores):
        e["score"] = round(s, 6)
    return entities


def assign_tiers(entities, cfg, observed=None):
    cuts = cfg.get("cuts", DEFAULT["cuts"])
    ordered = sorted(entities, key=lambda e: (-e["score"], e["label"]))
    n = len(ordered)
    obs_total = sum(observed.values()) if observed else 0
    use_obs = observed and obs_total >= cfg.get("min_observed", DEFAULT["min_observed"])
    if use_obs:
        w = cfg.get("observed_weight", DEFAULT["observed_weight"])
        share = {k: v / obs_total for k, v in observed.items()}
        top = max(share.values()) or 1
        for e in ordered:
            e["observed"] = observed.get(e["id"], 0)
            e["score"] = round((1 - w) * e["score"] + w * share.get(e["id"], 0) / top, 6)
        ordered.sort(key=lambda e: (-e["score"], e["label"]))
    for rank, e in enumerate(ordered):
        pos = rank / n if cuts["mode"] == "percent" else rank
        e["tier"] = bisect.bisect_right(cuts["at"], pos)
        e["rank"] = rank + 1
    return ordered
