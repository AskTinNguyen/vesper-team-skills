# Vesper UI Inspector Analysis

This reference summarizes what Vesper ships and which decisions to preserve.

## End-To-End Model

1. Human selects live UI element in dev mode.
2. Renderer captures normalized snapshot.
3. Main process stores workspace-scoped inspector state.
4. Chat send injects hidden context prefix.
5. Agent tools read same state through callback bridge.

## Shared Contracts

Source of truth in Vesper:
- `apps/electron/src/shared/ui-inspector-types.ts`
- `apps/electron/src/shared/ui-inspector-context.ts`

Core payload includes:
- selector/tag/label/route/bounds
- style subset + data attributes
- component path
- optional react source metadata
- optional screenshot data URL

## Capture + Redaction Defaults (Vesper)

Observed defaults in current implementation:
- `MAX_OUTER_HTML_LENGTH = 4000`
- `MAX_TEXT_SNIPPET_LENGTH = 500`
- `MAX_COMPONENT_PATH_DEPTH = 10`
- `CONTEXT_HTML_EXCERPT_MAX = 2400`
- `CONTEXT_TEXT_EXCERPT_MAX = 360`
- `CONTEXT_MAX_STYLE_KEYS = 120`
- `CONTEXT_MAX_DATA_ATTR_KEYS = 20`
- `SCREENSHOT_MAX_BYTES = 4 * 1024 * 1024`

Use equal or stricter values unless product requirements justify expansion.
Canonical cap ranges and resolution order live in `./contracts.md`.

## Human Path Highlights

- Overlay uses capture listeners and crosshair cursor.
- Inspector chrome is excluded from hit testing.
- Panel provides copy/send/clear/open actions.
- Send-to-chat can attach screenshot + hidden context prefix.

## Agent Path Highlights

Read-only tools:
- `vesper_ui_get_state`
- `vesper_ui_get_selection`
- `vesper_ui_get_context`
- `vesper_ui_capture_screenshot`

Permission model explicitly allowlists MCP-prefixed variants in safe mode.

Scope note:
- current Vesper implementation is workspace-scoped.
- this skill recommends `workspaceId + windowId` for stronger isolation in multi-window apps.

## Portability Rules

1. Keep one snapshot schema for all adapters.
2. Keep one context-builder function.
3. Route through existing chat send path.
4. Keep tools read-only by policy.
5. Redact before persistence and before model handoff.
