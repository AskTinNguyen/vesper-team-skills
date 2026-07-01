#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 || $# -gt 3 ]]; then
  echo "usage: $0 /absolute/path/to/app-root [--smoke-command '<command>']" >&2
  exit 2
fi

APP_ROOT="$1"
SMOKE_COMMAND=""

if [[ $# -eq 3 ]]; then
  if [[ "$2" != "--smoke-command" ]]; then
    echo "error: second argument must be --smoke-command" >&2
    exit 2
  fi
  SMOKE_COMMAND="$3"
fi

if [[ ! -d "$APP_ROOT" ]]; then
  echo "error: app root not found: $APP_ROOT" >&2
  exit 2
fi

if ! command -v rg >/dev/null 2>&1; then
  echo "error: rg is required" >&2
  exit 2
fi

failures=0

check() {
  local label="$1"
  local pattern="$2"
  if rg -n --hidden --glob '!node_modules/**' "$pattern" "$APP_ROOT" >/dev/null 2>&1; then
    echo "PASS: $label"
  else
    echo "FAIL: $label"
    failures=$((failures + 1))
  fi
}

check "Tool IDs present" "vesper_ui_get_state|vesper_ui_get_selection|vesper_ui_get_context|vesper_ui_capture_screenshot"
check "MCP allowlist present" "mcp__session__vesper_ui_get_state|mcp__session__vesper_ui_get_selection|mcp__session__vesper_ui_get_context|mcp__session__vesper_ui_capture_screenshot"
check "Context builder wiring" "buildUiInspectorContextPayload|agentContextPrefix"
check "Visible attachment wiring" "uiInspectorAttachment"
check "Callback bridge wiring" "onVesperUiAction"

if [[ "${REQUIRE_ERROR_CODES:-0}" == "1" ]]; then
  check "Error taxonomy wiring" "NO_SELECTION|CAPTURE_FAILED|SEND_FAILED|TOOL_UNAVAILABLE|PERMISSION_BLOCKED"
fi

if [[ "${REQUIRE_TYPED_ERRORS:-0}" == "1" ]]; then
  check "Typed error code field wiring" "code:\\s*['\"](NO_SELECTION|CAPTURE_FAILED|SEND_FAILED|TOOL_UNAVAILABLE|PERMISSION_BLOCKED)['\"]"
  check "Typed error retriable field wiring" "retriable\\s*:\\s*(true|false)"
  check "Typed error boundary wiring" "onVesperUiAction|uiInspectorSendToChat|uiInspector:sendToChat"
fi

if [[ -n "$SMOKE_COMMAND" ]]; then
  if (cd "$APP_ROOT" && bash -lc "$SMOKE_COMMAND"); then
    echo "PASS: Smoke command"
  else
    echo "FAIL: Smoke command"
    failures=$((failures + 1))
  fi
else
  echo "WARN: no smoke command provided; only static wiring checks were run"
fi

if [[ "$failures" -gt 0 ]]; then
  echo "verify-inspector-parity: FAILED ($failures checks missing)"
  exit 1
fi

echo "verify-inspector-parity: OK"
