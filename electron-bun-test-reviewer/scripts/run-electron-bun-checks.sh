#!/usr/bin/env bash
set -euo pipefail

# Run a stable verification sequence for Electron Bun test/typecheck work.
# Must be run from repository root.

if [[ ! -f "package.json" || ! -d "apps/electron" ]]; then
  echo "error: run from repository root (expected package.json + apps/electron/)" >&2
  exit 2
fi

echo "==> Root typecheck"
bun run typecheck:all

echo
echo "==> Targeted Electron main tests"
(
  cd apps/electron
  bun test src/main/__tests__/personas.test.ts src/main/__tests__/sessions.unexpected-exit.test.ts
)

echo
echo "==> Targeted shared tests for related strict typing surfaces"
(
  cd packages/shared
  bun test src/agent/__tests__/artifact-tools.test.ts src/agent/__tests__/code-executor.test.ts
)

echo
echo "All Electron Bun checks passed."
