"""Administrasjonsoversikt: admin.html med status for alle spørsmål og datasett.

Viser for hvert spørsmål: ID, spørsmålstekst, kategori, kilde, antall svar og skrivemåter,
vanskelighetsgrad, status for kvalitetssikring, fordeling på nivåer, saker til manuell
kontroll, siste kjøring og eventuelle feil. Filen lagres i prosjektroten (ikke på nettsiden).
"""
import datetime
import html
import json
import os

from . import pipeline, queue

TIER_NAMES = ["Tare", "Reke", "Makrell", "Blekksprut", "Breiflabb", "Kjempeblekksprut"]
COLORS = ["#9fd18b", "#ffab7a", "#6cc8ff", "#c79bff", "#ffd36b", "#5ef2d6"]


def _bar(tiers):
    tot = sum(tiers) or 1
    return "".join(f'<i title="{TIER_NAMES[i]}: {n}" style="width:{100 * n / tot:.2f}%;background:{COLORS[i]}"></i>'
                   for i, n in enumerate(tiers))


def write():
    st = queue.load_state()["jobs"]
    rows, total_n, total_k, published = [], 0, 0, 0
    for qid in pipeline.list_configs():
        cfg = pipeline.load_json(pipeline.p("config", "questions", qid + ".json"))
        stg = pipeline.load_json(pipeline.p("staging", qid + ".json")) or {}
        pub = pipeline.load_json(os.path.join(pipeline.SITE, "data", qid + ".json"))
        rev = pipeline.load_json(pipeline.p("review", qid + ".json"), [])
        job = st.get(qid, {})
        status = ("publisert" if pub and cfg.get("status", "godkjent") == "godkjent" else
                  job.get("status") or ("bygget" if stg else "ikke kjørt"))
        if pub:
            published += 1
            total_n += pub["n"]
            total_k += stg.get("keys", 0)
        prob = "; ".join(stg.get("problems", []))
        err = job.get("error", "")[:160]
        cnt = pub["n"] if pub else stg.get("count", "–")
        rows.append(f"""<tr class="s-{status.split()[0]}">
<td><code>{qid}</code></td><td>{html.escape(cfg['question'])}{' 🇳🇴' if cfg.get('norsk') else ''}</td>
<td>{html.escape(cfg.get('category', ''))}</td><td>{cfg['source']['type']}</td>
<td class="n">{cnt}</td><td class="n">{stg.get('keys', '–')}</td>
<td class="n">{pub.get('diff', '–') if pub else '–'}</td>
<td><b>{html.escape(status)}</b>{'<br><small>' + html.escape(prob) + '</small>' if prob else ''}{'<br><small>' + html.escape(err) + '</small>' if err else ''}</td>
<td><div class="bar">{_bar(stg.get('tiers', [0] * 6))}</div></td>
<td class="n">{len(rev)}</td><td><small>{html.escape(job.get('finished', stg.get('built', '')) or '')}</small></td>
<td><small>{', '.join(cfg.get('modes', []))}</small></td></tr>""")
    doc = f"""<!DOCTYPE html><html lang="no"><head><meta charset="utf-8"><title>Dypdykk – administrasjon</title>
<style>body{{font:14px Inter,system-ui,sans-serif;background:#06121f;color:#e6f2f7;margin:24px}}
h1{{margin:0 0 4px}}.sum{{color:#8db4c6;margin-bottom:16px}}table{{border-collapse:collapse;width:100%}}
th,td{{padding:7px 8px;border-bottom:1px solid #1d3346;text-align:left;vertical-align:top}}th{{position:sticky;top:0;background:#0b2033}}
.n{{text-align:right;font-variant-numeric:tabular-nums}}.bar{{display:flex;width:160px;height:10px;border-radius:5px;overflow:hidden;background:#13283a}}
.bar i{{display:block;height:100%}}code{{color:#5ef2d6}}small{{color:#8db4c6}}tr.s-publisert b{{color:#9fd18b}}
tr.s-stoppet b,tr.s-feilet b{{color:#ff7a6b}}tr.s-kjører b{{color:#ffd36b}}</style></head><body>
<h1>Dypdykk – datasett</h1><div class="sum">{published} publiserte datasett · {total_n} svar · {total_k} godkjente skrivemåter ·
generert {datetime.datetime.now():%Y-%m-%d %H:%M}. Bare spørsmål med status «publisert» vises for spillere.</div>
<table><tr><th>ID</th><th>Spørsmål</th><th>Kategori</th><th>Kilde</th><th>Svar</th><th>Skrivemåter</th><th>Vansk.</th>
<th>Status</th><th>Nivåer</th><th>Til kontroll</th><th>Sist kjørt</th><th>Moduser</th></tr>{''.join(rows)}</table>
<p class="sum">Kommandoer: <code>python3 -m dypdykk_data queue</code> · <code>status</code> · <code>run &lt;id&gt;</code> ·
<code>rollback &lt;id&gt;</code> · manuelle rettelser i <code>overrides/&lt;id&gt;.json</code> · tvilstilfeller i <code>review/&lt;id&gt;.json</code></p>
</body></html>"""
    out = os.path.join(pipeline.ROOT, "admin.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(doc)
    return out
