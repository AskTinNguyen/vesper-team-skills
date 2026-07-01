# Reference Code Map: Vesper UI Inspector

Use this map to port the pattern into other Electron apps.

## Shared Contract

- `apps/electron/src/shared/ui-inspector-types.ts`
  - Canonical snapshot/state/mode interfaces.

## Main Process

- `apps/electron/src/main/ui-inspector.ts`
  - In-memory workspace-scoped inspector store and screenshot capture.
- `apps/electron/src/main/ipc-ui-inspector.ts`
  - IPC handlers and context-prefix send-to-chat adapter.
- `apps/electron/src/main/ipc.ts`
  - IPC registration entry (`registerUiInspectorIpcHandlers`).

## IPC + Preload Surface

- `apps/electron/src/shared/types.ts`
  - IPC channel constants and typed `ElectronAPI` methods.
- `apps/electron/src/preload/index.ts`
  - Preload bridge methods (`uiInspector*`) and state-change subscription.

## Renderer Human UX

- `apps/electron/src/renderer/atoms/ui-inspector.ts`
  - Inspector state and panel mount/unmount atoms.
- `apps/electron/src/renderer/lib/ui-inspector/capture.ts`
  - DOM metadata capture, selector strategy, style allowlist, redaction.
- `apps/electron/src/renderer/lib/ui-inspector/react-devtools.ts`
  - Best-effort React fiber metadata extraction (`displayName`, source, owner stack).
- `apps/electron/src/renderer/components/dev/UiInspectorOverlay.tsx`
  - Hover highlight and click-to-capture interaction.
- `apps/electron/src/renderer/components/dev/UiInspectorPanel.tsx`
  - Developer panel actions and send-to-chat controls.
- `apps/electron/src/renderer/App.tsx`
  - Runtime shortcut for panel mount/unmount and panel placement.
- `apps/electron/src/renderer/components/app-shell/DevBadge.tsx`
  - Discoverable dev control button and shortcut hint.

## Agent Parity

- `packages/shared/src/agent/vesper-ui-tools.ts`
  - Session-scoped read-only inspector tools.
- `packages/shared/src/agent/session-scoped-tools.ts`
  - Tool callback contract and tool registration for both code mode and fallback path.
- `packages/shared/src/agent/vesper-agent.ts`
  - Agent callback surface (`onVesperUiAction`).
- `apps/electron/src/main/sessions.ts`
  - Main-process callback wiring for inspector tool actions.
- `packages/shared/src/agent/mode-manager.ts`
  - Read-only safe-mode classification for inspector tools.

## Tests

- `packages/shared/src/agent/__tests__/vesper-ui-tools.test.ts`
- `packages/shared/src/agent/__tests__/session-scoped-tools.test.ts`
- `packages/shared/src/agent/__tests__/session-scoped-tools-delegation.test.ts`
- `packages/shared/src/agent/__tests__/session-scoped-tools-profile.test.ts`
- `packages/shared/tests/mode-manager.test.ts`
