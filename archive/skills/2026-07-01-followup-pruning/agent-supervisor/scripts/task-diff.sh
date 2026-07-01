#!/usr/bin/env bash
set -euo pipefail

# task-diff.sh — Compare two task list snapshot files
#
# Usage:
#   task-diff.sh <previous.json> <current.json>
#
# Output: Human-readable diff showing new, removed, and changed tasks

usage() {
  cat <<'EOF'
Usage: task-diff.sh <previous.json> <current.json>

Compare two task list snapshot files and report changes.

Snapshot files are JSON arrays of task objects with fields:
  id, subject, status, owner, blockedBy

Output shows:
  + NEW tasks
  - REMOVED tasks
  ~ CHANGED tasks (with field-level diffs)
EOF
}

if [[ $# -lt 2 ]]; then
  usage
  exit 1
fi

PREV="$1"
CURR="$2"

if [[ ! -f "$PREV" ]]; then
  echo "Error: Previous snapshot not found: $PREV" >&2
  exit 1
fi

if [[ ! -f "$CURR" ]]; then
  echo "Error: Current snapshot not found: $CURR" >&2
  exit 1
fi

python3 -c "
import json, sys

with open('$PREV') as f:
    prev_tasks = {t['id']: t for t in json.load(f)}
with open('$CURR') as f:
    curr_tasks = {t['id']: t for t in json.load(f)}

changes = []
new_count = 0
removed_count = 0
changed_count = 0

# New tasks
for tid, task in sorted(curr_tasks.items()):
    if tid not in prev_tasks:
        new_count += 1
        print(f\"+ NEW: #{tid} [{task.get('status','')}] {task.get('subject','')}\")
        if task.get('owner'):
            print(f\"  Owner: {task['owner']}\")

# Removed tasks
for tid, task in sorted(prev_tasks.items()):
    if tid not in curr_tasks:
        removed_count += 1
        print(f\"- REMOVED: #{tid} {task.get('subject','')}\")

# Changed tasks
for tid in sorted(set(prev_tasks) & set(curr_tasks)):
    prev = prev_tasks[tid]
    curr = curr_tasks[tid]
    diffs = []
    for key in ['status', 'owner', 'subject']:
        pv = prev.get(key, '')
        cv = curr.get(key, '')
        if pv != cv:
            diffs.append(f\"{key}: '{pv}' -> '{cv}'\")

    # Check blockedBy changes
    prev_blocked = set(prev.get('blockedBy', []))
    curr_blocked = set(curr.get('blockedBy', []))
    if prev_blocked != curr_blocked:
        added = curr_blocked - prev_blocked
        removed = prev_blocked - curr_blocked
        parts = []
        if added: parts.append(f\"added blocks: {added}\")
        if removed: parts.append(f\"removed blocks: {removed}\")
        diffs.append(f\"blockedBy: {', '.join(parts)}\")

    if diffs:
        changed_count += 1
        print(f\"~ CHANGED: #{tid} {curr.get('subject','')}\")
        for d in diffs:
            print(f\"  {d}\")

print(f\"\n--- Summary: {new_count} new, {removed_count} removed, {changed_count} changed ---\")
"
