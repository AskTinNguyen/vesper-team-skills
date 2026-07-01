# Vesper UI Inspector Plan

Date: 2026-03-01
Worktree: `paper-clone-ui-inspector-plan`
Parent branch: `worktree-paper-clone`

## Goal

Bring canvas-style component handoff to the Vesper Electron app itself so developers can point at live UI, capture precise component context, and route that context directly to agents for fast UI/UX edits.

This must preserve Vesper's parity-by-design rule:
- humans need a direct in-app inspector workflow,
- agents need equivalent read-only access to the same captured state,
- one shared core service must back both paths.

## What We Already Have

Existing patterns we should reuse instead of inventing a new architecture:

- Canvas renderer capture and metadata composition in `apps/electron/src/renderer/pages/CanvasPage.tsx`
- Canvas main-process IPC and screenshot capture in `apps/electron/src/main/ipc-canvas.ts`
- Canvas session-scoped tool proxy wiring in `apps/electron/src/main/sessions.ts`
- Code-eligible proxy tool pattern in `packages/shared/src/agent/canvas-tools.ts`
- Session tool callback registry in `packages/shared/src/agent/session-scoped-tools.ts`
- Internal prompt injection using `agentContextPrefix` in `apps/electron/src/main/sessions.ts`
- Human-side action surfaces via JSON Render in `apps/electron/src/renderer/components/json-render/*`

## Target User Workflow

### Human path

1. Developer toggles `UI Inspector` in Vesper.
2. Hover highlights any visible renderer element.
3. Click captures a snapshot of that element.
4. Inspector sidebar/popover shows:
   - component label
   - file path + line (dev-only when available)
   - selector
   - bounding box
   - computed styles
   - HTML snippet
   - screenshot preview
5. Developer clicks `Send to Chat`.
6. Vesper sends the developer's next message with an internal inspector context prefix, so the agent knows exactly what to edit.

### Agent path

1. The same snapshot is stored in a shared inspector service in main.
2. Session-scoped tools expose read-only access to the active snapshot.
3. Agents can inspect the selected UI node and then use normal file-edit tools to patch the source.

## Scope

## In scope (initial delivery)

- Dev-only inspector overlay for the Electron renderer UI
- Single-node selection
- DOM metadata capture
- Renderer screenshot capture for selected element
- Prompt handoff via `agentContextPrefix`
- Session-scoped read-only inspector tools
- Safe-mode classification for read-only tools

## Out of scope (initial delivery)

- Arbitrary multi-select annotations
- Visual diffing against prior snapshots
- Automatic code edits from inspector without a chat turn
- Production-mode source mapping guarantees
- Persistent long-term storage of inspector history

## Architecture

### 1. Shared contracts

Create a dedicated shared contract module so renderer, preload, main, and agent tools all use the same payload.

New file:
- `apps/electron/src/shared/ui-inspector-types.ts`

Add types:
- `VesperUiInspectorMode = 'off' | 'inspect'`
- `VesperUiInspectorSourceLocation`
- `VesperUiInspectorComponentRef`
- `VesperUiInspectorNodeSummary`
- `VesperUiInspectorSnapshot`
- `VesperUiInspectorState`

Recommended `VesperUiInspectorSnapshot` fields:
- `id`
- `capturedAt`
- `route`
- `workspaceId`
- `sessionId`
- `selector`
- `tagName`
- `role`
- `label`
- `textSnippet`
- `outerHtml`
- `bounds` (`x`, `y`, `width`, `height`)
- `computedStyle`
- `dataAttributes`
- `componentPath` (DOM ancestry summary)
- `reactComponent`:
  - `displayName`
  - `ownerStack`
  - `source` (`filePath`, `line`, `column`) when available
- `screenshotDataUrl` or base64 payload

Reason:
- keeps the inspector payload stable across UI and agent adapters
- avoids bloating `shared/types.ts` with a large nested contract

### 2. Main-process core service

New file:
- `apps/electron/src/main/ui-inspector.ts`

Responsibilities:
- hold ephemeral per-window or per-workspace inspector state
- store current mode (`off` or `inspect`)
- store latest captured snapshot
- expose read methods for session tools
- broadcast updates to renderer windows
- capture screenshots using the same `capturePage` pattern canvas uses

Recommended service surface:
- `setUiInspectorMode(workspaceId, mode)`
- `getUiInspectorState(workspaceId)`
- `setUiInspectorSnapshot(workspaceId, snapshot)`
- `clearUiInspectorSnapshot(workspaceId)`
- `captureUiInspectorScreenshot(window, bounds)`
- `subscribeUiInspectorChanges(callback)`

Storage model:
- in-memory only for v1
- no disk persistence
- last snapshot per workspace is enough for the first iteration

### 3. IPC + preload bridge

Files:
- `apps/electron/src/main/ipc.ts`
- new `apps/electron/src/main/ipc-ui-inspector.ts`
- `apps/electron/src/shared/types.ts`
- `apps/electron/src/preload/index.ts`

