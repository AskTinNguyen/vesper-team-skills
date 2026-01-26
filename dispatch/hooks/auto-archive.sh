#!/bin/bash
#
# auto-archive.sh - Stop hook to archive tasks when session ends
#
# This hook runs asynchronously when a Claude Code session ends,
# preserving tasks as historical logs before cleanup.
#
# Install: Add to ~/.claude/settings.json hooks.Stop
#

TASKS_DIR="$HOME/.claude/tasks"
ARCHIVE_DIR="$HOME/.claude/tasks-archive"
LOG_FILE="$ARCHIVE_DIR/.archive.log"

# Get task list ID from environment (set by cc wrapper)
LIST_ID="${CLAUDE_CODE_TASK_LIST_ID:-}"

# Exit if no task list is set
if [ -z "$LIST_ID" ]; then
  exit 0
fi

LIST_DIR="$TASKS_DIR/$LIST_ID"

# Exit if list directory doesn't exist
if [ ! -d "$LIST_DIR" ]; then
  exit 0
fi

# Count tasks
TASK_COUNT=$(find "$LIST_DIR" -maxdepth 1 -name "*.json" -type f 2>/dev/null | wc -l | tr -d ' ')

# Exit if no tasks to archive
if [ "$TASK_COUNT" -eq 0 ]; then
  exit 0
fi

# Create archive directory
mkdir -p "$ARCHIVE_DIR"

# Create archive with timestamp
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
ARCHIVE_NAME="${LIST_ID}-${TIMESTAMP}"
ARCHIVE_PATH="$ARCHIVE_DIR/$ARCHIVE_NAME"

mkdir -p "$ARCHIVE_PATH"

# Copy all task files
cp "$LIST_DIR"/*.json "$ARCHIVE_PATH/" 2>/dev/null

# Count task statuses
COMPLETED=$(grep -l '"status":\s*"completed"' "$LIST_DIR"/*.json 2>/dev/null | wc -l | tr -d ' ')
PENDING=$(grep -l '"status":\s*"pending"' "$LIST_DIR"/*.json 2>/dev/null | wc -l | tr -d ' ')
IN_PROGRESS=$(grep -l '"status":\s*"in_progress"' "$LIST_DIR"/*.json 2>/dev/null | wc -l | tr -d ' ')

# Create manifest
cat > "$ARCHIVE_PATH/manifest.json" << EOF
{
  "listId": "$LIST_ID",
  "archivedAt": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "trigger": "stop-hook",
  "taskCount": $TASK_COUNT,
  "completedCount": $COMPLETED,
  "pendingCount": $PENDING,
  "inProgressCount": $IN_PROGRESS
}
EOF

# Log the archive
echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Archived $LIST_ID ($TASK_COUNT tasks) -> $ARCHIVE_NAME" >> "$LOG_FILE"

exit 0
