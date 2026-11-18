# Dypdykk – datasett

Henter, renser og publiserer svarlister til Dypdykk fra åpne kilder (Wikidata, SSB),
med norske navn først, alias, beregnet sjeldenhet og sikker publisering.
Bare Python 3.9+ standardbibliotek kreves.

## Kom i gang

```bash
cd dypdykk-data
python3 -m dypdykk_data list                       # status for alle spørsmål
python3 -m dypdykk_data run kommuner               # hent + kontroller + publiser
python3 -m dypdykk_data run all                    # alle spørsmål
python3 -m unittest discover -s tests -v           # tester
```

Etter `run` ligger datasettet i `site/data/<id>.json`. Last opp mappen `site/` til Netlify.

## Legge til et nytt spørsmål

Lag `config/questions/<id>.json`. Eksempel – «Nevn en norsk innsjø» fra Wikidata:

```json
{
  "question": "Nevn en norsk innsjø",
  "norsk": true,
  "attribution": "Kilde: Wikidata (CC0)",
  "source": {
    "type": "wikidata",
    "where": "?item wdt:P31/wdt:P279* wd:Q23397 ; wdt:P17 wd:Q20 .",
    "bands": [[0,2],[3,1000]],
    "label_langs": ["nb","nn","mul","en"],
    "alias_langs": ["nb","nn","se","mul"]
  },
  "rarity": {"weights": {"sitelinks": 1.0},
             "cuts": {"mode": "percent", "at": [0.03, 0.12, 0.30, 0.55, 0.85]}},
  "validate": {"min_count": 200, "must_include": ["Mjøsa", "Femunden"], "must_exclude": ["Oslo"]}
}
```

Så: `python3 -m dypdykk_data run <id>`. Ingen ny kode trengs.

Kildetyper: `wikidata` (SPARQL), `ssb_klass` (SSBs klassifikasjoner, f.eks. kommuner=131, fylker=104)
og `static` (håndlaget liste i spillets format).

## Slik fungerer det

1. **Innhenting** – store kategorier deles i bånd etter antall sitelinks. Blir et svar for stort,
   deles det automatisk videre etter Q-nummer. Alle svar caches i `cache/`. Pauser mellom kall,
   nye forsøk ved 429/5xx og egen User-Agent.
2. **Felles format** – hvert svar får en fast ID (Wikidata-ID / kommunenummer).
   Norsk navn (nb → nn → mul → en) vises; andre navn blir alias.
3. **Rensing** – tomme navn, rene ID-er, tall og parentes-presiseringer fjernes;
   samme ID to ganger slås sammen; alias som matcher `alias_exclude_regex` dropes.
4. **Kollisjoner** – hovednavn slår alias, alias slår avledede navn (etternavn).
   Et etternavn godtas bare når én person dominerer (`dominance`, standard 1,5×).
   Navnebrødre: den mest kjente blir eier av navnet (laveste/sikreste sjeldenhet).
   Tvilstilfeller skrives til `review/<id>.json`.
5. **Sjeldenhet** – se `dypdykk_data/rarity.py` for metoden. Persentiler av indikatorer
   (sitelinks, folketall …), vektet, sortert og delt i seks nivåer med justerbare grenser.
   Observerte svar fra spillere legges i `overrides/observed/<id>.json` ({"Q42": 17, …})
   og blandes inn først når det finnes nok av dem.
6. **Kontroller** – minimum antall, forventet antall, kontrollsvar som må finnes / ikke må finnes.
7. **Publisering** – stoppes hvis en kontroll feiler, hvis datasettet krymper mer enn `max_shrink`,
   eller hvis det er bygd fra testdata. Forrige versjon arkiveres i `site/data/archive/<id>/`.
   `python3 -m dypdykk_data rollback <id>` går tilbake.

## Manuelle rettelser – `overrides/<id>.json`

Røres aldri av importen og brukes på nytt hver gang:

```json
{
  "remove": ["Q123"],
  "add": [{"id": "manuell:1", "label": "Ola Nordmann", "aliases": ["Ola"], "tier": 4}],
  "aliases": {"Q11571": ["CR7"]},
  "label": {"Q529207": "Ronaldo (R9)"},
  "tier": {"Q615": 0},
  "reject_alias": ["Christiania"]
}
```

## Filer

| Mappe | Innhold |
|---|---|
| `config/questions/` | spørsmålsdefinisjoner |
| `dypdykk_data/` | koden (kilder, rensing, sjeldenhet, publisering) |
| `overrides/` | manuelle rettelser og observerte frekvenser |
| `staging/` | fullt resultat med ID, poeng, måltall og kilde |
| `review/` | oppføringer til manuell kontroll |
| `logs/` | logg for hver kjøring |
| `site/` | nettsiden som lastes opp; `site/data/` er datasettene |
| `tests/` | tester og testdata (merket TESTDATA) |

## Kildevilkår

- Wikidata: CC0 – fri bruk. Kilde oppgis likevel i spillet.
- SSB KLASS: NLOD 2.0 – krever kildehenvisning («Kilde: Statistisk sentralbyrå»). Vises i spillet.

## Kjøre automatisk (gjennom natten)

Claude-miljøet stopper prosesser kort tid etter at en arbeidsøkt er slutt. Langvarige importer
kjøres derfor på egen maskin eller på GitHub:

**Mac (anbefalt for å komme i gang):**
```bash
cd ~/Desktop/dypdykk-data
./automation/nattlig-import.sh                 # én kjøring nå (fortsetter der den slapp)
# Hver natt kl. 03:17:
sed "s#STI#$HOME/Desktop#" automation/no.dypdykk.import.plist > ~/Library/LaunchAgents/no.dypdykk.import.plist
launchctl load ~/Library/LaunchAgents/no.dypdykk.import.plist
```
Mac-en må være på (ikke i dvale) når jobben skal kjøre.

**GitHub Actions:** legg prosjektet i et GitHub-repo. `.github/workflows/nattlig-import.yml` kjører
importen hver natt, lagrer datasettene i repoet og publiserer til Netlify når secretene
`NETLIFY_AUTH_TOKEN` og `NETLIFY_SITE_ID` er satt.

Jobbene lagrer fremdrift i `state/jobs.json`, tåler avbrudd (cache + kø), prøver feilede jobber på nytt
med kontrollert ventetid, og publiserer aldri datasett som feiler kontrollene.
