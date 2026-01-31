#!/usr/bin/env bash
set -euo pipefail

# pr-status-check.sh — Check PR merge/review status and output task update instructions
#
# Usage:
#   pr-status-check.sh [--dry-run]
#
# Reads task list for tasks with pr_number= metadata, checks each PR's current
# status via gh CLI, and outputs JSON lines with recommended task updates.
#
# Requires: gh CLI (authenticated), CLAUDE_CODE_TASK_LIST_ID set

TASKS_ROOT="${HOME}/.claude/tasks"
DRY_RUN=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=true; shift ;;
    -h|--help)
      echo "Usage: pr-status-check.sh [--dry-run]"
      echo "Check PR status for all PR-linked tasks and output update instructions."
      exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

if ! command -v gh &>/dev/null; then
  echo "Error: gh CLI not found." >&2
  exit 1
fi

if [[ -z "${CLAUDE_CODE_TASK_LIST_ID:-}" ]]; then
  echo "Error: CLAUDE_CODE_TASK_LIST_ID not set." >&2
  exit 1
fi

TASK_DIR="${TASKS_ROOT}/${CLAUDE_CODE_TASK_LIST_ID}"

if [[ ! -d "$TASK_DIR" ]]; then
  echo "Error: Task directory not found: $TASK_DIR" >&2
  exit 1
fi

# Scan tasks for PR numbers
for task_file in "$TASK_DIR"/*.json; do
  [[ -f "$task_file" ]] || continue

  TASK_INFO=$(python3 -c "
import json, re, sys
with open('$task_file') as f:
    task = json.load(f)
desc = task.get('description', '')
m = re.search(r'pr_number=(\d+)', desc)
if m:
    print(json.dumps({
        'task_id': task.get('id', ''),
        'subject': task.get('subject', ''),
        'status': task.get('status', ''),
        'pr_number': int(m.group(1))
    }))
" 2>/dev/null) || continue

  [[ -z "$TASK_INFO" ]] && continue

  PR_NUM=$(echo "$TASK_INFO" | python3 -c "import json,sys; print(json.load(sys.stdin)['pr_number'])")
  TASK_ID=$(echo "$TASK_INFO" | python3 -c "import json,sys; print(json.load(sys.stdin)['task_id'])")
  TASK_STATUS=$(echo "$TASK_INFO" | python3 -c "import json,sys; print(json.load(sys.stdin)['status'])")

  # Skip already-completed tasks
  if [[ "$TASK_STATUS" == "completed" ]]; then
    continue
  fi

  # Fetch PR status
  PR_DATA=$(gh pr view "$PR_NUM" --json state,mergedAt,reviewDecision,reviews,isDraft,statusCheckRollup 2>/dev/null) || {
    echo "{\"task_id\": \"$TASK_ID\", \"pr\": $PR_NUM, \"action\": \"error\", \"reason\": \"failed to fetch PR\"}"
    continue
  }

  STATE=$(echo "$PR_DATA" | python3 -c "import json,sys; print(json.load(sys.stdin)['state'])")
  MERGED=$(echo "$PR_DATA" | python3 -c "import json,sys; print(json.load(sys.stdin).get('mergedAt') or '')")
  REVIEW=$(echo "$PR_DATA" | python3 -c "import json,sys; print(json.load(sys.stdin).get('reviewDecision') or 'PENDING')")
  IS_DRAFT=$(echo "$PR_DATA" | python3 -c "import json,sys; print(json.load(sys.stdin).get('isDraft', False))")

  # Determine action
  if [[ -n "$MERGED" ]]; then
    ACTION="complete"
    NOTE="PR #${PR_NUM} merged"
  elif [[ "$STATE" == "CLOSED" ]]; then
    ACTION="complete"
    NOTE="PR #${PR_NUM} closed without merge"
  elif [[ "$REVIEW" == "APPROVED" ]]; then
    ACTION="note"
    NOTE="PR #${PR_NUM} approved, ready to merge"
  elif [[ "$REVIEW" == "CHANGES_REQUESTED" ]]; then
    ACTION="flag"
    NOTE="PR #${PR_NUM} has changes requested"
  elif [[ "$IS_DRAFT" == "True" ]]; then
    ACTION="none"
    NOTE="PR #${PR_NUM} is still a draft"
  else
    ACTION="none"
    NOTE="PR #${PR_NUM} pending review"
  fi

  PREFIX=""
  [[ "$DRY_RUN" == "true" ]] && PREFIX="would_"

  echo "{\"task_id\": \"$TASK_ID\", \"pr\": $PR_NUM, \"action\": \"${PREFIX}${ACTION}\", \"note\": \"$NOTE\"}"
done

echo "Status check complete." >&2
