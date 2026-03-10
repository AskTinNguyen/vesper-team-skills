# Vesper Direct CDP Workflow

<required_reading>
Read `../references/vesper-cdp-reference.md` before following this workflow.
</required_reading>

## Goal

Connect to the live Vesper Electron renderer through CDP, prove the preload bridge is present, and capture concrete evidence quickly.

## Step 1: Check Whether CDP Is Already Available

```bash
curl -s http://127.0.0.1:9222/json
```

Expected result: JSON output. If this fails, continue to Step 2.

## Step 2: Launch Vesper in a CDP-Friendly Way

If you only need existing repo tests, prefer those first:

```bash
bun run test:e2e
```

If you need a live Electron window with raw CDP access, use the split launch.

Shell A:

```bash
source scripts/detect-instance.sh
bun run electron:build:resources
bun run electron:build:code-worker
bun x concurrently -k "bun run electron:dev:vite" "bun run electron:dev:main" "bun run electron:dev:preload"
```

Shell B:

```bash
source scripts/detect-instance.sh
VITE_DEV_SERVER_URL="http://localhost:${VESPER_VITE_PORT}" ./node_modules/.bin/electron --remote-debugging-port=9222 apps/electron
```

Expected result: `curl -s http://127.0.0.1:9222/json` now returns a Vesper `page` target.

## Step 3: Run the Fastest Safe Smoke Probe

From the skill directory:

```bash
./scripts/validate-setup.sh
node ./scripts/cdp-connect.js --check-api
```

Expected result:

- setup validator finds a Vesper page target
- `--check-api` reports `electronAPI: Available`

## Step 4: Capture Evidence

Run the bundled smoke suite:

```bash
node ./scripts/cdp-test.js --test-file ./scripts/sample-test.json
```

Expected result:

- the suite reports whether `window.electronAPI` exists
- it captures at least one screenshot
- it shows a concrete interaction result or a documented optional skip

## Step 5: Escalate Carefully

Only after the smoke probe succeeds should you attempt custom evaluation:

```bash
node ./scripts/cdp-connect.js --eval "typeof window.electronAPI"
node ./scripts/cdp-connect.js --eval "window.location.hash"
```

If an async call is slow or hangs, stop and report the last successful cheap check rather than waiting indefinitely on a deep session path.

## Done When

- `/json` is reachable
- the correct Vesper renderer target is selected
- `window.electronAPI` has been verified
- a screenshot or DOM summary exists
- blockers, if any, are tied to a specific failed check
