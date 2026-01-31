#!/usr/bin/env bash
set -euo pipefail

# check-agent-output.sh — Detect uncommitted agent work
#
# Usage:
#   check-agent-output.sh [--json] [--path DIR]
#
# Checks for:
#   - Uncommitted changes (staged and unstaged)
#   - Untracked files (excluding common noise)
#   - Unpushed commits
#   - Branches without upstream
#
# Output: Human-readable summary (default) or JSON (--json)

OUTPUT_JSON=false
REPO_PATH="."

while [[ $# -gt 0 ]]; do
  case "$1" in
    --json) OUTPUT_JSON=true; shift ;;
    --path) REPO_PATH="$2"; shift 2 ;;
    -h|--help)
      echo "Usage: check-agent-output.sh [--json] [--path DIR]"
      echo "Detect uncommitted changes, untracked files, and unpushed commits."
      exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

cd "$REPO_PATH"

# Check we're in a git repo
if ! git rev-parse --is-inside-work-tree &>/dev/null; then
  echo "Error: Not a git repository: $REPO_PATH" >&2
  exit 1
fi

# Gather data
BRANCH=$(git branch --show-current 2>/dev/null || echo "detached")
STAGED=$(git diff --cached --name-only 2>/dev/null || true)
UNSTAGED=$(git diff --name-only 2>/dev/null || true)
UNTRACKED=$(git ls-files --others --exclude-standard 2>/dev/null | grep -v -E '(\.DS_Store|__pycache__|node_modules|\.pyc$)' || true)

# Check for unpushed commits
UPSTREAM=$(git rev-parse --abbrev-ref "@{upstream}" 2>/dev/null || echo "")
if [[ -n "$UPSTREAM" ]]; then
  UNPUSHED=$(git log "$UPSTREAM..HEAD" --oneline 2>/dev/null || true)
  HAS_UPSTREAM=true
else
  UNPUSHED=""
  HAS_UPSTREAM=false
fi

# Counts
STAGED_COUNT=$(echo "$STAGED" | grep -c . 2>/dev/null || echo 0)
UNSTAGED_COUNT=$(echo "$UNSTAGED" | grep -c . 2>/dev/null || echo 0)
UNTRACKED_COUNT=$(echo "$UNTRACKED" | grep -c . 2>/dev/null || echo 0)
UNPUSHED_COUNT=$(echo "$UNPUSHED" | grep -c . 2>/dev/null || echo 0)

HAS_WORK=false
if [[ "$STAGED_COUNT" -gt 0 || "$UNSTAGED_COUNT" -gt 0 || "$UNTRACKED_COUNT" -gt 0 || "$UNPUSHED_COUNT" -gt 0 || "$HAS_UPSTREAM" == "false" ]]; then
  HAS_WORK=true
fi

if [[ "$OUTPUT_JSON" == "true" ]]; then
  python3 -c "
import json
result = {
    'branch': '$BRANCH',
    'has_work': $( [[ "$HAS_WORK" == "true" ]] && echo "True" || echo "False" ),
    'has_upstream': $( [[ "$HAS_UPSTREAM" == "true" ]] && echo "True" || echo "False" ),
    'staged_count': $STAGED_COUNT,
    'unstaged_count': $UNSTAGED_COUNT,
    'untracked_count': $UNTRACKED_COUNT,
    'unpushed_count': $UNPUSHED_COUNT,
    'staged_files': '''$STAGED'''.strip().split('\n') if '''$STAGED'''.strip() else [],
    'unstaged_files': '''$UNSTAGED'''.strip().split('\n') if '''$UNSTAGED'''.strip() else [],
    'untracked_files': '''$UNTRACKED'''.strip().split('\n') if '''$UNTRACKED'''.strip() else [],
}
print(json.dumps(result, indent=2))
"
else
  echo "=== Agent Output Check ==="
  echo "Branch: $BRANCH"
  echo ""

  if [[ "$HAS_WORK" == "false" ]]; then
    echo "No uncommitted work detected. Working tree is clean."
    exit 0
  fi

  if [[ "$STAGED_COUNT" -gt 0 ]]; then
    echo "Staged changes ($STAGED_COUNT files):"
    echo "$STAGED" | sed 's/^/  /'
    echo ""
  fi

  if [[ "$UNSTAGED_COUNT" -gt 0 ]]; then
    echo "Unstaged changes ($UNSTAGED_COUNT files):"
    echo "$UNSTAGED" | sed 's/^/  /'
    echo ""
  fi

  if [[ "$UNTRACKED_COUNT" -gt 0 ]]; then
    echo "Untracked files ($UNTRACKED_COUNT files):"
    echo "$UNTRACKED" | sed 's/^/  /'
    echo ""
  fi

  if [[ "$HAS_UPSTREAM" == "false" ]]; then
    echo "Branch '$BRANCH' has no upstream tracking branch."
    echo ""
  elif [[ "$UNPUSHED_COUNT" -gt 0 ]]; then
    echo "Unpushed commits ($UNPUSHED_COUNT):"
    echo "$UNPUSHED" | sed 's/^/  /'
    echo ""
  fi

  echo "--- Summary: ${STAGED_COUNT} staged, ${UNSTAGED_COUNT} unstaged, ${UNTRACKED_COUNT} untracked, ${UNPUSHED_COUNT} unpushed ---"
fi
