# Contracts

Use this document as the single source of truth for configuration caps and typed error handling.

## Configuration Caps

Use defaults unless stricter local policy is required.

| Key | Default | Min | Max | Suggested Env Key | Enforced In |
|---|---:|---:|---:|---|---|
| `MAX_OUTER_HTML_LENGTH` | `4000` | `200` | `8000` | `UI_INSPECTOR_MAX_OUTER_HTML_LENGTH` | capture serializer |
| `MAX_TEXT_SNIPPET_LENGTH` | `500` | `80` | `2000` | `UI_INSPECTOR_MAX_TEXT_SNIPPET_LENGTH` | capture serializer |
| `MAX_COMPONENT_PATH_DEPTH` | `10` | `3` | `20` | `UI_INSPECTOR_MAX_COMPONENT_PATH_DEPTH` | capture serializer |
| `CONTEXT_HTML_EXCERPT_MAX` | `2400` | `120` | `4000` | `UI_INSPECTOR_CONTEXT_HTML_EXCERPT_MAX` | context builder |
| `CONTEXT_TEXT_EXCERPT_MAX` | `360` | `80` | `1000` | `UI_INSPECTOR_CONTEXT_TEXT_EXCERPT_MAX` | context builder |
| `CONTEXT_MAX_STYLE_KEYS` | `120` | `20` | `200` | `UI_INSPECTOR_CONTEXT_MAX_STYLE_KEYS` | context builder |
| `CONTEXT_MAX_DATA_ATTR_KEYS` | `20` | `5` | `60` | `UI_INSPECTOR_CONTEXT_MAX_DATA_ATTR_KEYS` | context builder |
| `SCREENSHOT_MAX_BYTES` | `4194304` | `262144` | `6291456` | `UI_INSPECTOR_SCREENSHOT_MAX_BYTES` | screenshot encoder |

## Config Resolution Order

Apply configuration in this order:
1. Static defaults from this document.
2. Environment overrides.
3. Runtime flags or app settings.
4. Clamp final values to min/max ranges above.

Startup validation requirements:
- emit one startup log/event that prints effective values
- fail fast if any configured value cannot be parsed as a number
- reject values outside min/max range after clamping if policy requires strict mode

## Typed Result Schema

Use typed results for IPC and tool callbacks.

```ts
type InspectorErrorCode =
  | "NO_SELECTION"
  | "CAPTURE_FAILED"
  | "SEND_FAILED"
  | "TOOL_UNAVAILABLE"
  | "PERMISSION_BLOCKED";

type InspectorError = {
  code: InspectorErrorCode;
  message: string;
  retriable: boolean;
};

type InspectorResult<T> =
  | { success: true; data: T }
  | { success: false; error: InspectorError };
```

Compatibility rule:
- if a legacy boundary returns string errors, normalize to `InspectorError` before returning from IPC handlers or session tools.

## Error Codes And Fallbacks

| Code | Trigger | Human UI Behavior | Agent Result (typed) | Fallback |
|---|---|---|---|---|
| `NO_SELECTION` | Send/query without current snapshot | Toast/banner: "No UI selection" | `{ success:false, error:{ code:"NO_SELECTION", message:"No UI selection is currently captured.", retriable:true } }` | Prompt to capture first |
| `CAPTURE_FAILED` | Snapshot/screenshot capture fails | Keep mode active, show retry CTA | `{ success:false, error:{ code:"CAPTURE_FAILED", message:"Capture failed.", retriable:true } }` | Retry without screenshot |
| `SEND_FAILED` | Chat send pipeline error | Preserve payload in panel for retry/copy | `{ success:false, error:{ code:"SEND_FAILED", message:"Send failed.", retriable:true } }` | Copy context manually |
| `TOOL_UNAVAILABLE` | Callback bridge missing | Non-blocking warning in dev panel | `{ success:false, error:{ code:"TOOL_UNAVAILABLE", message:"Inspector unavailable.", retriable:false } }` | Human path only |
| `PERMISSION_BLOCKED` | Safe mode/tool policy blocks mutation attempt | Explain read-only boundary | `{ success:false, error:{ code:"PERMISSION_BLOCKED", message:"Blocked by policy.", retriable:false } }` | Ask to change mode intentionally |
