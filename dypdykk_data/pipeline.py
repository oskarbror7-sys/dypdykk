"""Rørledningen: kilde → rensing → alias → kollisjoner → sjeldenhet → kontroll → staging → publisering.

Datastier (relativt til prosjektroten):
  config/questions/<id>.json     – spørsmålsdefinisjon
  overrides/<id>.json            – manuelle rettelser (røres aldri av importen)
  overrides/observed/<id>.json   – observerte svarfrekvenser fra spillere (valgfritt)
  tests/fixtures/<id>/*.json     – testdata for --offline
  staging/<id>.json              – fullt resultat med ID, poeng og kilder
  review/<id>.json               – oppføringer som bør sjekkes manuelt
  logs/<id>-<tid>.log            – logg for hver kjøring
  site/data/<id>.json            – publisert, kompakt fil som spillet leser
  site/data/index.json           – liste over publiserte datasett
  site/data/archive/<id>/        – tidligere publiserte versjoner (for rollback)
"""
import datetime
import glob
import json
import os
import re
import shutil
import time

from .normalize import norm, clean_label
from . import rarity
from .sources import wikidata, ssb, static

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Skrivbare mapper (staging, review, logs, overrides) kan flyttes med DYPDYKK_WORK, f.eks. i tester.
WORK = os.environ.get("DYPDYKK_WORK", ROOT)
SITE = os.environ.get("DYPDYKK_SITE", os.path.join(ROOT, "site"))
_WRITABLE = {"staging", "review", "logs", "overrides"}
SOURCES = {"wikidata": wikidata, "ssb_klass": ssb, "static": static}
KIND_RANK = {"label": 0, "alias": 1, "derived": 2}


def p(*parts):
    base = WORK if parts and parts[0] in _WRITABLE else ROOT
    return os.path.join(base, *parts)


def load_json(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path, obj, compact=False):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        if compact:
            json.dump(obj, f, ensure_ascii=False, separators=(",", ":"))
        else:
            json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)   # atomisk: en halvskrevet fil blir aldri synlig


def list_configs():
    return sorted(os.path.splitext(os.path.basename(f))[0] for f in glob.glob(p("config", "questions", "*.json")))


class Logger:
    def __init__(self, qid, quiet=False):
        os.makedirs(p("logs"), exist_ok=True)
        self.path = p("logs", f"{qid}-{datetime.datetime.now():%Y%m%d-%H%M%S}.log")
        self.quiet = quiet
        self.lines = []

    def __call__(self, msg):
        line = f"{datetime.datetime.now():%H:%M:%S} {msg}"
        self.lines.append(line)
        if not self.quiet:
            print(line, flush=True)
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(line + "\n")


def _fixture(qid):
    d = p("tests", "fixtures", qid)
    if not os.path.isdir(d):
        raise FileNotFoundError(f"Ingen testdata for {qid} i {d}")
    return {os.path.splitext(os.path.basename(f))[0]: load_json(f) for f in glob.glob(os.path.join(d, "*.json"))}


def _dedupe(entities, log):
    """Samme ID flere ganger i kilden -> ett objekt (alias og høyeste måltall slås sammen)."""
    by_id, order = {}, []
    for e in entities:
        if e["id"] not in by_id:
            by_id[e["id"]] = e
            order.append(e["id"])
            continue
        a = by_id[e["id"]]
        a["aliases"] = list(a["aliases"]) + [e["label"]] + list(e["aliases"])
        for k, v in e["metrics"].items():
            if v is not None and (a["metrics"].get(k) is None or v > a["metrics"][k]):
                a["metrics"][k] = v
    if len(order) < len(entities):
        log(f"Slo sammen {len(entities) - len(order)} duplikater med samme ID")
    return [by_id[i] for i in order]


def _lk(label):
    """Nøkler en etikett kan treffes på i overstyringer: rå etikett og rensket etikett («X (opera)» -> «X»)."""
    label = label or ""
    return {k for k in (norm(label), norm(clean_label(label) or "")) if k}


