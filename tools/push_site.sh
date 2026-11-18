#!/usr/bin/env bash
# Legger site/ (uten arkivet) som eneste commit i grenen «nettside». Historikken holdes liten.
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# Nyeste spillfiler fra main (i tilfelle de er endret mens importen kjørte)
if git -C "$ROOT" fetch -q --depth 1 origin main 2>/dev/null; then
  git -C "$ROOT" --work-tree="$ROOT/site" checkout FETCH_HEAD -- nettside 2>/dev/null && cp -r "$ROOT/site/nettside/." "$ROOT/site/" && rm -rf "$ROOT/site/nettside"
  git -C "$ROOT" reset -q
fi
cd "$ROOT/site"
rm -rf .git
git init -q -b nettside
git config user.name "dypdykk-bot"; git config user.email "bot@dypdykk.invalid"
git add -A -- . ':!data/archive'
git commit -qm "Nettside $(date -u +%F\ %H:%M)"
# Ingen endring siden forrige publisering? Da hopper vi over (sparer byggeminutter hos Netlify)
REMOTE="https://x-access-token:${GITHUB_TOKEN}@github.com/${GITHUB_REPOSITORY}.git"
if git fetch -q --depth 1 "$REMOTE" nettside 2>/dev/null && [ "$(git rev-parse HEAD^{tree})" = "$(git rev-parse FETCH_HEAD^{tree})" ]; then
  echo "Ingen endringer – nettsiden er allerede oppdatert"; rm -rf .git; exit 0
fi
git push -q -f "$REMOTE" nettside
rm -rf .git
echo "Publisert til grenen nettside"
