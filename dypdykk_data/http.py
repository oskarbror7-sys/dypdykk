"""HTTP med høflig oppførsel overfor åpne API-er.

- Egen User-Agent med kontaktinfo (påkrevd av Wikimedia).
- Minimum pause mellom kall til samme vert (hastighetsbegrensning).
- Nye forsøk med eksponentiell ventetid ved 429/5xx, og respekt for Retry-After.
- Disk-cache: samme forespørsel hentes bare én gang (kan slås av med refresh=True).
"""
import gzip
import http.client
import hashlib
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

USER_AGENT = "DypdykkDataBot/1.0 (https://dypdykk.netlify.app; norsk quizspill) python-urllib"
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cache")
MIN_INTERVAL = {"query.wikidata.org": 1.5, "www.wikidata.org": 0.5, "wikimedia.org": 0.2}
_last_call = {}


class FetchError(RuntimeError):
    pass


def _cache_path(key: str) -> str:
    h = hashlib.sha256(key.encode()).hexdigest()[:32]
    return os.path.join(CACHE_DIR, h[:2], h + ".json.gz")


def fetch_json(url, params=None, data=None, refresh=False, retries=6, timeout=90, log=None):
    if params:
        url = url + ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    key = url + ("\n" + data if data else "")
    path = _cache_path(key)
    # Svar eldre enn DYPDYKK_CACHE_DAGER (standard 7) hentes på nytt, slik at nattlige kjøringer får ferske data
    max_age = float(os.environ.get("DYPDYKK_CACHE_DAGER", "7")) * 86400
    if not refresh and os.path.exists(path) and time.time() - os.path.getmtime(path) < max_age:
        with gzip.open(path, "rt", encoding="utf-8") as f:
            return json.load(f)

    host = urllib.parse.urlparse(url).hostname or ""
    wait = MIN_INTERVAL.get(host, 0.3)
    delay = 2.0
    for attempt in range(retries):
        since = time.time() - _last_call.get(host, 0)
        if since < wait:
            time.sleep(wait - since)
        _last_call[host] = time.time()
        body = data.encode() if data else None
        req = urllib.request.Request(url, data=body, headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/sparql-results+json, application/json",
            **({"Content-Type": "application/x-www-form-urlencoded"} if body else {}),
        })
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw = r.read().decode("utf-8", errors="replace")
            try:
                payload = json.loads(raw)
            except ValueError:
                # Wikidata avbryter store svar midt i strømmen (tidsavbrudd) -> ugyldig JSON.
                # Ikke lagre i cache; la kalleren dele opp spørringen.
                raise FetchError(f"Ufullstendig svar ({len(raw)} tegn) fra {host}")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with gzip.open(path, "wt", encoding="utf-8") as f:
                json.dump(payload, f)
            return payload
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504):
                ra = e.headers.get("Retry-After")
                sleep = float(ra) if ra and ra.isdigit() else delay
                if log:
                    log(f"HTTP {e.code} fra {host}, venter {sleep:.0f}s (forsøk {attempt + 1}/{retries})")
                time.sleep(sleep)
                delay = min(delay * 2, 120)
                continue
            raise FetchError(f"HTTP {e.code} fra {url[:120]}") from e
        except (http.client.IncompleteRead, http.client.RemoteDisconnected) as e:
            # Tilkoblingen ble brutt midt i et stort svar: la kalleren dele opp spørringen.
            raise FetchError(f"Avbrutt svar fra {host}: {e!r}") from e
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            if log:
                log(f"Nettverksfeil mot {host}: {e} (forsøk {attempt + 1}/{retries})")
            time.sleep(delay)
            delay = min(delay * 2, 120)
    raise FetchError(f"Ga opp etter {retries} forsøk: {url[:120]}")
