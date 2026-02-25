# Command Recipes

Use these command sequences to reproduce, isolate, and verify Electron Bun test issues.

## Installation Baseline

From repo root:
```bash
cd /Users/tinnguyen/vesper
bun install
```

## Baseline Typecheck

From repo root:
```bash
bun run typecheck:all
```

## Targeted Electron Test Run

From repo root:
```bash
cd apps/electron
bun test src/main/__tests__/personas.test.ts src/main/__tests__/sessions.unexpected-exit.test.ts
```

## Single Failing File Run

```bash
cd apps/electron
bun test src/main/__tests__/sessions.unexpected-exit.test.ts
```

## Full Electron Workspace Typecheck

```bash
cd apps/electron
bun run typecheck
```

## Shared Package Tests Related to Type Safety

```bash
cd packages/shared
bun test src/agent/__tests__/artifact-tools.test.ts src/agent/__tests__/code-executor.test.ts
```

## Mock Surface Audit

```bash
cd /Users/tinnguyen/vesper
./skills/electron-bun-test-reviewer/scripts/audit-main-test-mocks.sh
```

Fail on all warnings (strict hygiene pass):
```bash
cd /Users/tinnguyen/vesper
./skills/electron-bun-test-reviewer/scripts/audit-main-test-mocks.sh --strict
```

## Post-Fix Verification Sequence

```bash
cd /Users/tinnguyen/vesper
./skills/electron-bun-test-reviewer/scripts/run-electron-bun-checks.sh
```

## Triage Helpers

Find mocks of a shared module:
```bash
rg -n "mock\\.module\\('../workspace-path-resolver'|mock\\.module\\('electron'" apps/electron/src/main/__tests__
```

Find missing export references quickly:
```bash
rg -n "migrateLegacyWorkspaceConfigFields|ipcMain|nativeImage" apps/electron/src/main
```

Inspect package scripts that define test/typecheck behavior:
```bash
cat package.json
cat apps/electron/package.json
cat packages/shared/package.json
```

## CI Parity Snapshot

Check team CLI workflow command usage:
```bash
rg -n "bun install --frozen-lockfile|bun run test:team-cli" .github/workflows/team-cli-golden.yml
```
