# Workflow: Electron

<required_reading>
- ../references/vesper-ui-inspector-analysis.md
- ../references/contracts.md
- ../references/electron-porting-guide.md
- ../references/code-examples.md
- ../references/testing-checklist.md
- ../references/troubleshooting.md
- ../references/source-map.md
</required_reading>

Apply this workflow in order.

## 1. Set Inputs

Define:
- `APP_ROOT`: absolute path to target app repo.
- `WORKSPACE_SCOPE`: choose explicitly:
  - `workspace` for strict parity with current Vesper baseline
  - `workspaceId + windowId` for multi-window hardening (recommended for new apps)
- `CHAT_SEND_ENTRY`: existing send-message function/handler.

Read current implementation points:

```bash
cd "$APP_ROOT"
rg -n "sendMessage|agentContextPrefix|ipcMain.handle|contextBridge|mode-manager|session-scoped-tools"
```

## 2. Enforce State Scope Contract (Required)

Implement these rules before wiring tools:
- If using workspace scope, document cross-window tradeoffs and keep no cross-workspace reads.
- If using window-hardened scope, use `${workspaceId}:${windowId}` (or stricter equivalent).
- Cleanup: clear inspector snapshot when a tracked window is destroyed.
- Concurrency: captures in window A must not mutate state for window B when window-hardened scope is enabled.

Verification checkpoint:

```bash
cd "$APP_ROOT"
rg -n "workspaceId|windowId|BrowserWindow|destroyed|clearSnapshot|uiInspector"
```

Expected outcome:
- two open windows can hold different snapshots concurrently
- closing one window does not clear the other window state

## 3. Add Shared Contracts

Create or extend one shared module for:
- mode/state/snapshot types
- send options/result types
- chat-visible attachment type

Use canonical names and keep fields aligned with `../references/contracts.md` and `../references/code-examples.md`.

## 4. Build Main Inspector Service

Implement:
- `getState`
- `setMode`
- `setSnapshot`
- `clearSnapshot`
- `subscribe`
- screenshot capture with byte cap + resize fallback

Persist in-memory only for v1 unless product requirements demand persistence.

## 5. Add IPC + Preload Bridge

Add channels for:
- get state
- set mode
- set snapshot
- clear
- state changed event
- capture screenshot
- send to chat

Expose typed preload APIs. Do not call raw IPC from renderer.

## 6. Build Renderer Overlay + Panel

Implement:
- hover highlight
- click capture
- `Esc` to cancel
- inspector chrome exclusion (`data-ui-inspector-chrome="true"`)
- panel actions: copy context, clear, send

Capture must include redaction and cap behavior.

## 7. Wire Chat Handoff

Send via existing chat pipeline with:
- user prompt
- hidden `agentContextPrefix`
- optional visible inspector attachment

Do not create a separate LLM execution path.

## 8. Add Agent Read-Only Tools

Add callback bridge + tools with canonical IDs:
- `vesper_ui_get_state`
- `vesper_ui_get_selection`
- `vesper_ui_get_context`
- `vesper_ui_capture_screenshot`

Add read-only allowlist entries in safe mode policy.

## 9. Run Verification

Use `../references/testing-checklist.md` commands.

Minimum:

```bash
cd "$APP_ROOT"
rg -n "vesper_ui_get_state|vesper_ui_get_selection|vesper_ui_get_context|vesper_ui_capture_screenshot"
rg -n "mcp__session__vesper_ui_get_state|mcp__session__vesper_ui_get_selection|mcp__session__vesper_ui_get_context|mcp__session__vesper_ui_capture_screenshot"
rg -n "NO_SELECTION|CAPTURE_FAILED|SEND_FAILED|TOOL_UNAVAILABLE|PERMISSION_BLOCKED"
```

## 10. Report

Return output using the `Agent Response Contract` in `../SKILL.md`.
