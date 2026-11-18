#!/bin/bash
# Nattlig import for Dypdykk.
# - Kjører importkøen (fortsetter der den slapp, hopper over det som er ferdig i dag)
# - Prøver feilede jobber på nytt
# - Lager administrasjonsoversikt
# - Publiserer til Netlify hvis NETLIFY_AUTH_TOKEN og NETLIFY_SITE_ID er satt
# Bruk: ./automation/nattlig-import.sh   (fra prosjektmappen dypdykk-data)
set -u
cd "$(dirname "$0")/.."
LOG="logs/natt-$(date +%Y%m%d-%H%M%S).log"
mkdir -p logs
LOCK="state/natt.lock"
mkdir -p state
if [ -e "$LOCK" ] && kill -0 "$(cat "$LOCK")" 2>/dev/null; then echo "Kjører allerede (pid $(cat "$LOCK"))"; exit 0; fi
echo $$ > "$LOCK"; trap 'rm -f "$LOCK"' EXIT
{
  echo "=== Start $(date)"
  python3 -m dypdykk_data queue --retry
  python3 -m dypdykk_data report
  if [ -n "${NETLIFY_AUTH_TOKEN:-}" ] && [ -n "${NETLIFY_SITE_ID:-}" ]; then
    npx --yes netlify-cli deploy --prod --dir site --site "$NETLIFY_SITE_ID" --auth "$NETLIFY_AUTH_TOKEN" --message "Nattlig dataimport $(date +%F)"
  else
    echo "Hopper over Netlify-publisering (NETLIFY_AUTH_TOKEN/NETLIFY_SITE_ID ikke satt). Last opp mappen site/ manuelt."
  fi
  echo "=== Ferdig $(date)"
} >> "$LOG" 2>&1
