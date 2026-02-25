#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-.}"

if ! command -v rg >/dev/null 2>&1; then
  echo "ripgrep (rg) is required for this scan." >&2
  exit 1
fi

COMMON_GLOBS=(
  --hidden
  --glob '!.git'
  --glob '!node_modules'
  --glob '!dist'
  --glob '!build'
)

print_section() {
  printf '\n== %s ==\n' "$1"
}

print_section "Credential-bearing GitHub URLs"
rg -n "${COMMON_GLOBS[@]}" 'https?://[^/\s:@]+:[^/\s@]+@github\.com|https?://[^/\s@]+@github\.com' "$ROOT" || true

print_section "Possible token exposure in logs or payloads"
rg -n "${COMMON_GLOBS[@]}" 'ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|Authorization:\s*(token|bearer)|\baccessToken\b|github.*token' "$ROOT" || true

print_section "Subprocess env inheritance without filtering"
rg -n "${COMMON_GLOBS[@]}" 'env:\s*process\.env|env:\s*\{\s*\.\.\.process\.env' "$ROOT" || true

print_section "IPC handlers mentioning token-like fields"
if [ -d "$ROOT/apps" ] || [ -d "$ROOT/packages" ]; then
  rg -n "${COMMON_GLOBS[@]}" 'ipc(Main|Renderer)\.(handle|on).*token|oauth.*token|\baccessToken\b' "$ROOT/apps" "$ROOT/packages" 2>/dev/null || true
else
  rg -n "${COMMON_GLOBS[@]}" 'ipc(Main|Renderer)\.(handle|on).*token|oauth.*token|\baccessToken\b' "$ROOT" || true
fi

printf '\nScan complete. Review each hit manually before patching.\n'