def _apply_overrides(entities, ov, log):
    # Etiketter som starter med liten bokstav (vanlig for arter: «gråspurv») vises med stor forbokstav i spillet
    for e in entities:
        lab = e.get("label") or ""
        if lab[:1].islower():
            e["label"] = lab[:1].upper() + lab[1:]
    # Wikidata-objekter for wikisider (kategorier, maler, prosjektsider) er aldri gyldige svar
    ns = re.compile(r"^(Category|Kategori|Template|Mal|Wikipedia|MediaWiki|Portal|Help|Hjelp|Module|Modul|User|Bruker|Draft)\s*:", re.I)
    before = len(entities)
    entities = [e for e in entities if not ns.match(e.get("label") or "")]
    if len(entities) < before:
        log(f"Fjernet {before - len(entities)} wikisider (Category:, Template: …)")
    removed = set(ov.get("remove", []))
    if removed:
        before = len(entities)
        entities = [e for e in entities if e["id"] not in removed]
        log(f"Overstyring: fjernet {before - len(entities)} oppføringer")
    if ov.get("remove_labels"):
        bad = {norm(x) for x in ov["remove_labels"]}
        before = len(entities)
        entities = [e for e in entities if not (_lk(e["label"]) & bad)]
        log(f"Overstyring: fjernet {before - len(entities)} etter navn")
    # Navnebaserte rettelser (praktisk når Wikidata-ID-en ikke er kjent): ny etikett, fast nivå, alias-regler
    if ov.get("relabel"):
        rl = {norm(k): v for k, v in ov["relabel"].items()}
        n = 0
        for e in entities:
            new = next((rl[k] for k in _lk(e["label"]) if k in rl), None)
            if new:
                e["aliases"] = list(e["aliases"]) + [e["label"]]
                e["orig_label"] = e["label"]
                e["label"] = new
                n += 1
        log(f"Overstyring: nye etiketter for {n}")
    if ov.get("tier_labels"):
        tl = {norm(k): v for k, v in ov["tier_labels"].items()}
        for e in entities:
            for k in _lk(e["label"]) | _lk(e.get("orig_label")):
                if k in tl:
                    e["pinned_tier"] = tl[k]
                    break
    if ov.get("alias_labels"):
        al = {norm(k): v for k, v in ov["alias_labels"].items()}
        for e in entities:
            extra = next((al[k] for k in _lk(e["label"]) if k in al), None)
            if extra:
                e["aliases"] = list(e["aliases"]) + [x for x in extra if x not in e["aliases"]]
                e["manual_aliases"] = list(e.get("manual_aliases", [])) + extra
    for old, new in ov.get("alias_rules", []):
        for e in entities:
            for t in [e["label"]] + list(e["aliases"]):
                if old.lower() in t.lower():
                    alt = re.sub(re.escape(old), new, t, flags=re.I)
                    if alt != t and alt not in e["aliases"]:
                        e["aliases"] = list(e["aliases"]) + [alt]
    for add in ov.get("add", []):
        entities.append({"id": add["id"], "label": add["label"], "aliases": add.get("aliases", []),
                         "metrics": add.get("metrics", {}), "source": "manuell", "pinned_tier": add.get("tier")})
    by_id = {e["id"]: e for e in entities}
    for eid, al in ov.get("aliases", {}).items():
        if eid in by_id:
            by_id[eid]["aliases"] = list(by_id[eid]["aliases"]) + al
            by_id[eid]["manual_aliases"] = al
    for eid, t in ov.get("tier", {}).items():
        if eid in by_id:
            by_id[eid]["pinned_tier"] = t
    for eid, lab in ov.get("label", {}).items():
        if eid in by_id:
            old = by_id[eid]["label"]
            by_id[eid]["label"] = lab
            by_id[eid]["aliases"] = list(by_id[eid]["aliases"]) + [old]
    return entities


def _derive(entities, cfg):
    """Avledede alias, f.eks. etternavn for de mest kjente («Haaland», «Messi»)."""
    d = cfg.get("derive", {})
    sur = d.get("surname")
    if not sur:
        return
    ranked = sorted(entities, key=lambda e: -e["score"])[: sur.get("top", 3000)]
    for e in ranked:
        parts = e["label"].split()
        if len(parts) >= 2:
            last = parts[-1]
            if len(norm(last)) >= sur.get("min_len", 4) and last.lower() not in ("jr", "jr.", "junior", "filho", "neto"):
                e.setdefault("derived", []).append(last)


