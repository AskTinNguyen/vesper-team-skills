# Implementation Checklist: Electron UI Inspector

Use this as a delivery checklist when implementing the feature in another Electron app.

## Phase 1: Contracts and Core

- [ ] Add shared inspector types (`mode`, `state`, `snapshot`, `bounds`, `send options`).
- [ ] Build main-process inspector state service (set/get/clear/subscribe).
- [ ] Add screenshot capture helper with bounds normalization and max-size control.

## Phase 2: IPC and Preload

- [ ] Add IPC channels for:
  - [ ] `getState`
  - [ ] `setMode`
  - [ ] `setSnapshot`
  - [ ] `clear`
  - [ ] `captureScreenshot`
  - [ ] `sendToChat`
  - [ ] `stateChanged` event
- [ ] Register IPC handlers in main registration entry.
- [ ] Expose typed preload API and `onStateChanged` listener.

## Phase 3: Renderer Capture UX

- [ ] Add state atoms/store for inspector state and panel visibility.
- [ ] Add overlay to highlight hovered element and capture click target.
- [ ] Implement capture utility with:
  - [ ] selector fallback logic (`id`, `data-*`, role, classes, tag)
  - [ ] text/HTML trimming
  - [ ] style allowlist subset
  - [ ] `data-*` extraction
  - [ ] component path ancestry
  - [ ] optional React source metadata
- [ ] Add panel with selection preview and actions.

## Phase 4: Developer Controls

- [ ] Mount/unmount panel at runtime (no restart).
- [ ] Add discoverable dev control in app shell.
- [ ] Add panel toggle shortcut.
- [ ] Add inspect mode shortcut.
- [ ] Ensure hiding panel also exits inspect mode.

## Phase 5: Agent Handoff and Tooling

- [ ] Build structured context block serializer.
- [ ] Route send-to-chat through existing message path with context prefix.
- [ ] Add session-scoped read-only inspector tools.
- [ ] Wire tool callbacks from agent runtime to main inspector service.
- [ ] Mark inspector tools as read-only in permission/safe mode configuration.

## Phase 6: Safety and Quality

- [ ] Redact sensitive node values (password inputs minimum).
- [ ] Keep payload bounded (style key allowlist, trim caps, screenshot cap).
- [ ] Fail soft when source metadata is unavailable.
- [ ] Verify panel does not self-capture (ignore inspector chrome nodes).

## Phase 7: Validation

- [ ] Manual:
  - [ ] Toggle panel on/off while app runs.
  - [ ] Capture at least 3 different components.
  - [ ] Confirm source path/line appears in dev builds when available.
  - [ ] Confirm `Send to Chat` injects structured inspector context.
- [ ] Agent path:
  - [ ] Query read-only inspector tools after a capture.
  - [ ] Confirm returned data matches panel snapshot.
- [ ] Automation:
  - [ ] Run targeted tests for tool registration/callback wiring.
  - [ ] Run permission-mode tests covering read-only classification.
