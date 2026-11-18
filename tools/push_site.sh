#!/usr/bin/env bash
# Legger site/ (uten arkivet) som eneste commit i grenen «nettside». Historikken holdes liten.
set -e
cd "$(dirname "$0")/../site"
rm -rf .git
git init -q -b nettside
git config user.name "dypdykk-bot"; git config user.email "bot@dypdykk.invalid"
git add -A -- . ':!data/archive'
git commit -qm "Nettside $(date -u +%F\ %H:%M)"
git push -q -f "https://x-access-token:${GITHUB_TOKEN}@github.com/${GITHUB_REPOSITORY}.git" nettside
rm -rf .git
echo "Publisert til grenen nettside"