def build(qid, offline=False, refresh=False, quiet=False):
    cfg = load_json(p("config", "questions", qid + ".json"))
    if not cfg:
        raise SystemExit(f"Fant ikke config/questions/{qid}.json")
    log = Logger(qid, quiet)
    t0 = time.time()
    src_cfg = cfg["source"]
    mod = SOURCES[src_cfg["type"]]
    log(f"=== Bygger «{cfg['question']}» ({qid}) fra {src_cfg['type']}{' [OFFLINE TESTDATA]' if offline else ''}")

    raw = mod.collect(src_cfg, log, refresh=refresh, fixture=_fixture(qid) if offline else None)
    entities = mod.to_entities(raw, src_cfg)
    log(f"Fra kilde: {len(entities)} objekter")
    entities = _dedupe(entities, log)

    ov = load_json(p("overrides", qid + ".json"), {})
    entities = _apply_overrides(entities, ov, log)
    reject = {norm(a) for a in ov.get("reject_alias", [])}
    alias_ex = re.compile(cfg["alias_exclude_regex"]) if cfg.get("alias_exclude_regex") else None

    # 1) Rens etiketter og alias
    review = []
    kept = []
    for e in entities:
        lab = clean_label(e["label"])
        if not lab and (e.get("source") == "manuell" or e.get("orig_label")) and (e["label"] or "").strip():
            lab = e["label"].strip()   # bevisst valgt kort navn, f.eks. «X» eller programmeringsspråket «C»
        if not lab:
            review.append({"id": e["id"], "problem": "ugyldig etikett", "label": e["label"]})
            continue
        e["label"] = lab
        seen, al = {norm(lab)}, []
        for a in e.get("aliases", []):
            c = clean_label(a)
            if c and alias_ex and alias_ex.search(c):
                continue
            if c and norm(c) not in seen and norm(c) not in reject:
                seen.add(norm(c))
                al.append(c)
        e["aliases"] = al
        kept.append(e)
    entities = kept

    # 1b) Korte alias uten selskapsendelser («Tesla, Inc.» -> «Tesla»)
    if cfg.get("strip_suffixes"):
        suf = re.compile(r"[,\s]+(" + "|".join(re.escape(x) for x in cfg["strip_suffixes"]) + r")\.?$", re.I)
        for e in entities:
            for n in [e["label"]] + list(e["aliases"]):
                short = n
                for _ in range(3):
                    short = suf.sub("", short).strip()
                if short != n and len(norm(short)) >= 2 and short not in e["aliases"] and short != e["label"]:
                    e["aliases"].append(short)

    # 1c) Korte alias uten klubbforstavelser («SK Brann» -> «Brann», «FC Barcelona» -> «Barcelona»)
    if cfg.get("strip_prefixes"):
        pre = re.compile(r"^(" + "|".join(re.escape(x) for x in cfg["strip_prefixes"]) + r")\.?\s+", re.I)
        for e in entities:
            for n in [e["label"]] + list(e["aliases"]):
                short = pre.sub("", n).strip()
                if short != n and len(norm(short)) >= 3 and short not in e["aliases"] and short != e["label"]:
                    e["aliases"].append(short)

    # 2) Sjeldenhetsscore (før kollisjoner, så den mest kjente vinner tvetydige navn)
    rkey = "rarity_offline" if offline and "rarity_offline" in cfg else "rarity"
    rcfg = {**rarity.DEFAULT, **cfg.get(rkey, {})}
    rarity.score(entities, rcfg)
    _derive(entities, cfg)

    # 3) Bygg nøkkel -> kandidater og løs kollisjoner
    keymap = {}
    sur = cfg.get("derive", {}).get("surname", {})
    dominance, dom_metric = sur.get("dominance", 1.5), sur.get("metric", "sitelinks")
    for e in entities:
        for kind, names in (("label", [e["label"]]), ("alias", e["aliases"]), ("derived", e.get("derived", []))):
            for n in names:
                k = norm(n)
                if k and k not in reject:
                    keymap.setdefault(k, []).append((KIND_RANK[kind], -e["score"], e["id"], n))
    owner = {}
    by_id = {e["id"]: e for e in entities}
    collisions = 0
    steal = cfg.get("alias_steal_ratio", 5.0)
    for k, cands in keymap.items():
        cands.sort()
        best = cands[0]
        # Et alias kan «stjele» et navn fra et mye mindre kjent hovednavn (f.eks. «Messi»):
        # ellers ville et kjent kallenavn gitt høyeste sjeldenhet.
        m_best = by_id[best[2]]["metrics"].get(dom_metric) or 0
        for c in cands[1:]:
            if c[2] != best[2] and c[0] < KIND_RANK["derived"] and m_best > 0 \
                    and (by_id[c[2]]["metrics"].get(dom_metric) or 0) >= steal * m_best:
                review.append({"key": k, "problem": "kjent alias vant over ukjent hovednavn",
                               "valgt": by_id[c[2]]["label"], "tapte": by_id[best[2]]["label"]})
                best = c
                m_best = by_id[c[2]]["metrics"].get(dom_metric) or 0
        others = [c for c in cands if c[2] != best[2]]
        if best[0] == KIND_RANK["derived"] and others:
            # Avledet alias (etternavn) beholdes bare hvis én person klart dominerer.
            s1 = by_id[best[2]]["metrics"].get(dom_metric) or 0
            s2 = by_id[others[0][2]]["metrics"].get(dom_metric) or 0
            if s2 > 0 and s1 / s2 < dominance and others[0][0] == KIND_RANK["derived"]:
                review.append({"key": k, "problem": "tvetydig etternavn forkastet",
                               "kandidater": [by_id[c[2]]["label"] for c in cands[:5]]})
                continue
            if others[0][0] < best[0]:
                continue
        if others and others[0][0] == best[0] and best[0] == KIND_RANK["label"]:
            collisions += 1
            if len(review) < 5000 and abs(best[1] - others[0][1]) < 0.02:
                review.append({"key": k, "problem": "flere med samme navn (mest kjente valgt)",
                               "valgt": by_id[best[2]]["label"], "valgt_id": best[2],
                               "andre": [c[2] for c in others[:5]]})
        owner[k] = best[2]

    # 4) Hvert objekt beholder bare navnene det faktisk «eier» (duplikater slås sammen)
    owned = {}
    for k, eid in owner.items():
        owned.setdefault(eid, set()).add(k)
    final = []
    for e in entities:
        keys = owned.get(e["id"])
        if not keys:
            continue
        names = [e["label"]] + e["aliases"] + e.get("derived", [])
        out_alias, used = [], set()
        for n in names[1:]:
            k = norm(n)
            if k in keys and k not in used and k != norm(e["label"]):
                used.add(k)
                out_alias.append(n)
        if norm(e["label"]) not in keys:
            # Hovednavnet tilhører et annet (mer kjent) objekt; bruk første eide alias som visningsnavn.
            if not out_alias:
                continue
            e["label"], out_alias = out_alias[0], out_alias[1:]
        e["aliases"] = out_alias
        final.append(e)
    log(f"Etter rensing og sammenslåing: {len(final)} unike svar, {len(owner)} godkjente skrivemåter, "
        f"{collisions} navnekollisjoner")

    # 5) Nivåer
    observed = load_json(p("overrides", "observed", qid + ".json"), None)
    # Svar med fast nivå (manuelle eller «kjent for noe annet») holdes utenfor rangeringen, så de ikke tar
    # plassene til de vanlige svarene: grensene regnes bare på de frie svarene.
    free = [e for e in final if e.get("pinned_tier") is None]
    pinned = [e for e in final if e.get("pinned_tier") is not None]
    rc = rcfg
    cuts = (rcfg or {}).get("cuts") or {}
    if pinned and cuts.get("mode") == "rank" and final:
        # Grensene er faste plasser beregnet for hele listen; skaler dem når mange svar har fast nivå
        k = len(free) / len(final)
        rc = dict(rcfg, cuts=dict(cuts, at=[max(1, round(a * k)) for a in cuts["at"]]))
    ordered = rarity.assign_tiers(free, rc, observed) if free else []
    for e in pinned:
        e["tier"] = int(e["pinned_tier"])
        e.setdefault("score", 0.0)
        e["rank"] = None
    ordered = sorted(ordered + pinned, key=lambda e: (-(e.get("score") or 0), e["label"]))
    dist = [sum(1 for e in ordered if e["tier"] == t) for t in range(6)]
    log(f"Fordeling på nivå 0–5 (Tare→Kjempeblekksprut): {dist}")

    # 6) Kontroller
    problems = validate(cfg, ordered, owner, log, offline)
    result = {
        "id": qid, "question": cfg["question"], "norsk": cfg.get("norsk", False),
        "built": datetime.datetime.now().isoformat(timespec="seconds"), "offline": offline,
        "source": src_cfg["type"], "attribution": cfg.get("attribution", ""),
        "as_of": raw.get("date") if isinstance(raw, dict) and "date" in raw else None,
        "count": len(ordered), "keys": len(owner), "tiers": dist, "problems": problems,
        "entries": [{"id": e["id"], "label": e["label"], "aliases": e["aliases"], "tier": e["tier"],
                     "rank": e["rank"], "score": e["score"], "metrics": e["metrics"], "source": e["source"]}
                    for e in ordered],
    }
    save_json(p("staging", qid + ".json"), result)
    save_json(p("review", qid + ".json"), review)
    log(f"Staging lagret ({len(ordered)} svar). {len(review)} oppføringer til manuell kontroll. "
        f"{'KONTROLLER FEILET: ' + '; '.join(problems) if problems else 'Alle kontroller bestått.'} "
        f"({time.time() - t0:.1f}s)")
    return result


