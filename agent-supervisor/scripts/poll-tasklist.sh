#!/usr/bin/env bash
set -euo pipefail

# poll-tasklist.sh — Interval polling with snapshot and diff detection for task list
#
# Usage:
#   poll-tasklist.sh snapshot             Take a snapshot of the current task list
#   poll-tasklist.sh diff                 Compare current state to last snapshot
#   poll-tasklist.sh start [INTERVAL]     Start polling loop (default: 300s / 5min)
#
# Requires: CLAUDE_CODE_TASK_LIST_ID set

TASKS_ROOT="${HOME}/.claude/tasks"
SNAPSHOT_DIR="/tmp/agent-supervisor-snapshots"
mkdir -p "$SNAPSHOT_DIR"

usage() {
  cat <<'EOF'
Usage: poll-tasklist.sh COMMAND [OPTIONS]

Commands:
  snapshot             Save current task list state to a snapshot file
  diff                 Compare current state to the last snapshot
  start [INTERVAL]     Start polling loop (default: 300 seconds)

Snapshots are stored in /tmp/agent-supervisor-snapshots/.

Environment:
  CLAUDE_CODE_TASK_LIST_ID  Required. The active task list ID.
EOF
}

if [[ -z "${CLAUDE_CODE_TASK_LIST_ID:-}" ]]; then
  echo "Error: CLAUDE_CODE_TASK_LIST_ID not set." >&2
  exit 1
fi

TASK_DIR="${TASKS_ROOT}/${CLAUDE_CODE_TASK_LIST_ID}"
LIST_ID="$CLAUDE_CODE_TASK_LIST_ID"

# Take a snapshot of the current task list state as JSON
take_snapshot() {
  local output_file="$1"

  if [[ ! -d "$TASK_DIR" ]]; then
    echo "[]" > "$output_file"
    return
  fi

  python3 -c "
import json, os, glob

task_dir = '$TASK_DIR'
tasks = []
for f in sorted(glob.glob(os.path.join(task_dir, '*.json'))):
    try:
        with open(f) as fh:
            task = json.load(fh)
            tasks.append({
                'id': task.get('id', ''),
                'subject': task.get('subject', ''),
                'status': task.get('status', ''),
                'owner': task.get('owner', ''),
                'blockedBy': task.get('blockedBy', []),
            })
    except (json.JSONDecodeError, IOError):
        pass

print(json.dumps(tasks, indent=2))
" > "$output_file"
}

# Compare two snapshots
compare_snapshots() {
  local prev="$1"
  local curr="$2"

  python3 -c "
import json, sys

with open('$prev') as f:
    prev_tasks = {t['id']: t for t in json.load(f)}
with open('$curr') as f:
    curr_tasks = {t['id']: t for t in json.load(f)}

changes = []

# New tasks
for tid, task in curr_tasks.items():
    if tid not in prev_tasks:
        changes.append({'type': 'new', 'task_id': tid, 'subject': task['subject'], 'status': task['status']})

# Removed tasks
for tid, task in prev_tasks.items():
    if tid not in curr_tasks:
        changes.append({'type': 'removed', 'task_id': tid, 'subject': task['subject']})

# Changed tasks
for tid in set(prev_tasks) & set(curr_tasks):
    prev = prev_tasks[tid]
    curr = curr_tasks[tid]
    diffs = {}
    for key in ['status', 'owner', 'subject']:
        if prev.get(key) != curr.get(key):
            diffs[key] = {'from': prev.get(key, ''), 'to': curr.get(key, '')}
    if diffs:
        changes.append({'type': 'changed', 'task_id': tid, 'subject': curr['subject'], 'changes': diffs})

if not changes:
    print('No changes detected.')
else:
    for c in changes:
        if c['type'] == 'new':
            print(f\"+ NEW: #{c['task_id']} [{c['status']}] {c['subject']}\")
        elif c['type'] == 'removed':
            print(f\"- REMOVED: #{c['task_id']} {c['subject']}\")
        elif c['type'] == 'changed':
            parts = []
            for k, v in c['changes'].items():
                parts.append(f\"{k}: {v['from']} -> {v['to']}\")
            print(f\"~ CHANGED: #{c['task_id']} {c['subject']} ({', '.join(parts)})\")
    print(f\"\nTotal changes: {len(changes)}\")
"
}

COMMAND="${1:-}"
shift || true

case "$COMMAND" in
  snapshot)
    SNAPSHOT_FILE="${SNAPSHOT_DIR}/${LIST_ID}-$(date +%Y%m%d-%H%M%S).json"
    take_snapshot "$SNAPSHOT_FILE"
    # Also save as "latest" for easy diff
    cp "$SNAPSHOT_FILE" "${SNAPSHOT_DIR}/${LIST_ID}-latest.json"
    echo "Snapshot saved: $SNAPSHOT_FILE"
    ;;

  diff)
    LATEST="${SNAPSHOT_DIR}/${LIST_ID}-latest.json"
    if [[ ! -f "$LATEST" ]]; then
      echo "No previous snapshot found. Run 'poll-tasklist.sh snapshot' first." >&2
      exit 1
    fi
    CURRENT=$(mktemp "${SNAPSHOT_DIR}/current-XXXXXX.json")
    take_snapshot "$CURRENT"
    compare_snapshots "$LATEST" "$CURRENT"
    rm -f "$CURRENT"
    ;;

  start)
    INTERVAL="${1:-300}"
    echo "Starting poll loop (interval: ${INTERVAL}s, list: $LIST_ID)" >&2
    CYCLE=0
    while true; do
      CYCLE=$((CYCLE + 1))
      echo "" >&2
      echo "=== Poll Cycle $CYCLE ($(date +%H:%M:%S)) ===" >&2

      # Take current snapshot
      CURRENT="${SNAPSHOT_DIR}/${LIST_ID}-current.json"
      take_snapshot "$CURRENT"

      # Diff against previous
      LATEST="${SNAPSHOT_DIR}/${LIST_ID}-latest.json"
      if [[ -f "$LATEST" ]]; then
        compare_snapshots "$LATEST" "$CURRENT"
      else
        echo "First cycle — no previous snapshot to compare."
      fi

      # Rotate current to latest
      cp "$CURRENT" "$LATEST"

      # Summary
      python3 -c "
import json
with open('$CURRENT') as f:
    tasks = json.load(f)
by_status = {}
for t in tasks:
    s = t.get('status', 'unknown')
    by_status[s] = by_status.get(s, 0) + 1
parts = [f'{s}: {c}' for s, c in sorted(by_status.items())]
print(f\"Summary: {', '.join(parts)} (total: {len(tasks)})\")
"

      echo "Next poll in ${INTERVAL}s..." >&2
      sleep "$INTERVAL"
    done
    ;;

  -h|--help|help)
    usage
    ;;

  *)
    echo "Unknown command: $COMMAND" >&2
    usage
    exit 1
    ;;
esac