Add IPC channels:
- `UI_INSPECTOR_GET_STATE`
- `UI_INSPECTOR_SET_MODE`
- `UI_INSPECTOR_SET_SNAPSHOT`
- `UI_INSPECTOR_CLEAR`
- `UI_INSPECTOR_STATE_CHANGED`
- `UI_INSPECTOR_CAPTURE_SCREENSHOT`
- `UI_INSPECTOR_SEND_TO_CHAT`

Add preload methods to `ElectronAPI`:
- `uiInspectorGetState()`
- `uiInspectorSetMode(mode)`
- `uiInspectorSetSnapshot(snapshot)`
- `uiInspectorClear()`
- `uiInspectorCaptureScreenshot(bounds)`
- `uiInspectorSendToChat(sessionId, prompt, options?)`
- `onUiInspectorStateChanged(callback)`

`uiInspectorSendToChat(...)` should call the existing `sendMessage(...)` path with a generated `agentContextPrefix`, not a separate agent execution path.

### 4. Renderer human adapter

New files:
- `apps/electron/src/renderer/atoms/ui-inspector.ts`
- `apps/electron/src/renderer/components/dev/UiInspectorOverlay.tsx`
- `apps/electron/src/renderer/components/dev/UiInspectorPanel.tsx`
- `apps/electron/src/renderer/lib/ui-inspector/capture.ts`
- `apps/electron/src/renderer/lib/ui-inspector/react-devtools.ts`

Likely touch points:
- `apps/electron/src/renderer/App.tsx`
- or `apps/electron/src/renderer/components/app-shell/AppShell.tsx`

Responsibilities:

`UiInspectorOverlay.tsx`
- full-screen transparent overlay in inspect mode
- tracks pointer target using `document.elementFromPoint`
- draws hover highlight box
- captures clicked element
- ignores the overlay and inspector UI itself

`capture.ts`
- converts a clicked `Element` into `VesperUiInspectorSnapshot`
- extracts:
  - selector fallback chain (`id`, `data-*`, stable DOM path)
  - tag name / role / accessible label
  - `outerHTML` (trimmed)
  - text snippet (trimmed)
  - computed style allowlist
  - ancestry path summaries
  - relevant `data-testid`, `data-slot`, `data-state`, `data-node-id`

`react-devtools.ts`
- dev-gated best-effort extraction of React component metadata
- traverse React fiber from DOM node
- capture `displayName`
- capture owner stack
- capture `_debugSource.fileName`, `lineNumber`, `columnNumber` when present
- fail soft in production or when metadata is unavailable

`UiInspectorPanel.tsx`
- shows current snapshot details
- actions:
  - `Copy Context`
  - `Open File`
  - `Show In Folder`
  - `Send to Chat`
  - `Clear`

### 5. Agent adapter (session-scoped tools)

New file:
- `packages/shared/src/agent/vesper-ui-tools.ts`

Follow the same proxy pattern as `canvas-tools.ts`.

New read-only tools:
- `vesper_ui_get_selection`
- `vesper_ui_get_node`
- `vesper_ui_get_tree`
- `vesper_ui_get_styles`
- `vesper_ui_screenshot`

Tool semantics:
- `vesper_ui_get_selection`: returns the active snapshot summary
- `vesper_ui_get_node`: returns the full snapshot
- `vesper_ui_get_tree`: returns the captured DOM/component ancestry tree
- `vesper_ui_get_styles`: returns the captured computed style subset
- `vesper_ui_screenshot`: returns the captured screenshot or requests a fresh one from main

Integration points:
- register callback getter in `session-scoped-tools.ts`
- add `onVesperUiAction` to `SessionScopedToolCallbacks`
- wire `managed.agent.onVesperUiAction` in `apps/electron/src/main/sessions.ts`
- add the tools to the code-mode eligible tool set and the non-code-mode fallback path

### 6. Safe mode and permissions

File:
- `packages/shared/src/agent/mode-manager.ts`

Mark these as read-only and allowed in safe mode:
- `mcp__session__vesper_ui_get_selection`
- `mcp__session__vesper_ui_get_node`
- `mcp__session__vesper_ui_get_tree`
- `mcp__session__vesper_ui_get_styles`
- `mcp__session__vesper_ui_screenshot`

Reason:
- inspection should be allowed without granting mutation power
- actual code changes still require normal file tools and existing permission gates

## Prompt Handoff Contract

When the developer clicks `Send to Chat`, we should generate a structured context prefix and pass it through the existing `sendMessage(..., { agentContextPrefix })` path.

Recommended format:

```xml
<vesper_ui_inspector_context>
  <target>
    <label>SessionList row</label>
    <selector>[data-testid="session-row"]</selector>
    <route>chat/session/abc</route>
    <bounds x="12" y="144" width="320" height="52" />
  </target>
  <react>
    <component>SessionListItem</component>
    <source file="/abs/path/apps/electron/src/renderer/components/app-shell/SessionList.tsx" line="612" />
  </react>
  <style>{...trimmed json...}</style>
  <html><![CDATA[<button ...>...</button>]]></html>
  <instructions>
    The user is referring to this live Vesper UI element. Prefer editing the source file above.
  </instructions>
</vesper_ui_inspector_context>
```

