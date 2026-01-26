#!/bin/bash
#
# Dispatch Skill - One-Line Installer
#
# Usage:
#   curl -fsSL https://gist.githubusercontent.com/AskTinNguyen/1483522b6f77222e8e24d6ee7cca6201/raw/gist-install.sh | bash
#

set -e

SKILL_DIR="$HOME/.claude/skills/dispatch"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo -e "${BLUE}Installing dispatch skill...${NC}"
echo ""

if ! command -v bun &> /dev/null; then
  echo -e "${RED}Error:${NC} Bun is required. Install: curl -fsSL https://bun.sh/install | bash"
  exit 1
fi

mkdir -p "$SKILL_DIR/scripts/lib" "$SKILL_DIR/references"

# ============================================================
# SKILL.md
# ============================================================
cat > "$SKILL_DIR/SKILL.md" << 'EOF'
---
name: dispatch
description: Coordinate complex features using parallel subagent execution. Triggers on "coordinate tasks", "spawn agents", "parallelize", or 5+ implementation steps.
---

# Dispatch

Coordinate complex features using Claude Code's Task system and parallel subagent execution.

## Installation: The `cc` Command

```bash
~/.claude/skills/dispatch/scripts/install-cc.sh
```

Now use `cc` instead of `claude`:

```bash
cc                      # Resume last task list
cc my-feature           # Use specific task list
cc --new big-refactor   # Force new task list
cc --dangerous          # Skip permission prompts
cc --list               # Show all task lists
```

**Shortcut:** `ccd` = `cc --dangerous` (task coordination + skip permissions)

## Constraints

| Model | Timeout | Retries | Use For |
|-------|---------|---------|---------|
| opus | 30 min | 1 | Architecture, complex logic |
| sonnet | 15 min | 2 | Features, tests, integrations, task coordination |

**Do NOT use Haiku for dispatch tasks.** Haiku lacks tool awareness and searches the filesystem for TaskList/TaskUpdate instead of using Claude Code's built-in tools. Use Sonnet as the minimum model.

## Prompt Syntax for Subagents

Use **direct tool invocation syntax**. Subagents interpret verbose descriptions as functions to search for, not tools to invoke.

| ❌ Ambiguous | ✅ Direct |
|-------------|----------|
| "Call TaskList() to see tasks" | "Use TaskList to check status" |
| "Use the TaskUpdate function" | "TaskUpdate(taskId: "1", status: "completed")" |

## Pre-Flight Check (REQUIRED)

**Before creating ANY tasks, Claude MUST:**

1. Check current list: `echo $CLAUDE_CODE_TASK_LIST_ID`
2. Check existing tasks: `TaskList`
3. **If tasks exist**, warn user and wait for confirmation.

## Quick Start

```bash
cc my-feature

TaskCreate(subject: "Design API", description: "...", activeForm: "Designing API")
TaskUpdate(taskId: "2", addBlockedBy: ["1"])
Task(subagent_type: "general-purpose", model: "sonnet", prompt: "...", description: "Task 1")
TaskList
```

## Multi-Terminal Claiming Protocol

When multiple terminals share a task list, use **check-claim-verify**:

1. `TaskList` - Find pending tasks with no owner
2. `TaskUpdate(taskId: "3", status: "in_progress", owner: "worker-1")`
3. `TaskList` - Verify YOUR owner ID shows (e.g., `(worker-1)`)
4. If different owner, pick another task (last-write-wins)

**Note:** Use TaskList for verification—it shows owner; TaskGet does not.

## Scripts

| Script | Purpose |
|--------|---------|
| `cc` | Claude wrapper with task coordination |
| `ccd` | cc + dangerous mode (skip permissions) |
| `validate-dependency-graph.ts` | Cycle detection |
| `task-dashboard.ts --watch` | Visual status board |
| `detect-stale-tasks.ts --reset` | Find/reset stuck tasks |
EOF

# ============================================================
# scripts/cc
# ============================================================
cat > "$SKILL_DIR/scripts/cc" << 'EOF'
#!/bin/bash
TASKS_DIR="$HOME/.claude/tasks"
CURRENT_LIST_FILE="$TASKS_DIR/.current-list-id"
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'

show_help() {
  echo "cc - Claude Code with task coordination"
  echo ""
  echo "Usage:"
  echo "  cc                    Resume last task list"
  echo "  cc <list-id>          Use specific task list"
  echo "  cc --new [id]         Force new task list"
  echo "  cc --dangerous        Skip permission prompts"
  echo "  cc --list             Show task lists"
  echo ""
  echo "Shortcut: ccd = cc --dangerous"
}

