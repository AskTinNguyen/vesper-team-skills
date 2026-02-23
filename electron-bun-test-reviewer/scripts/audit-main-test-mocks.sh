#!/usr/bin/env bash
set -euo pipefail

# Audit common mock.module surfaces in Electron main-process tests.
# By default, exits non-zero only for critical gaps in files that import sessions.
# Use --strict to fail on all warnings.

strict=0
TEST_ROOT="apps/electron/src/main/__tests__"

if [[ "${1:-}" == "--strict" ]]; then
  strict=1
  shift
fi

if [[ -n "${1:-}" ]]; then
  TEST_ROOT="$1"
fi

if ! command -v rg >/dev/null 2>&1; then
  echo "error: rg (ripgrep) is required" >&2
  exit 2
fi

if [[ ! -d "$TEST_ROOT" ]]; then
  echo "error: test root not found: $TEST_ROOT" >&2
  exit 2
fi

errors=0
warnings=0

emit_warn() {
  echo "WARN: $1"
  warnings=$((warnings + 1))
}

emit_error() {
  echo "ERROR: $1"
  errors=$((errors + 1))
}

workspace_mock_files="$(rg -l "mock\\.module\\('../workspace-path-resolver'" "$TEST_ROOT" || true)"
if [[ -n "$workspace_mock_files" ]]; then
  while IFS= read -r file; do
    [[ -z "$file" ]] && continue
    if ! rg -q "migrateLegacyWorkspaceConfigFields" "$file"; then
      if rg -q "from '../sessions'|import\\('../sessions'" "$file"; then
        emit_error "missing workspace-path-resolver export migrateLegacyWorkspaceConfigFields in: $file"
      else
        emit_warn "missing workspace-path-resolver export migrateLegacyWorkspaceConfigFields in: $file"
      fi
    fi
  done <<<"$workspace_mock_files"
fi

electron_mock_files="$(rg -l "mock\\.module\\('electron'" "$TEST_ROOT" || true)"
if [[ -n "$electron_mock_files" ]]; then
  while IFS= read -r file; do
    [[ -z "$file" ]] && continue
    imports_sessions=0
    if rg -q "from '../sessions'|import\\('../sessions'" "$file"; then
      imports_sessions=1
    fi
    for symbol in app BrowserWindow ipcMain nativeImage; do
      if ! rg -q "$symbol" "$file"; then
        if [[ "$imports_sessions" -eq 1 ]]; then
          emit_error "missing electron mock symbol '$symbol' in sessions-coupled file: $file"
        else
          emit_warn "missing electron mock symbol '$symbol' in: $file"
        fi
      fi
    done
  done <<<"$electron_mock_files"
fi

if [[ "$errors" -ne 0 ]]; then
  echo
  echo "Mock audit failed with $errors critical error(s) and $warnings warning(s)."
  exit 1
fi

if [[ "$strict" -eq 1 && "$warnings" -ne 0 ]]; then
  echo
  echo "Mock audit strict mode failed with $warnings warning(s)."
  exit 1
fi

if [[ "$warnings" -ne 0 ]]; then
  echo
  echo "Mock audit completed with $warnings warning(s) and no critical errors."
else
  echo "Mock audit passed for: $TEST_ROOT"
fi