Rules:
- keep it compact enough for normal chat turns
- trim `outerHTML` and style payloads
- do not include secrets or user message contents from unrelated UI regions

## Delivery Phases

### Phase 1: Shared contracts + renderer-only MVP

Goal:
- let developers inspect a single element and manually review its metadata

Work:
- add `ui-inspector-types.ts`
- add renderer atoms
- mount `UiInspectorOverlay`
- capture DOM metadata only (no React source yet)
- render panel with current snapshot

Acceptance:
- inspect mode can be toggled
- hovering highlights elements reliably
- clicking captures selector, bounds, HTML, text, and styles
- panel can clear and recapture

### Phase 2: Main-process service + screenshot + chat handoff

Goal:
- make the snapshot sharable and useful for real agent work

Work:
- add `ui-inspector.ts`
- add IPC handlers and preload bridge
- add screenshot capture in main
- add `Send to Chat` action using `agentContextPrefix`
- reuse existing `open_path` and `show_in_folder` actions where possible

Acceptance:
- selected snapshot survives renderer component remounts during the session
- screenshot preview appears in the panel
- `Send to Chat` injects structured context and starts a normal session turn

### Phase 3: Session-scoped read-only tools

Goal:
- give agents direct access to the same inspector state

Work:
- add `vesper-ui-tools.ts`
- register new callbacks in `session-scoped-tools.ts`
- wire main-process tool handlers in `sessions.ts`
- classify tools as read-only in `mode-manager.ts`

Acceptance:
- agent can query selected UI context without extra human copy/paste
- safe mode still allows inspection
- tools return the same data the panel shows

### Phase 4: React source mapping + polish

Goal:
- make the inspector point agents directly to the right source file

Work:
- add best-effort React fiber extraction
- expose component owner stack
- surface file path + line in panel
- improve selector stability and ignore false-positive targets
- add keyboard shortcut for inspector mode

Acceptance:
- in dev mode, most clicked app components resolve to a meaningful component name
- source file links open the right file in the default editor
- failures degrade gracefully to DOM-only metadata

## File-by-File Change List

### New files

- `apps/electron/src/shared/ui-inspector-types.ts`
- `apps/electron/src/main/ui-inspector.ts`
- `apps/electron/src/main/ipc-ui-inspector.ts`
- `apps/electron/src/renderer/atoms/ui-inspector.ts`
- `apps/electron/src/renderer/components/dev/UiInspectorOverlay.tsx`
- `apps/electron/src/renderer/components/dev/UiInspectorPanel.tsx`
- `apps/electron/src/renderer/lib/ui-inspector/capture.ts`
- `apps/electron/src/renderer/lib/ui-inspector/react-devtools.ts`
- `packages/shared/src/agent/vesper-ui-tools.ts`

### Existing files to modify

- `apps/electron/src/main/ipc.ts`
- `apps/electron/src/main/sessions.ts`
- `apps/electron/src/preload/index.ts`
- `apps/electron/src/shared/types.ts`
- `apps/electron/src/renderer/App.tsx`
- `apps/electron/src/renderer/components/app-shell/AppShell.tsx` (if this is the cleaner mount point)
- `packages/shared/src/agent/vesper-agent.ts`
- `packages/shared/src/agent/session-scoped-tools.ts`
- `packages/shared/src/agent/mode-manager.ts`

## Risks and Mitigations

1. React source metadata may be missing.
- Mitigation: treat React source mapping as optional and dev-only.
- Fallback: use DOM selector + ancestry + screenshot.

2. Overlay may interfere with normal clicks.
- Mitigation: only enable in explicit inspect mode and stop propagation when active.
- Exclude inspector chrome from hit-testing.

3. `outerHTML` and computed styles can be too large.
- Mitigation: trim HTML length, use a style allowlist, and cap payload sizes.

4. Sensitive UI content could be captured.
- Mitigation: redact known secret inputs, avoid serializing values from password/token fields, and trim unrelated text.

5. Multiple windows/workspaces may race.
- Mitigation: scope inspector state by workspace and sender window.

## Test Plan

### Renderer

- Overlay highlights the element under the cursor
- Clicking captures the intended target and not the overlay itself
- Inspector panel shows stable values after rerenders
- Secret input fields are redacted from snapshots

### Main / IPC

- State broadcasts update all listeners in the active workspace window
- Screenshot capture returns an image for valid bounds
- Clearing the snapshot removes active selection state

### Agent integration

- Session tool calls return the current snapshot
- Safe mode allows read-only inspector tools
- `Send to Chat` results in a normal session turn with the injected inspector context

## Recommended Implementation Order

1. Build the shared types and renderer overlay first.
2. Add the main-process service and screenshot support.
3. Add `Send to Chat` with `agentContextPrefix`.
4. Add session-scoped read-only tools.
5. Add React source mapping last, behind a dev-only best-effort gate.

## Definition of Done

This feature is done when:
- a Vesper developer can click a live app component,
- see structured UI context immediately,
- send that context into chat in one step,
- and the agent can also inspect the same selection via tools,
- all without introducing a separate architecture from the existing canvas/session tool patterns.
