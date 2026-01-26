#!/bin/bash
#
# start-session.sh - Start Claude Code with shared task list coordination
#
# This is the CORRECT way to enable multi-agent task coordination.
# The CLAUDE_CODE_TASK_LIST_ID must be set BEFORE starting Claude.
#
# Usage:
#   ./start-session.sh                    # New session with auto-generated ID
#   ./start-session.sh my-project         # New session with custom ID
#   ./start-session.sh --resume           # Resume most recent session
#   ./start-session.sh --resume my-proj   # Resume specific session
#
# Examples:
#   ./start-session.sh feature-auth       # Start working on auth feature
#   ./start-session.sh --resume           # Continue previous work
#

set -e

TASKS_DIR="$HOME/.claude/tasks"
CURRENT_LIST_FILE="$TASKS_DIR/.current-list-id"

# Parse arguments
RESUME=false
LIST_ID=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --resume|-r)
      RESUME=true
      shift
      ;;
    --help|-h)
      echo "Usage: start-session.sh [OPTIONS] [LIST_ID]"
      echo ""
      echo "Start Claude Code with multi-agent task coordination enabled."
      echo ""
      echo "Options:"
      echo "  --resume, -r    Resume the most recent or specified task list"
      echo "  --help, -h      Show this help message"
      echo ""
      echo "Arguments:"
      echo "  LIST_ID         Custom task list ID (default: auto-generated)"
      echo ""
      echo "Examples:"
      echo "  start-session.sh                    # New session"
      echo "  start-session.sh my-feature         # New session with ID 'my-feature'"
      echo "  start-session.sh --resume           # Resume most recent"
      echo "  start-session.sh --resume my-feat   # Resume 'my-feat' session"
      exit 0
      ;;
    *)
      LIST_ID="$1"
      shift
      ;;
  esac
done

# Ensure tasks directory exists
mkdir -p "$TASKS_DIR"

# Determine the list ID to use
if [ "$RESUME" = true ]; then
  if [ -n "$LIST_ID" ]; then
    # Resume specific list
    if [ ! -d "$TASKS_DIR/$LIST_ID" ]; then
      echo "Error: Task list '$LIST_ID' not found"
      echo "Available lists:"
      ls -1 "$TASKS_DIR" | grep -v '^\.' | head -10
      exit 1
    fi
  elif [ -f "$CURRENT_LIST_FILE" ]; then
    # Resume from .current-list-id
    LIST_ID=$(cat "$CURRENT_LIST_FILE")
    echo "Resuming task list: $LIST_ID"
  else
    # Find most recent list with tasks
    LIST_ID=$(find "$TASKS_DIR" -maxdepth 2 -name "*.json" -type f 2>/dev/null | \
              xargs -I{} dirname {} 2>/dev/null | \
              xargs -I{} stat -f "%m %N" {} 2>/dev/null | \
              sort -rn | head -1 | awk '{print $2}' | xargs basename 2>/dev/null)

    if [ -z "$LIST_ID" ]; then
      echo "No existing task lists found. Starting fresh."
      LIST_ID="session-$(date +%s)"
    else
      echo "Resuming most recent task list: $LIST_ID"
    fi
  fi
else
  # New session
  if [ -z "$LIST_ID" ]; then
    LIST_ID="session-$(date +%s)"
  fi
fi

# Create the task list directory
mkdir -p "$TASKS_DIR/$LIST_ID"

# Update current list file
echo "$LIST_ID" > "$CURRENT_LIST_FILE"

# Count existing tasks
TASK_COUNT=$(find "$TASKS_DIR/$LIST_ID" -name "*.json" -type f 2>/dev/null | wc -l | tr -d ' ')

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  Task Coordination Enabled                                   ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║  List ID: $(printf '%-50s' "$LIST_ID")║"
echo "║  Tasks:   $(printf '%-50s' "$TASK_COUNT")║"
echo "║  Path:    ~/.claude/tasks/$LIST_ID/"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Start Claude with the environment variable
exec env CLAUDE_CODE_TASK_LIST_ID="$LIST_ID" claude "$@"
