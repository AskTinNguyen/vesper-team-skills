# Electron Porting Guide

Use `../workflows/electron.md` for sequence. This file defines Electron-specific integration contracts.
Use `./contracts.md` as the canonical source for caps and error taxonomy.

## IPC Contract

Required channels:
- `uiInspector:getState`
- `uiInspector:setMode`
- `uiInspector:setSnapshot`
- `uiInspector:clear`
- `uiInspector:stateChanged`
- `uiInspector:captureScreenshot`
- `uiInspector:sendToChat`

Required preload APIs:
- `uiInspectorGetState()`
- `uiInspectorSetMode(mode)`
- `uiInspectorSetSnapshot(snapshot)`
- `uiInspectorClear()`
- `uiInspectorCaptureScreenshot(bounds, scale?, captureContext?)`
- `uiInspectorSendToChat(sessionId, prompt, options?)`
- `onUiInspectorStateChanged(callback)`

## Required Integration Interfaces

1. `capture(element) -> snapshot`
2. `buildContext(snapshot, options) -> string`
3. `sendMessage(prompt, options.agentContextPrefix, options.uiInspectorAttachment)`
4. `onVesperUiAction({ action, params }) -> InspectorResult<unknown>`

## Typed Result Contract

Return typed errors from tool callbacks and IPC wrappers.

```ts
// Import canonical types from your shared inspector contract module.
type InspectorResult<T> = { success: true; data: T } | { success: false; error: InspectorError };
```

Compatibility note:
- if existing implementation returns string errors, normalize those into `InspectorError` at adapter boundaries.

## State Scope Requirements

- keep state scoped by `workspaceId + windowId`
- avoid cross-window snapshot reads
- clear per-window state on teardown
- keep `updatedAt` monotonic per state record

## Fallback Matrix

| Failure | First Fallback | Second Fallback |
|---|---|---|
| Full-frame crop fails | direct rect capture | disable screenshot and continue with metadata |
| No selection on send | keep panel open | show capture instruction |
| Agent callback unavailable | human send path only | copy-context manual fallback |

## Observability Events

Suggested metric/event names:
- `ui_inspector_mode_toggled`
- `ui_inspector_capture_success`
- `ui_inspector_capture_failure`
- `ui_inspector_send_success`
- `ui_inspector_send_failure`
- `ui_inspector_tool_call`

## Canonical Snippets

Use reusable code from `./code-examples.md` for:
- selector generation
- redaction
- callback bridge
- robust send adapter

Troubleshooting:
- use `./troubleshooting.md` for symptom -> diagnostic -> fix guidance.
