#!/usr/bin/env bash
set -euo pipefail

# reconcile.sh — Full bidirectional reconciliation between GitHub and task list
#
# Usage:
#   reconcile.sh [--dry-run] [--prs-only] [--issues-only]
#
# Performs:
#   1. Sync new open PRs into task list (via sync-prs-to-tasks.sh)
#   2. Sync new open issues into task list (via sync-issues-to-tasks.sh)
#   3. Check PR statuses and update tasks (via pr-status-check.sh)
#   4. Flag discrepancies (tasks without matching GitHub entities)
#
# Requires: gh CLI (authenticated), CLAUDE_CODE_TASK_LIST_ID set

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DRY_RUN=false
PRS_ONLY=false
ISSUES_ONLY=false

usage() {
  cat <<'EOF'
Usage: reconcile.sh [OPTIONS]

Full bidirectional reconciliation between GitHub and the Claude Code task list.

Options:
  --dry-run       Show what would change without modifying tasks
  --prs-only      Only sync and check PRs (skip issues)
  --issues-only   Only sync issues (skip PRs)
  -h, --help      Show this help

Environment:
  CLAUDE_CODE_TASK_LIST_ID  Required. The active task list ID.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=true; shift ;;
    --prs-only) PRS_ONLY=true; shift ;;
    --issues-only) ISSUES_ONLY=true; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage; exit 1 ;;
  esac
done

DRY_FLAG=""
[[ "$DRY_RUN" == "true" ]] && DRY_FLAG="--dry-run"

REPO=$(gh repo view --json nameWithOwner -q '.nameWithOwner' 2>/dev/null) || {
  echo "Error: Not in a GitHub repo or gh not authenticated." >&2
  exit 1
}

echo "=== GitHub Sync Reconciliation ===" >&2
echo "Repo: $REPO" >&2
echo "Task list: ${CLAUDE_CODE_TASK_LIST_ID:-NOT SET}" >&2
echo "" >&2

# Phase 1: Sync new PRs
if [[ "$ISSUES_ONLY" == "false" ]]; then
  echo "--- Phase 1: Syncing open PRs ---" >&2
  bash "$SCRIPT_DIR/sync-prs-to-tasks.sh" $DRY_FLAG
  echo "" >&2
fi

# Phase 2: Sync new issues
if [[ "$PRS_ONLY" == "false" ]]; then
  echo "--- Phase 2: Syncing open issues ---" >&2
  bash "$SCRIPT_DIR/sync-issues-to-tasks.sh" $DRY_FLAG
  echo "" >&2
fi

# Phase 3: Check PR statuses
if [[ "$ISSUES_ONLY" == "false" ]]; then
  echo "--- Phase 3: Checking PR statuses ---" >&2
  bash "$SCRIPT_DIR/pr-status-check.sh" $DRY_FLAG
  echo "" >&2
fi

# Phase 4: Flag orphaned tasks (tasks with GitHub metadata but no matching open entity)
echo "--- Phase 4: Checking for discrepancies ---" >&2

TASKS_ROOT="${HOME}/.claude/tasks"
TASK_DIR="${TASKS_ROOT}/${CLAUDE_CODE_TASK_LIST_ID}"

if [[ -d "$TASK_DIR" ]]; then
  ORPHANED=0
  for task_file in "$TASK_DIR"/*.json; do
    [[ -f "$task_file" ]] || continue

    python3 -c "
import json, re, sys
with open('$task_file') as f:
    task = json.load(f)
if task.get('status') == 'completed':
    sys.exit(0)
desc = task.get('description', '')
pr_match = re.search(r'pr_number=(\d+)', desc)
issue_match = re.search(r'issue_number=(\d+)', desc)
if pr_match or issue_match:
    kind = 'pr' if pr_match else 'issue'
    num = pr_match.group(1) if pr_match else issue_match.group(1)
    print(json.dumps({
        'task_id': task.get('id', ''),
        'subject': task.get('subject', ''),
        'github_type': kind,
        'github_number': int(num)
    }))
" 2>/dev/null || true
  done | while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    GH_TYPE=$(echo "$line" | python3 -c "import json,sys; print(json.load(sys.stdin)['github_type'])")
    GH_NUM=$(echo "$line" | python3 -c "import json,sys; print(json.load(sys.stdin)['github_number'])")
    TASK_ID=$(echo "$line" | python3 -c "import json,sys; print(json.load(sys.stdin)['task_id'])")

    if [[ "$GH_TYPE" == "pr" ]]; then
      STATE=$(gh pr view "$GH_NUM" --json state -q '.state' 2>/dev/null) || STATE="NOT_FOUND"
    else
      STATE=$(gh issue view "$GH_NUM" --json state -q '.state' 2>/dev/null) || STATE="NOT_FOUND"
    fi

    if [[ "$STATE" == "CLOSED" || "$STATE" == "MERGED" || "$STATE" == "NOT_FOUND" ]]; then
      echo "{\"task_id\": \"$TASK_ID\", \"github_type\": \"$GH_TYPE\", \"github_number\": $GH_NUM, \"state\": \"$STATE\", \"action\": \"flag_orphaned\"}"
    fi
  done
fi

echo "" >&2
echo "=== Reconciliation complete ===" >&2
