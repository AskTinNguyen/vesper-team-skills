# Vesper Source Map

Use this map when adapting the pattern from Vesper.

## Shared Contracts

- `apps/electron/src/shared/ui-inspector-types.ts`
- `apps/electron/src/shared/ui-inspector-context.ts`

## Main Process

- `apps/electron/src/main/ui-inspector.ts`
- `apps/electron/src/main/ipc-ui-inspector.ts`
- `apps/electron/src/main/ui-inspector-live-capture.ts`
- `apps/electron/src/main/sessions.ts`

## Preload And IPC Types

- `apps/electron/src/preload/index.ts`
- `apps/electron/src/shared/types.ts`

## Renderer

- `apps/electron/src/renderer/lib/ui-inspector/capture.ts`
- `apps/electron/src/renderer/lib/ui-inspector/react-devtools.ts`
- `apps/electron/src/renderer/components/dev/UiInspectorOverlay.tsx`
- `apps/electron/src/renderer/components/dev/UiInspectorPanel.tsx`
- `apps/electron/src/renderer/atoms/ui-inspector.ts`
- `apps/electron/src/renderer/components/app-shell/DevBadge.tsx`
- `apps/electron/src/renderer/App.tsx`

Renderer caveat:
- `react-devtools.ts` relies on private React internals for best-effort source extraction in dev mode.
- treat source extraction as optional and fail soft when internals are unavailable.

## Agent Tool Bridge

- `packages/shared/src/agent/vesper-ui-tools.ts`
- `packages/shared/src/agent/session-scoped-tools.ts`
- `packages/shared/src/agent/vesper-agent.ts`
- `packages/shared/src/agent/mode-manager.ts`

## Tests

- `packages/shared/src/agent/__tests__/vesper-ui-tools.test.ts`