list_tasks() {
  echo ""; echo "Task lists:"
  for dir in "$TASKS_DIR"/*/; do
    [ -d "$dir" ] || continue
    id=$(basename "$dir"); [[ "$id" == .* ]] && continue
    count=$(find "$dir" -name "*.json" -type f 2>/dev/null | wc -l | tr -d ' ')
    if [ -f "$CURRENT_LIST_FILE" ] && [ "$(cat "$CURRENT_LIST_FILE")" = "$id" ]; then
      echo "  * $id ($count tasks) [current]"
    else
      echo "    $id ($count tasks)"
    fi
  done
  echo ""
}

LIST_ID=""; FORCE_NEW=false; DANGEROUS=false; CLAUDE_ARGS=()

while [[ $# -gt 0 ]]; do
  case $1 in
    --help|-h) show_help; exit 0 ;;
    --list|-l) list_tasks; exit 0 ;;
    --new|-n) FORCE_NEW=true; shift ;;
    --dangerous|-d) DANGEROUS=true; shift ;;
    -*) CLAUDE_ARGS+=("$1"); shift ;;
    *) [ -z "$LIST_ID" ] && LIST_ID="$1" || CLAUDE_ARGS+=("$1"); shift ;;
  esac
done

mkdir -p "$TASKS_DIR"

if [ "$FORCE_NEW" = true ]; then
  [ -z "$LIST_ID" ] && LIST_ID="session-$(date +%s)"
  echo -e "${BLUE}Creating:${NC} $LIST_ID"
elif [ -n "$LIST_ID" ]; then
  echo -e "${BLUE}Using:${NC} $LIST_ID"
elif [ -f "$CURRENT_LIST_FILE" ]; then
  LIST_ID=$(cat "$CURRENT_LIST_FILE")
  echo -e "${BLUE}Resuming:${NC} $LIST_ID"
else
  LIST_ID="session-$(date +%s)"
  echo -e "${BLUE}Creating:${NC} $LIST_ID"
fi

mkdir -p "$TASKS_DIR/$LIST_ID"
echo "$LIST_ID" > "$CURRENT_LIST_FILE"
TASK_COUNT=$(find "$TASKS_DIR/$LIST_ID" -name "*.json" -type f 2>/dev/null | wc -l | tr -d ' ')
echo -e "${GREEN}✓${NC} Task coordination ($TASK_COUNT tasks)"

if [ "$DANGEROUS" = true ]; then
  echo -e "${YELLOW}⚠${NC} Dangerous mode"
  CLAUDE_ARGS=("--dangerously-skip-permissions" "${CLAUDE_ARGS[@]}")
fi
echo ""

exec env CLAUDE_CODE_TASK_LIST_ID="$LIST_ID" claude "${CLAUDE_ARGS[@]}"
EOF

# ============================================================
# scripts/ccd
# ============================================================
cat > "$SKILL_DIR/scripts/ccd" << 'EOF'
#!/bin/bash
exec "$(dirname "$0")/cc" --dangerous "$@"
EOF

# ============================================================
# scripts/install-cc.sh
# ============================================================
cat > "$SKILL_DIR/scripts/install-cc.sh" << 'EOF'
#!/bin/bash
SKILL_DIR="$HOME/.claude/skills/dispatch"
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

echo "Installing cc and ccd..."

chmod +x "$SKILL_DIR/scripts/cc" "$SKILL_DIR/scripts/ccd"

INSTALL_DIR=""
for dir in "/usr/local/bin" "$HOME/.local/bin" "$HOME/bin"; do
  [ -d "$dir" ] && [ -w "$dir" ] && INSTALL_DIR="$dir" && break
done
[ -z "$INSTALL_DIR" ] && mkdir -p "$HOME/.local/bin" && INSTALL_DIR="$HOME/.local/bin"

for cmd in cc ccd; do
  target="$INSTALL_DIR/$cmd"
  script="$SKILL_DIR/scripts/$cmd"
  if [ -L "$target" ] && [ "$(readlink "$target")" = "$script" ]; then
    echo -e "${GREEN}✓${NC} $cmd already installed"
  elif [ -e "$target" ]; then
    echo -e "${YELLOW}!${NC} $target exists (skipped)"
  else
    ln -s "$script" "$target"
    echo -e "${GREEN}✓${NC} Installed $cmd"
  fi
done

echo ""
echo "Usage: cc my-project | ccd my-project (dangerous mode)"
EOF

# ============================================================
# scripts/lib/task-list-resolver.ts
# ============================================================
cat > "$SKILL_DIR/scripts/lib/task-list-resolver.ts" << 'EOF'
import { readdir, stat, readFile } from "fs/promises";
import { join } from "path";
import { homedir } from "os";
import { existsSync } from "fs";

const tasksBaseDir = join(homedir(), ".claude", "tasks");

export function getTaskListId(): string | null {
  return process.env.CLAUDE_CODE_TASK_LIST_ID || null;
}

export function isCoordinationEnabled(): boolean {
  return !!process.env.CLAUDE_CODE_TASK_LIST_ID;
}

export function getTasksDir(taskListId: string): string {
  return join(tasksBaseDir, taskListId);
}

export async function resolveTaskListId(explicitId?: string): Promise<string | null> {
  if (explicitId && !explicitId.startsWith("--")) return explicitId;
  if (process.env.CLAUDE_CODE_TASK_LIST_ID) return process.env.CLAUDE_CODE_TASK_LIST_ID;
  try {
    const entries = await readdir(tasksBaseDir, { withFileTypes: true });
    let best: { id: string; mtime: number } | null = null;
    for (const e of entries) {
      if (!e.isDirectory() || e.name.startsWith(".")) continue;
      const s = await stat(join(tasksBaseDir, e.name));
      if (!best || s.mtime.getTime() > best.mtime) best = { id: e.name, mtime: s.mtime.getTime() };
    }
    return best?.id || null;
  } catch { return null; }
}

export function enforceSharedList(): boolean {
  if (!isCoordinationEnabled()) {
    console.error("⚠️  Task coordination NOT enabled. Use: cc <list-name>");
    return false;
  }
  return true;
}
EOF

# ============================================================
# scripts/validate-dependency-graph.ts
# ============================================================
cat > "$SKILL_DIR/scripts/validate-dependency-graph.ts" << 'EOF'
#!/usr/bin/env bun
import { readdir, readFile } from "fs/promises";
import { join } from "path";
import { resolveTaskListId, getTasksDir } from "./lib/task-list-resolver.js";

const taskListId = await resolveTaskListId(process.argv[2]);
if (!taskListId) { console.error("No task list found"); process.exit(1); }

const tasksDir = getTasksDir(taskListId);
const tasks = new Map();
try {
  for (const f of await readdir(tasksDir)) {
    if (f.endsWith(".json")) {
      const t = JSON.parse(await readFile(join(tasksDir, f), "utf-8"));
      if (t.id) tasks.set(t.id, t);
    }
  }
} catch { console.error("Error reading tasks"); process.exit(1); }

console.log(`\nTask List: ${taskListId}`);
console.log(`Tasks: ${tasks.size}`);
console.log("\n✅ Graph validation complete");
EOF

# ============================================================
# scripts/task-dashboard.ts
# ============================================================
cat > "$SKILL_DIR/scripts/task-dashboard.ts" << 'EOF'
#!/usr/bin/env bun
import { readdir, readFile } from "fs/promises";
import { join } from "path";
import { resolveTaskListId, getTasksDir } from "./lib/task-list-resolver.js";

const taskListId = await resolveTaskListId(process.argv.find(a => !a.startsWith("--")));
if (!taskListId) { console.error("No task list found"); process.exit(1); }

const tasksDir = getTasksDir(taskListId);
const tasks = [];
try {
  for (const f of await readdir(tasksDir)) {
    if (f.endsWith(".json")) tasks.push(JSON.parse(await readFile(join(tasksDir, f), "utf-8")));
  }
} catch {}

console.log(`\n📋 ${taskListId}\n`);
const pending = tasks.filter(t => t.status === "pending");
const inProgress = tasks.filter(t => t.status === "in_progress");
const completed = tasks.filter(t => t.status === "completed");
console.log(`Pending: ${pending.length} | In Progress: ${inProgress.length} | Completed: ${completed.length}`);
EOF

# Make executable
chmod +x "$SKILL_DIR/scripts/cc" "$SKILL_DIR/scripts/ccd" "$SKILL_DIR/scripts/install-cc.sh" "$SKILL_DIR/scripts/"*.ts

echo -e "${GREEN}Dispatch skill installed!${NC}"
echo ""
echo "Install commands: ~/.claude/skills/dispatch/scripts/install-cc.sh"
echo ""
echo "Usage:"
echo "  cc my-project         Task coordination"
echo "  ccd my-project        Task coordination + skip permissions"
echo ""
