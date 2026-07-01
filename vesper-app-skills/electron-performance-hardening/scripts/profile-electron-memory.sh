#!/usr/bin/env bash
set -euo pipefail

# Quick RSS sampler for Electron/Node startup diagnosis.
# Usage:
#   ./scripts/profile-electron-memory.sh "Electron"
#   SAMPLES=40 INTERVAL=1 ./scripts/profile-electron-memory.sh "vesper"

MATCH="${1:-Electron}"
SAMPLES="${SAMPLES:-30}"
INTERVAL="${INTERVAL:-2}"

printf "match=%s samples=%s interval=%ss\n" "$MATCH" "$SAMPLES" "$INTERVAL"
printf "%-20s %-8s %-10s %-10s %s\n" "timestamp" "pid" "rss_mb" "vsz_mb" "command"

for ((i=1; i<=SAMPLES; i++)); do
  ts="$(date '+%Y-%m-%d %H:%M:%S')"
  pids="$(pgrep -f "$MATCH" || true)"

  if [[ -z "$pids" ]]; then
    printf "%-20s %-8s %-10s %-10s %s\n" "$ts" "-" "-" "-" "no process match"
    sleep "$INTERVAL"
    continue
  fi

  while IFS= read -r pid; do
    [[ -z "$pid" ]] && continue
    rss_kb="$(ps -p "$pid" -o rss= | tr -d ' ' || true)"
    vsz_kb="$(ps -p "$pid" -o vsz= | tr -d ' ' || true)"
    cmd="$(ps -p "$pid" -o command= | sed -E 's/[[:space:]]+/ /g' | cut -c1-70 || true)"

    if [[ -z "$rss_kb" || -z "$vsz_kb" ]]; then
      continue
    fi

    rss_mb=$((rss_kb / 1024))
    vsz_mb=$((vsz_kb / 1024))
    printf "%-20s %-8s %-10s %-10s %s\n" "$ts" "$pid" "$rss_mb" "$vsz_mb" "$cmd"
  done <<< "$pids"

  sleep "$INTERVAL"
done
