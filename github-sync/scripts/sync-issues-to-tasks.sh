#!/usr/bin/env bash
set -euo pipefail

# sync-issues-to-tasks.sh — Pull open GitHub issues into Claude Code task list
#
# Usage:
#   sync-issues-to-tasks.sh [--label LABEL] [--milestone MILESTONE] [--limit N] [--dry-run]
#
# Requires: gh CLI (authenticated), CLAUDE_CODE_TASK_LIST_ID set
# Output: JSON lines — one object per issue with sync action taken

TASKS_ROOT="${HOME}/.claude/tasks"
LABEL=""
MILESTONE=""
LIMIT=50
DRY_RUN=false

usage() {
  cat <<'EOF'
Usage: sync-issues-to-tasks.sh [OPTIONS]

Pull open GitHub issues into the Claude Code task list.
Deduplicates by issue number — existing tasks are skipped.

Options:
  --label LABEL          Filter issues by label
  --milestone MILESTONE  Filter issues by milestone
  --limit N              Max issues to fetch (default: 50)
  --dry-run              Show what would be created without modifying tasks
  -h, --help             Show this help

Environment:
  CLAUDE_CODE_TASK_LIST_ID  Required. The active task list ID.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --label) LABEL="$2"; shift 2 ;;
    --milestone) MILESTONE="$2"; shift 2 ;;
    --limit) LIMIT="$2"; shift 2 ;;
    --dry-run) DRY_RUN=true; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage; exit 1 ;;
  esac
done

# Validate environment
if ! command -v gh &>/dev/null; then
  echo "Error: gh CLI not found. Install from https://cli.github.com" >&2
  exit 1
fi

if [[ -z "${CLAUDE_CODE_TASK_LIST_ID:-}" ]]; then
  echo "Error: CLAUDE_CODE_TASK_LIST_ID not set. Start Claude with cc <list-name>." >&2
  exit 1
fi

TASK_DIR="${TASKS_ROOT}/${CLAUDE_CODE_TASK_LIST_ID}"

# Build gh command
GH_ARGS=(issue list --json number,title,author,labels,body,url,milestone,assignees --limit "$LIMIT" --state open)
[[ -n "$LABEL" ]] && GH_ARGS+=(--label "$LABEL")
[[ -n "$MILESTONE" ]] && GH_ARGS+=(--milestone "$MILESTONE")

# Fetch issues
ISSUES=$(gh "${GH_ARGS[@]}" 2>/dev/null) || {
  echo "Error: Failed to fetch issues. Check gh auth status." >&2
  exit 1
}

ISSUE_COUNT=$(echo "$ISSUES" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))")
echo "Found $ISSUE_COUNT open issues" >&2

# Collect existing issue numbers from task descriptions
existing_issue_numbers() {
  if [[ -d "$TASK_DIR" ]]; then
    for f in "$TASK_DIR"/*.json; do
      [[ -f "$f" ]] || continue
      python3 -c "
import json, re, sys
with open('$f') as fh:
    task = json.load(fh)
desc = task.get('description', '')
m = re.search(r'issue_number=(\d+)', desc)
if m:
    print(m.group(1))
" 2>/dev/null
    done
  fi
}

EXISTING=$(existing_issue_numbers | sort -u)

# Process each issue
echo "$ISSUES" | python3 -c "
import json, sys

issues = json.load(sys.stdin)
for issue in issues:
    print(json.dumps(issue))
" | while IFS= read -r issue_json; do
  NUMBER=$(echo "$issue_json" | python3 -c "import json,sys; print(json.load(sys.stdin)['number'])")
  TITLE=$(echo "$issue_json" | python3 -c "import json,sys; print(json.load(sys.stdin)['title'])")
  AUTHOR_LOGIN=$(echo "$issue_json" | python3 -c "import json,sys; print(json.load(sys.stdin)['author']['login'])")
  URL=$(echo "$issue_json" | python3 -c "import json,sys; print(json.load(sys.stdin)['url'])")
  BODY=$(echo "$issue_json" | python3 -c "import json,sys; print(json.load(sys.stdin).get('body','') or '')")
  LABELS=$(echo "$issue_json" | python3 -c "import json,sys; print(', '.join(l['name'] for l in json.load(sys.stdin).get('labels',[])) or 'none')")
  MILESTONE_NAME=$(echo "$issue_json" | python3 -c "import json,sys; m=json.load(sys.stdin).get('milestone'); print(m['title'] if m else 'none')")
  ASSIGNEES=$(echo "$issue_json" | python3 -c "import json,sys; print(', '.join('@'+a['login'] for a in json.load(sys.stdin).get('assignees',[])) or 'unassigned')")

  # Check dedup
  if echo "$EXISTING" | grep -qw "$NUMBER"; then
    echo "{\"issue\": $NUMBER, \"action\": \"skipped\", \"reason\": \"already exists\"}"
    continue
  fi

  DESCRIPTION="GitHub Issue: ${URL}
Author: @${AUTHOR_LOGIN}
Labels: ${LABELS}
Milestone: ${MILESTONE_NAME}
Assignees: ${ASSIGNEES}

${BODY}

---
Metadata: issue_number=${NUMBER}"

  if [[ "$DRY_RUN" == "true" ]]; then
    echo "{\"issue\": $NUMBER, \"action\": \"would_create\", \"title\": \"Issue #${NUMBER}: ${TITLE}\"}"
  else
    echo "{\"issue\": $NUMBER, \"action\": \"create\", \"subject\": \"Issue #${NUMBER}: ${TITLE}\", \"description\": $(echo "$DESCRIPTION" | python3 -c "import json,sys; print(json.dumps(sys.stdin.read()))"), \"activeForm\": \"Working on issue #${NUMBER}\"}"
  fi
done

echo "Sync complete." >&2
