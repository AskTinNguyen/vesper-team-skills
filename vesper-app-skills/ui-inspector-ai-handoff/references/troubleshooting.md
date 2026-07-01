# Troubleshooting

Use this runbook when implementation checks fail.

| Symptom | Likely Cause | Diagnostic Command | Fix |
|---|---|---|---|
| `NO_SELECTION` on send/tool query | Snapshot not captured or state cleared too early | `rg -n "setSnapshot|clearSnapshot|NO_SELECTION" "$APP_ROOT"` | Ensure click capture writes snapshot before send; clear only on explicit clear/window teardown. |
| Screenshot capture fails | Bounds invalid, zero-size node, or byte cap too strict | `rg -n "captureScreenshot|SCREENSHOT_MAX_BYTES|CAPTURE_FAILED" "$APP_ROOT"` | Clamp bounds, retry without screenshot, and keep typed `CAPTURE_FAILED` fallback. |
| `SEND_FAILED` from chat adapter | timeout/auth/backend error in existing send pipeline | `rg -n "agentContextPrefix|AbortController|authorization|csrf|SEND_FAILED" "$APP_ROOT"` | Keep existing send path, add timeout+abort, classify auth/network/server failures into typed errors. |
| Agent tool returns unavailable | callback bridge not wired in session runtime | `rg -n "onVesperUiAction|vesper_ui_get_state|session-scoped-tools" "$APP_ROOT"` | Register callbacks in runtime bootstrap and verify tool IDs match canonical names. |
| Safe mode blocks expected read | tool not marked read-only in permission policy | `rg -n "mcp__session__vesper_ui_|readOnlySessionTools|mode-manager" "$APP_ROOT"` | Add MCP-prefixed inspector IDs to read-only allowlist. |
| Two windows overwrite each other | state key scoped too broadly | `rg -n "workspaceId|windowId|uiInspector" "$APP_ROOT"` | Scope state by `workspaceId + windowId`; clear only per-window on teardown. |
| Payload too large | caps missing in capture/context builder | `rg -n "MAX_OUTER_HTML_LENGTH|CONTEXT_HTML_EXCERPT_MAX|CONTEXT_MAX_STYLE_KEYS" "$APP_ROOT"` | Enforce caps from `contracts.md` before storing/sending payload. |

Escalation:
- if parity checks pass but behavior still drifts, run the full matrix in `testing-checklist.md` and capture a minimal repro with the selected element, route, and tool response payload.
