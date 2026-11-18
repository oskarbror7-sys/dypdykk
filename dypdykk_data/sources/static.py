"""Håndlagde, lukkede lister (f.eks. «Nevn en planet»).

Brukes for små kategorier der en ekstern kilde ikke gir noe ekstra. Formatet er
det samme som spillet bruker: nivåer skilt med «|», svar med «,», alias med «/».
Nivåene her er manuelt satt, og regnes som overstyrte (ikke beregnet).

Konfig (under "source"):
  "type": "static",
  "answers": "Jorden/Jorda,Mars|Jupiter,Saturn|..."
"""


def collect(cfg, log, refresh=False, fixture=None):
    groups = cfg["answers"].split("|")
    out = []
    for tier, grp in enumerate(groups):
        for item in grp.split(","):
            names = [n.strip() for n in item.split("/") if n.strip()]
            if names:
                out.append((tier, names))
    log(f"Statisk liste: {len(out)} svar")
    return {"items": out}


def to_entities(data, cfg):
    ents = []
    for i, (tier, names) in enumerate(data["items"]):
        ents.append({"id": f"static:{i}", "label": names[0], "aliases": names[1:],
                     "metrics": {"manual_rank": -i}, "source": "manuell", "pinned_tier": tier})
    return ents
