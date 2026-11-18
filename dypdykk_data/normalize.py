"""Normalisering av svar.

MÅ være identisk med funksjonen norm() i spillet (index.html), ellers kan et
svar som er godkjent her bli avvist i spillet. Testen tests/test_normalize.py
sjekker dette mot JavaScript-koden.

    s.toLowerCase()
     .replace(/\\+\\+/g,"pp").replace(/#/g,"sharp")      // C++ og C# skal ikke bli «c»
     .replace(/æ/g,"ae").replace(/ø/g,"o").replace(/å/g,"a")
     .normalize("NFD").replace(/[\\u0300-\\u036f]/g,"")
     .replace(/[^a-z0-9]/g,"")
"""
import re
import unicodedata

_COMBINING = re.compile("[̀-ͯ]")
_NON_ALNUM = re.compile("[^a-z0-9]")


def norm(s: str) -> str:
    s = s.lower().replace("++", "pp").replace("#", "sharp").replace("æ", "ae").replace("ø", "o").replace("å", "a")
    s = unicodedata.normalize("NFD", s)
    s = _COMBINING.sub("", s)
    return _NON_ALNUM.sub("", s)


_PAREN = re.compile(r"\s*\([^)]*\)\s*$")
_WS = re.compile(r"\s+")


def clean_label(s: str):
    """Rydder en etikett fra en kilde. Returnerer None hvis den skal forkastes."""
    if not s:
        return None
    s = _WS.sub(" ", s).strip()
    s = _PAREN.sub("", s).strip()          # «Arne Larsen (fotballspiller)» -> «Arne Larsen»
    if not s or len(s) > 80:
        return None
    if re.fullmatch(r"Q\d+", s):            # Wikidata-ID uten navn
        return None
    k = norm(s)
    if len(k) < 2 or (k.isdigit() and len(k) < 4):   # titler som «1984» og «2001» er gyldige
        return None
    return s
