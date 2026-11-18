"""Skriver tabellen over publiserte datasett i DEVELOPMENT_PROGRESS.md ut fra site/data (faktiske tall)."""
import json, os, glob, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows, tot_a, tot_k = [], 0, 0
for f in sorted(glob.glob(os.path.join(ROOT, "site", "data", "*.json"))):
    if f.endswith("index.json"):
        continue
    j = json.load(open(f, encoding="utf-8"))
    keys = sum(len(l.split("\t")) for l in j["k"].split("\n")) if j.get("k") else 0
    tot_a += j["n"]; tot_k += keys
    rows.append(f"| {j['id']} | {j['q']} | {j.get('cat', '')} | {j['n']:,} | {keys:,} |".replace(",", " "))
table = ("| ID | Spørsmål | Kategori | Svar | Skrivemåter |\n|---|---|---|---|---|\n" + "\n".join(rows) +
         f"\n\n**Sum: {len(rows)} datasett, {tot_a:,} godkjente svar, {tot_k:,} godkjente skrivemåter.**".replace(",", " "))
p = os.path.join(ROOT, "DEVELOPMENT_PROGRESS.md")
md = open(p, encoding="utf-8").read()
md = re.sub(r"(## Faktisk importert og publisert[^\n]*\n)(.*?)(\n## )", lambda m: m.group(1) + table + "\n" + m.group(3), md, flags=re.S)
open(p, "w", encoding="utf-8").write(md)
print(len(rows), tot_a, tot_k)
