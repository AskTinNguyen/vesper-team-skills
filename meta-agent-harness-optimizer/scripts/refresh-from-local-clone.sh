#!/usr/bin/env bash
set -euo pipefail

SRC="${1:-/Users/tinnguyen/meta-agent}"
OUT_DIR="$(cd "$(dirname "$0")/.." && pwd)/references/source-snapshots"
mkdir -p "$OUT_DIR"

if [ ! -d "$SRC" ]; then
  echo "Source repo not found: $SRC" >&2
  exit 1
fi

cp "$SRC/README.md" "$OUT_DIR/README.md"
cp "$SRC/SKILL.md" "$OUT_DIR/source-SKILL.md"
cp "$SRC/WRITEUP.md" "$OUT_DIR/WRITEUP.md"
cp "$SRC/meta_agent/outer_loop.py" "$OUT_DIR/outer_loop.py"
cp "$SRC/meta_agent/eval_runner.py" "$OUT_DIR/eval_runner.py"
cp "$SRC/meta_agent/task_runner.py" "$OUT_DIR/task_runner.py"
cp "$SRC/meta_agent/cli.py" "$OUT_DIR/cli.py"
cp "$SRC/meta_agent/benchmark.py" "$OUT_DIR/benchmark.py"
cp "$SRC/benchmarks/tau3/sdk_adapter.py" "$OUT_DIR/sdk_adapter.py"
cp "$SRC/configs/vanilla.py" "$OUT_DIR/vanilla.py"
cp "$SRC/configs/bootstrap.py" "$OUT_DIR/bootstrap.py"
cp "$SRC/configs/hooks.py" "$OUT_DIR/hooks.py"

echo "Refreshed source snapshots from $SRC into $OUT_DIR"