def validate(cfg, entries, owner, log, offline=False):
    v = cfg.get("validate_offline" if offline and "validate_offline" in cfg else "validate", {})
    probs = []
    n = len(entries)
    if n < v.get("min_count", 1):
        probs.append(f"for få svar ({n} < {v['min_count']})")
    if "expected_count" in v and n != v["expected_count"]:
        msg = f"antall {n} avviker fra forventet {v['expected_count']} ({v.get('expected_note', '')})"
        (probs.append(msg) if v.get("expected_strict") else log("ADVARSEL: " + msg))
    for must in v.get("must_include", []):
        if norm(must) not in owner:
            probs.append(f"mangler kontrollsvar «{must}»")
    for bad in v.get("must_exclude", []):
        if norm(bad) in owner:
            probs.append(f"inneholder feil svar «{bad}»")
    return probs


def publish(qid, force=False, quiet=False):
    log = Logger(qid + "-publish", quiet)
    st = load_json(p("staging", qid + ".json"))
    if not st:
        raise SystemExit(f"Ingen staging for {qid}. Kjør build først.")
    cfg = load_json(p("config", "questions", qid + ".json"))
    if st["problems"] and not force:
        log(f"STOPPET: {qid} har feil i kontrollene: {st['problems']}")
        return False
    if st.get("offline") and not force:
        log(f"STOPPET: {qid} er bygd fra testdata (--offline). Bruk --force for å publisere likevel.")
        return False
    out = os.path.join(SITE, "data", qid + ".json")
    prev = load_json(out)
    max_shrink = cfg.get("validate", {}).get("max_shrink", 0.15)
    # «min_count_after_cleanup» i overstyringsfilen: bevisst opprydding får krympe ned til dette tallet
    allow_to = (load_json(p("overrides", qid + ".json"), {}) or {}).get("min_count_after_cleanup")
    if prev and not force and st["count"] < prev["n"] * (1 - max_shrink) and not (allow_to and st["count"] >= allow_to):
        log(f"STOPPET: {qid} krymper fra {prev['n']} til {st['count']} svar (> {max_shrink:.0%}). "
            f"Mulig feil i kilden. Bruk --force hvis endringen er riktig.")
        return False
    version = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    compact = {
        "id": qid, "q": st["question"], "norsk": st["norsk"], "v": version, "n": st["count"],
        "src": st["attribution"], "asOf": st["as_of"],
        "cat": cfg.get("category", "Annet"), "modes": cfg.get("modes", ["daily", "endless", "packs", "party"]),
        "diff": difficulty(st), "status": cfg.get("status", "godkjent"),
        "e": [[e["label"], e["tier"], *e["aliases"]] for e in st["entries"]],
    }
    # Ferdig normaliserte nøkler (én linje per svar, nøkler skilt med tabulator), så spillet slipper å normalisere
    # hundretusenvis av navn på mobilen. Første forekomst vinner (samme regel som i spillet).
    seen, lines = set(), []
    for e in st["entries"]:
        ks = []
        for n in [e["label"], *e["aliases"]]:
            k = norm(n)
            if k and k not in seen:
                seen.add(k)
                ks.append(k)
        lines.append("\t".join(ks))       # linje i = svar i
    compact["k"] = "\n".join(lines)
    # Med ferdige nøkler trenger spillet bare visningsnavn og nivå; alias ligger i nøklene.
    compact["e"] = [[e["label"], e["tier"]] for e in st["entries"]]
    # Uendret innhold: ikke skriv filen på nytt (da blir det heller ingen ny publisering av nettsiden)
    if prev and not force and all(prev.get(f) == compact.get(f) for f in ("q", "norsk", "n", "src", "cat", "modes", "diff", "status", "e", "k")):
        log(f"Uendret: {qid} ({st['count']} svar) – ingen ny versjon")
        return True
    if prev:
        arch = os.path.join(SITE, "data", "archive", qid)
        os.makedirs(arch, exist_ok=True)
        shutil.copy2(out, os.path.join(arch, f"{prev['v']}.json"))
        added = len({e[0] for e in compact["e"]} - {e[0] for e in prev["e"]})
        removed = len({e[0] for e in prev["e"]} - {e[0] for e in compact["e"]})
        log(f"Endringer mot forrige versjon {prev['v']}: +{added} / -{removed} visningsnavn")
    save_json(out, compact, compact=True)
    _update_index()
    log(f"PUBLISERT {qid} v{version}: {st['count']} svar -> {out}")
    return True


