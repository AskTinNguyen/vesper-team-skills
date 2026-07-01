# Vesper CDP Reference

Use this reference when running CDP against the Vesper Electron app.

## Repo Facts

- Run commands from the repo root.
- The normal dev entrypoint is `bun run electron:dev`.
- Vesper dev instances are isolated per worktree through `scripts/detect-instance.sh`.
- `VESPER_VITE_PORT` is dynamic and usually starts at `5174`, not `5173`.
- Electron window titles usually include `Vesper` or `Vesper Dev (<instance-id>)`.
- Existing repo-native CDP helpers live under `scripts/e2e/`.

## Preferred Tooling Order

1. Existing repo tests under `apps/electron/src/__tests__/e2e/`
2. `scripts/e2e/cdp-utils.cjs` and `scripts/e2e/run-all.cjs`
3. Skill-local probes in `scripts/cdp-connect.js` and `scripts/cdp-test.js`
4. Fully custom WebSocket scripts only when the first three are insufficient

## Reliable Vesper Launch Patterns

### If `9222` Is Already Live

Use the running app and continue:

```bash
curl -s http://127.0.0.1:9222/json
```

Expected result: JSON with at least one non-DevTools `page` target.

### If You Need a Manual CDP Launch

In one shell, start the watcher stack:

```bash
source scripts/detect-instance.sh
bun run electron:build:resources
bun run electron:build:code-worker
bun x concurrently -k "bun run electron:dev:vite" "bun run electron:dev:main" "bun run electron:dev:preload"
```

In a second shell, launch Electron with CDP:

```bash
source scripts/detect-instance.sh
VITE_DEV_SERVER_URL="http://localhost:${VESPER_VITE_PORT}" ./node_modules/.bin/electron --remote-debugging-port=9222 apps/electron
```

Expected result: `curl -s http://127.0.0.1:9222/json` returns a `page` target for Vesper.

## Safer Targeting Rules

- Prefer a `page` target whose title contains `Vesper`.
- Ignore `DevTools` targets.
- Do not assume the renderer URL is fixed; read it from `/json`.

## Cheap Smoke Checks

These are fast and reliable enough to use before deeper automation:

```bash
curl -s http://127.0.0.1:9222/json
node scripts/cdp-connect.js --check-api
node scripts/cdp-test.js --test-file scripts/sample-test.json
```

Expected result:

- `/json` returns targets
- `--check-api` reports `electronAPI: Available`
- the sample test writes screenshots and reports pass/fail output without hanging

## Vesper-Specific Failure Modes

### CDP Port Missing While Vesper Is Running

Likely cause: Electron was launched without `--remote-debugging-port=9222`.

Fix: use the manual CDP launch pattern above instead of assuming `bun run electron:dev` exposed `9222`.

### App Opens to Onboarding or an Empty Workspace

Likely cause: dev-instance isolation created a clean profile under `~/.vesper-dev/<instance-id>/`.

Fix: create or open a workspace inside that dev instance before expecting existing production state.

### Wrong Vite Port

Likely cause: another instance claimed `5174`.

Fix: source `scripts/detect-instance.sh` and use `http://localhost:${VESPER_VITE_PORT}`.

### Wrong Process Killed

Avoid blanket `pkill -f electron`. If you need to stop the current instance, source `scripts/detect-instance.sh` first and target the matching `VESPER_CONFIG_DIR`.

### Long IPC Call Hangs

Reduce the scope. First prove:

1. correct target
2. `window.electronAPI`
3. route change
4. screenshot

Only after that should you try long session or message-path calls.
