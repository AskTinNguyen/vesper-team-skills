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
BUN_BIN="${VESPER_BUN_BIN:-bun}"
JSON_HELPER="$(cd "$(dirname "$0")" && pwd)/json.ts"
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

if ! command -v "$BUN_BIN" &>/dev/null; then
  echo "Error: Bun runtime not found. Expected VESPER_BUN_BIN or bun on PATH." >&2
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

ISSUE_COUNT=$(echo "$ISSUES" | "$BUN_BIN" "$JSON_HELPER" count)
echo "Found $ISSUE_COUNT open issues" >&2

# Collect existing issue numbers from task descriptions
existing_issue_numbers() {
  if [[ -d "$TASK_DIR" ]]; then
    for f in "$TASK_DIR"/*.json; do
      [[ -f "$f" ]] || continue
      "$BUN_BIN" "$JSON_HELPER" task-metadata "$f" issue_number 2>/dev/null
    done
  fi
}

EXISTING=$(existing_issue_numbers | sort -u)

# Process each issue
echo "$ISSUES" | "$BUN_BIN" "$JSON_HELPER" jsonl | while IFS= read -r issue_json; do
  NUMBER=$(echo "$issue_json" | "$BUN_BIN" "$JSON_HELPER" field number)
  TITLE=$(echo "$issue_json" | "$BUN_BIN" "$JSON_HELPER" field title)
  AUTHOR_LOGIN=$(echo "$issue_json" | "$BUN_BIN" "$JSON_HELPER" field author.login)
  URL=$(echo "$issue_json" | "$BUN_BIN" "$JSON_HELPER" field url)
  BODY=$(echo "$issue_json" | "$BUN_BIN" "$JSON_HELPER" field body)
  LABELS=$(echo "$issue_json" | "$BUN_BIN" "$JSON_HELPER" join labels name ', ' none)
  MILESTONE_NAME=$(echo "$issue_json" | "$BUN_BIN" "$JSON_HELPER" field milestone.title none)
  ASSIGNEES=$(echo "$issue_json" | "$BUN_BIN" "$JSON_HELPER" join assignees login ', @' unassigned)
  if [[ "$ASSIGNEES" != "unassigned" ]]; then
    ASSIGNEES="@${ASSIGNEES}"
  fi

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
    echo "{\"issue\": $NUMBER, \"action\": \"create\", \"subject\": \"Issue #${NUMBER}: ${TITLE}\", \"description\": $(echo "$DESCRIPTION" | "$BUN_BIN" "$JSON_HELPER" stringify-stdin), \"activeForm\": \"Working on issue #${NUMBER}\"}"
  fi
done

echo "Sync complete." >&2
