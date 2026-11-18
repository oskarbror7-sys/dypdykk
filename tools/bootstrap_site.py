"""Henter den publiserte nettsiden inn i site/ før en nattlig kjøring.

1. Finnes grenen «nettside» i repoet (lagt dit av forrige kjøring), brukes den.
2. Ellers (første kjøring) lastes siden ned fra https://dypdykk.netlify.app.

Slik trenger repoet ikke inneholde de store datafilene i hovedgrenen.
"""
import json, os, subprocess, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
LIVE = os.environ.get("DYPDYKK_LIVE", "https://dypdykk.netlify.app")
ASSETS = ["index.html", "_headers", "favicon.svg", "apple-touch-icon.png", "icon-192.png", "icon-512.png",
          "manifest.webmanifest", "og-image.jpg", "robots.txt"]


def git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True)


def from_branch():
    if git("fetch", "--depth", "1", "origin", "nettside").returncode != 0:
        return False
    os.makedirs(SITE, exist_ok=True)
    r = git("--work-tree=" + SITE, "checkout", "FETCH_HEAD", "--", ".")
    git("reset", "-q")
    return r.returncode == 0 and os.path.exists(os.path.join(SITE, "index.html"))


def get(path):
    req = urllib.request.Request(f"{LIVE}/{path}", headers={"User-Agent": "DypdykkDataBot/1.0 (https://dypdykk.netlify.app)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def save(path, data):
    full = os.path.join(SITE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "wb") as f:
        f.write(data)


def from_live():
    for a in ASSETS:
        try:
            save(a, get(a))
        except Exception as e:
            print(f"  mangler {a}: {e}")
    try:
        idx = json.loads(get("data/index.json"))
    except Exception as e:
        print(f"  ingen data/index.json på {LIVE}: {e}")
        return
    save("data/index.json", json.dumps(idx, ensure_ascii=False, indent=1).encode())
    for d in idx.get("datasets", []):
        try:
            save(d["file"], get(d["file"]))
        except Exception as e:
            print(f"  kunne ikke hente {d['file']}: {e}")
    print(f"  hentet {len(idx.get('datasets', []))} datasett fra {LIVE}")


if __name__ == "__main__":
    if from_branch():
        print("Nettsiden hentet fra grenen «nettside»")
    else:
        print(f"Første kjøring: henter nettsiden fra {LIVE}")
        from_live()
    # Spillfilene i repoet (mappen nettside/) er alltid nyest og legges over
    src = os.path.join(ROOT, "nettside")
    if os.path.isdir(src):
        for dirpath, _, files in os.walk(src):
            for name in files:
                full = os.path.join(dirpath, name)
                with open(full, "rb") as f:
                    save(os.path.relpath(full, src), f.read())
        print("Spillfilene fra nettside/ er lagt inn")
    if not os.path.exists(os.path.join(SITE, "index.html")):
        sys.exit("Fant ingen nettside å bygge videre på")
