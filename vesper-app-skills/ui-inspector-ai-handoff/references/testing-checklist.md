# Testing Checklist

Use this checklist for every implementation of this skill.

## Command Templates

Set:
- `APP_ROOT=/absolute/path/to/app`

Run static wiring checks:

```bash
cd "$APP_ROOT"
rg -n "vesper_ui_get_state|vesper_ui_get_selection|vesper_ui_get_context|vesper_ui_capture_screenshot"
rg -n "mcp__session__vesper_ui_get_state|mcp__session__vesper_ui_get_selection|mcp__session__vesper_ui_get_context|mcp__session__vesper_ui_capture_screenshot"
rg -n "agentContextPrefix|uiInspectorAttachment|buildUiInspectorContextPayload|InspectorResult|InspectorError"
```

## Test Runner Matrix

Use the runner your app already uses.

1. Discover candidate tests:

```bash
cd "$APP_ROOT"
rg --files | rg "(ui-inspector|vesper-ui-tools|inspector).*test|spec"
```

2. Run one matching command:

```bash
# Capture first matching test path once
TEST_PATH="$(rg --files | rg '(ui-inspector|vesper-ui-tools|inspector).*test|spec' | head -n 1)"
[ -z "$TEST_PATH" ] && echo "No inspector test found" && exit 1

# Bun
bun test "$TEST_PATH"

# Vitest
pnpm vitest run "$TEST_PATH"

# Jest
npx jest "$TEST_PATH"

# Playwright
pnpm playwright test -g "ui inspector"
```

## CI Gate (Minimum)

Require all of:
- naming checks pass
- context builder wiring is present
- read-only allowlist entries are present
- unit/integration tests for redaction + context trimming pass
- integration test for capture -> send flow passes

## Thresholds

Use canonical caps from `./contracts.md`.
Do not duplicate numeric values in project-local docs unless you also reference the canonical source.

## Edge-Case Matrix

| Case | Expected Behavior | Failure Fallback |
|---|---|---|
| Shadow DOM node | capture nearest valid inspectable element | return typed `CAPTURE_FAILED` with retry |
| Portal node | capture visual target and stable selector fallback | store route + component path |
| Iframe boundary | block cross-origin capture | metadata-only capture |
| Detached node during click | abort capture cleanly | ask user to recapture |
| Zero-size element | ignore and prompt for another target | keep inspect mode active |
| Animated layout shift | stabilize across multiple frames | retry after 1 frame window |
| Two windows/tabs active | isolated state per window/tab key | no cross-window snapshot overwrite |

## Redaction Tests

Minimum assertions:
- password/hidden input values are redacted
- token-like strings are redacted
- sensitive query params are stripped
- unrelated form values are not serialized

## Runtime Parity Smoke Checks

Manual minimum:
1. Capture a UI node from the panel.
2. Send prompt with inspector context.
3. Call read-only tool (`vesper_ui_get_selection` or equivalent).
4. Confirm tool payload matches panel selection (selector/route/label + capped excerpts).

Automated minimum (recommended in CI):

```bash
cd "$APP_ROOT"
PARITY_TEST="$(rg --files | rg '(ui-inspector|vesper-ui-tools|inspector).*(test|spec)' | head -n 1)"
[ -n "$PARITY_TEST" ] && bun test "$PARITY_TEST"
```

## Final Verification

Run helper from `vesper-team-skills` repo root:

```bash
./ui-inspector-ai-handoff/scripts/verify-inspector-parity.sh "$APP_ROOT"
```

Run helper with behavioral smoke command:

```bash
PARITY_TEST="$(cd "$APP_ROOT" && rg --files | rg '(ui-inspector|vesper-ui-tools|inspector).*(test|spec)' | head -n 1)"
[ -z "$PARITY_TEST" ] && echo "No parity test file found" && exit 1
./ui-inspector-ai-handoff/scripts/verify-inspector-parity.sh "$APP_ROOT" --smoke-command "bun test \"$PARITY_TEST\""
```

Require typed error contract checks:

```bash
REQUIRE_TYPED_ERRORS=1 ./ui-inspector-ai-handoff/scripts/verify-inspector-parity.sh "$APP_ROOT"
```

Require both code taxonomy and typed shape checks:

```bash
REQUIRE_ERROR_CODES=1 REQUIRE_TYPED_ERRORS=1 ./ui-inspector-ai-handoff/scripts/verify-inspector-parity.sh "$APP_ROOT"
```

Note:
- enable strict flags only after your implementation adopts typed error-code taxonomy end to end.
- parity checks against current Vesper baseline may pass default mode but fail strict mode by design.

Or from inside this skill directory:

```bash
./scripts/verify-inspector-parity.sh "$APP_ROOT"
```

If checks fail, use `./references/troubleshooting.md`.