def difficulty(st):
    """Vanskelighetsgrad 1–3 ut fra hvor mange svar som finnes: få svar = vanskeligere å komme på noe."""
    n = st["count"]
    return 3 if n < 40 else 2 if n < 400 else 1


def rollback(qid, quiet=False):
    log = Logger(qid + "-rollback", quiet)
    arch = os.path.join(SITE, "data", "archive", qid)
    versions = sorted(glob.glob(os.path.join(arch, "*.json")))
    if not versions:
        log("Ingen tidligere versjon å gå tilbake til.")
        return False
    last = versions[-1]
    shutil.copy2(last, os.path.join(SITE, "data", qid + ".json"))
    os.remove(last)
    _update_index()
    log(f"Gikk tilbake til {os.path.basename(last)}")
    return True


def _day_number(today=None):
    """Dagnummer i dagens-dykk-kalenderen (dag 1 = 1. november 2026), samme som dayNumber() i spillet."""
    import datetime
    today = today or datetime.date.today()
    return max(1, (today - datetime.date(2026, 11, 1)).days + 1)


def _update_index():
    d = os.path.join(SITE, "data")
    idx = []
    # «from»: første dag spørsmålet kan dukke opp i dagens dykk. Bevares fra forrige indeks, slik at
    # kalenderen for tidligere dager aldri endres når nye datasett publiseres. Nye datasett starter i morgen.
    # Lagres også i state/first_day.json, som er fasit hvis indeksen blir skrevet av en eldre versjon.
    fd_path = os.path.join(ROOT, "state", "first_day.json")
    old_from = {}
    try:
        old_from.update(load_json(fd_path))
    except Exception:
        pass
    try:
        for e in load_json(os.path.join(d, "index.json")).get("datasets", []):
            if "from" in e:
                old_from.setdefault(e["id"], e["from"])
    except Exception:
        pass
    for f in sorted(glob.glob(os.path.join(d, "*.json"))):
        if os.path.basename(f) == "index.json":
            continue
        j = load_json(f)
        if j.get("status", "godkjent") != "godkjent":
            continue   # bare kvalitetssikrede spørsmål vises for spillere
        idx.append({"id": j["id"], "q": j["q"], "norsk": j.get("norsk", False), "n": j["n"], "v": j["v"],
                    "src": j.get("src", ""), "cat": j.get("cat", "Annet"), "modes": j.get("modes", []),
                    "diff": j.get("diff", 2), "file": "data/" + os.path.basename(f),
                    "from": old_from.get(j["id"], _day_number() + 1)})
    save_json(os.path.join(d, "index.json"), {"datasets": idx}, compact=False)
    os.makedirs(os.path.dirname(fd_path), exist_ok=True)
    old_from.update({e["id"]: e["from"] for e in idx})
    save_json(fd_path, old_from, compact=False)
