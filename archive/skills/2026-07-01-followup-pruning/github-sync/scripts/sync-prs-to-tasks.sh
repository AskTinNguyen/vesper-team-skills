#!/usr/bin/env bash
set -euo pipefail

# sync-prs-to-tasks.sh — Pull open GitHub PRs into Claude Code task list
#
# Usage:
#   sync-prs-to-tasks.sh [--label LABEL] [--author AUTHOR] [--limit N] [--dry-run]
#
# Requires: gh CLI (authenticated), CLAUDE_CODE_TASK_LIST_ID set
# Output: JSON lines — one object per PR with sync action taken

TASKS_ROOT="${HOME}/.claude/tasks"
BUN_BIN="${VESPER_BUN_BIN:-bun}"
JSON_HELPER="$(cd "$(dirname "$0")" && pwd)/json.ts"
LABEL=""
AUTHOR=""
LIMIT=50
DRY_RUN=false

usage() {
  cat <<'EOF'
Usage: sync-prs-to-tasks.sh [OPTIONS]

Pull open GitHub PRs into the Claude Code task list.
Deduplicates by PR number — existing tasks are skipped.

Options:
  --label LABEL    Filter PRs by label
  --author AUTHOR  Filter PRs by author (e.g. "@me", "username")
  --limit N        Max PRs to fetch (default: 50)
  --dry-run        Show what would be created without modifying tasks
  -h, --help       Show this help

Environment:
  CLAUDE_CODE_TASK_LIST_ID  Required. The active task list ID.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --label) LABEL="$2"; shift 2 ;;
    --author) AUTHOR="$2"; shift 2 ;;
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
GH_ARGS=(pr list --json number,title,author,headRefName,baseRefName,labels,body,url,isDraft,reviewDecision --limit "$LIMIT" --state open)
[[ -n "$LABEL" ]] && GH_ARGS+=(--label "$LABEL")
[[ -n "$AUTHOR" ]] && GH_ARGS+=(--author "$AUTHOR")

# Fetch PRs
PRS=$(gh "${GH_ARGS[@]}" 2>/dev/null) || {
  echo "Error: Failed to fetch PRs. Check gh auth status." >&2
  exit 1
}

PR_COUNT=$(echo "$PRS" | "$BUN_BIN" "$JSON_HELPER" count)
echo "Found $PR_COUNT open PRs" >&2

# Collect existing PR numbers from task descriptions
existing_pr_numbers() {
  if [[ -d "$TASK_DIR" ]]; then
    for f in "$TASK_DIR"/*.json; do
      [[ -f "$f" ]] || continue
      "$BUN_BIN" "$JSON_HELPER" task-metadata "$f" pr_number 2>/dev/null
    done
  fi
}

EXISTING=$(existing_pr_numbers | sort -u)

# Process each PR
echo "$PRS" | "$BUN_BIN" "$JSON_HELPER" jsonl | while IFS= read -r pr_json; do
  NUMBER=$(echo "$pr_json" | "$BUN_BIN" "$JSON_HELPER" field number)
  TITLE=$(echo "$pr_json" | "$BUN_BIN" "$JSON_HELPER" field title)
  AUTHOR_LOGIN=$(echo "$pr_json" | "$BUN_BIN" "$JSON_HELPER" field author.login)
  HEAD=$(echo "$pr_json" | "$BUN_BIN" "$JSON_HELPER" field headRefName)
  BASE=$(echo "$pr_json" | "$BUN_BIN" "$JSON_HELPER" field baseRefName)
  URL=$(echo "$pr_json" | "$BUN_BIN" "$JSON_HELPER" field url)
  BODY=$(echo "$pr_json" | "$BUN_BIN" "$JSON_HELPER" field body)
  IS_DRAFT=$(echo "$pr_json" | "$BUN_BIN" "$JSON_HELPER" field isDraft false)
  LABELS=$(echo "$pr_json" | "$BUN_BIN" "$JSON_HELPER" join labels name ', ' none)
  REVIEW=$(echo "$pr_json" | "$BUN_BIN" "$JSON_HELPER" field reviewDecision pending)

  # Check dedup
  if echo "$EXISTING" | grep -qw "$NUMBER"; then
    echo "{\"pr\": $NUMBER, \"action\": \"skipped\", \"reason\": \"already exists\"}"
    continue
  fi

  DESCRIPTION="GitHub PR: ${URL}
Author: @${AUTHOR_LOGIN}
Branch: ${HEAD} -> ${BASE}
Labels: ${LABELS}
Review: ${REVIEW}
Draft: ${IS_DRAFT}

${BODY}

---
Metadata: pr_number=${NUMBER}"

  if [[ "$DRY_RUN" == "true" ]]; then
    echo "{\"pr\": $NUMBER, \"action\": \"would_create\", \"title\": \"PR #${NUMBER}: ${TITLE}\"}"
  else
    # Output task creation instruction for the calling agent
    echo "{\"pr\": $NUMBER, \"action\": \"create\", \"subject\": \"PR #${NUMBER}: ${TITLE}\", \"description\": $(echo "$DESCRIPTION" | "$BUN_BIN" "$JSON_HELPER" stringify-stdin), \"activeForm\": \"Reviewing PR #${NUMBER}\"}"
  fi
done

echo "Sync complete." >&2
