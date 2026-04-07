#!/usr/bin/env bash
set -euo pipefail

SRC="${1:-/Users/tinnguyen/meta-agent}"
if [ ! -d "$SRC" ]; then
  echo "Source repo not found: $SRC" >&2
  exit 1
fi

cd "$SRC"
for f in meta_agent/*.py configs/*.py benchmarks/tau3/*.py; do
  echo "===== $f ====="
  nl -ba "$f" | sed -n '1,260p'
  echo
 done
