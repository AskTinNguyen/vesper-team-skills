# Workflow: Web

<required_reading>
- ../references/vesper-ui-inspector-analysis.md
- ../references/contracts.md
- ../references/web-porting-guide.md
- ../references/code-examples.md
- ../references/testing-checklist.md
- ../references/troubleshooting.md
</required_reading>

Apply this workflow in order.

## 1. Set Inputs

Define:
- `APP_ROOT`: absolute path to target app repo.
- `CHAT_ENDPOINT`: existing backend endpoint for chat send.
- `AUTH_MODE`: session/cookie/token auth model.

Locate existing send pipeline and auth boundary:

```bash
cd "$APP_ROOT"
rg -n "agentContextPrefix|sendMessage|/chat|fetch\\(|axios|authorization|csrf"
```

## 2. Add Shared Contracts

Create one shared snapshot/context contract used by both:
- UI inspector panel
- backend chat handoff

Do not fork schema per adapter.

Implementation targets (example):
- `src/shared/ui-inspector/types.ts`
- `src/shared/ui-inspector/context.ts`

Verification checkpoint:

```bash
cd "$APP_ROOT"
rg -n "UiInspectorSnapshot|buildUiInspectorContextPayload|InspectorResult|InspectorError"
```

Expected outcome:
- one contract module is imported by both UI capture code and chat send adapter

## 3. Build Client Capture Layer

Implement overlay + click capture with:
- inspector chrome exclusion
- selector fallback chain
- redaction and payload caps
- optional screenshot pipeline

Implementation targets (example):
- `src/ui/inspector/overlay.tsx`
- `src/ui/inspector/capture.ts`

Verification checkpoint:

```bash
cd "$APP_ROOT"
rg -n "data-ui-inspector-chrome|selectorForElement|redact|MAX_OUTER_HTML_LENGTH|SCREENSHOT_MAX_BYTES"
```

Expected outcome:
- click capture returns a normalized snapshot using canonical caps from `../references/contracts.md`

## 4. Build Context + Send Adapter

Send through existing API with:
- prompt
- `agentContextPrefix`
- optional visible inspector attachment summary

Use timeout + abort + error handling.

Implementation targets (example):
- `src/api/chat/send.ts`
- `src/ui/inspector/send-inspector-context.ts`

Verification checkpoint:

```bash
cd "$APP_ROOT"
rg -n "agentContextPrefix|uiInspectorAttachment|AbortController|SEND_FAILED|PERMISSION_BLOCKED"
```

Expected outcome:
- adapter returns typed errors and does not create a parallel execution path outside the existing chat send pipeline

## 5. Add Agent Parity API/Tools

Expose read-only endpoints or tools equivalent to:
- `get_state`
- `get_selection`
- `get_context`
- `capture_screenshot` (if enabled)

Verification checkpoint:

```bash
cd "$APP_ROOT"
rg -n "vesper_ui_get_state|vesper_ui_get_selection|vesper_ui_get_context|vesper_ui_capture_screenshot|get_state|get_selection|get_context|capture_screenshot"
```

Expected outcome:
- agent path returns the same snapshot/context data shown in the UI panel

## 6. Add Policy + Security Guards

Enforce:
- dev-mode feature flag
- redaction policy
- same-origin and auth checks
- size caps before model handoff

Verification checkpoint:

```bash
cd "$APP_ROOT"
rg -n "uiInspectorEnabled|uiInspectorScreenshotsEnabled|uiInspectorSendToChatEnabled|same-origin|csrf|authorization"
```

Expected outcome:
- feature can be disabled instantly and rejects unauthorized cross-origin requests

## 7. Run Verification

Use `../references/testing-checklist.md` commands and edge-case matrix.

## 8. Rollout

Follow staged rollout + observability requirements in `../references/web-porting-guide.md`.

## 9. Report

Return output using the `Agent Response Contract` in `../SKILL.md`.
