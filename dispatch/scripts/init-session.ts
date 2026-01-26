#!/usr/bin/env bun
/**
 * init-session.ts
 *
 * Generate the command to start Claude with task coordination enabled.
 *
 * IMPORTANT: CLAUDE_CODE_TASK_LIST_ID must be set BEFORE starting Claude.
 * Running this script after Claude is already running will NOT enable
 * task coordination - you must restart Claude.
 *
 * Usage:
 *   bun run init-session.ts              # Show command for new session
 *   bun run init-session.ts my-project   # Show command with custom ID
 *   bun run init-session.ts --resume     # Show command to resume recent session
 *   bun run init-session.ts --check      # Check if current session has coordination
 *
 * The preferred approach is to use start-session.sh which does this automatically.
 */

import { readdir, stat, mkdir, writeFile, readFile } from "fs/promises";
import { join } from "path";
import { homedir } from "os";
import { existsSync } from "fs";

const tasksBaseDir = join(homedir(), ".claude", "tasks");
const currentListFile = join(tasksBaseDir, ".current-list-id");
const args = process.argv.slice(2);

async function findMostRecentListWithTasks(): Promise<{ id: string; taskCount: number } | null> {
  try {
    const entries = await readdir(tasksBaseDir, { withFileTypes: true });
    const lists: { id: string; modified: Date; taskCount: number }[] = [];

    for (const entry of entries) {
      if (!entry.isDirectory() || entry.name.startsWith(".")) continue;

      const listPath = join(tasksBaseDir, entry.name);
      const listStat = await stat(listPath);

      let taskCount = 0;
      try {
        const files = await readdir(listPath);
        taskCount = files.filter(f => f.endsWith(".json")).length;
      } catch {}

      lists.push({ id: entry.name, modified: listStat.mtime, taskCount });
    }

    if (lists.length === 0) return null;

    // Sort: prefer lists with tasks, then by recency
    lists.sort((a, b) => {
      if (a.taskCount > 0 && b.taskCount === 0) return -1;
      if (b.taskCount > 0 && a.taskCount === 0) return 1;
      return b.modified.getTime() - a.modified.getTime();
    });

    return { id: lists[0].id, taskCount: lists[0].taskCount };
  } catch {
    return null;
  }
}

// Help
if (args.includes("--help") || args.includes("-h")) {
  console.log(`
init-session.ts - Generate Claude startup command with task coordination

Usage:
  bun run init-session.ts              Show command for new session
  bun run init-session.ts my-project   Show command with custom ID
  bun run init-session.ts --resume     Show command to resume recent session
  bun run init-session.ts --check      Check if current session has coordination

IMPORTANT: CLAUDE_CODE_TASK_LIST_ID must be set BEFORE starting Claude.
This script outputs the command you need to run - it cannot enable
coordination in an already-running Claude session.

Preferred approach: Use start-session.sh instead, which handles everything:
  ~/.claude/skills/dispatch/scripts/start-session.sh my-project

Examples:
  # Generate command for new session
  bun run init-session.ts feature-auth
  # Output: CLAUDE_CODE_TASK_LIST_ID=feature-auth claude

  # Check if current session has coordination
  bun run init-session.ts --check
`);
  process.exit(0);
}

// Check mode - verify if current session has coordination
if (args.includes("--check")) {
  const currentId = process.env.CLAUDE_CODE_TASK_LIST_ID;
  if (currentId) {
    console.log(`✅ Task coordination is enabled`);
    console.log(`   List ID: ${currentId}`);
    console.log(`   Path: ${tasksBaseDir}/${currentId}/`);

    // Count tasks
    try {
      const files = await readdir(join(tasksBaseDir, currentId));
      const taskCount = files.filter(f => f.endsWith(".json")).length;
      console.log(`   Tasks: ${taskCount}`);
    } catch {
      console.log(`   Tasks: 0 (new list)`);
    }
  } else {
    console.log(`❌ Task coordination is NOT enabled`);
    console.log(``);
    console.log(`   CLAUDE_CODE_TASK_LIST_ID is not set.`);
    console.log(`   Tasks will be stored in a session-specific list that`);
    console.log(`   subagents cannot access.`);
    console.log(``);
    console.log(`   To enable coordination, restart Claude with:`);
    console.log(`   CLAUDE_CODE_TASK_LIST_ID=my-project claude`);
    console.log(``);
    console.log(`   Or use the wrapper script:`);
    console.log(`   ~/.claude/skills/dispatch/scripts/start-session.sh`);
  }
  process.exit(currentId ? 0 : 1);
}

await mkdir(tasksBaseDir, { recursive: true });

let listId: string;
const resume = args.includes("--resume") || args.includes("-r");
const explicitId = args.find(a => !a.startsWith("-"));

if (resume) {
  // Resume mode - find existing list
  if (explicitId) {
    listId = explicitId;
    if (!existsSync(join(tasksBaseDir, listId))) {
      console.error(`Error: Task list '${listId}' not found`);
      process.exit(1);
    }
  } else if (existsSync(currentListFile)) {
    listId = (await readFile(currentListFile, "utf-8")).trim();
  } else {
    const recent = await findMostRecentListWithTasks();
    if (recent) {
      listId = recent.id;
    } else {
      console.error(`No existing task lists found.`);
      console.error(`Use without --resume to create a new list.`);
      process.exit(1);
    }
  }
} else if (explicitId) {
  // Explicit ID provided
  listId = explicitId;
} else {
  // Generate new ID
  listId = `session-${Date.now()}`;
}

// Create list directory if needed
await mkdir(join(tasksBaseDir, listId), { recursive: true });

// Update current list file
await writeFile(currentListFile, listId);

// Count tasks
let taskCount = 0;
try {
  const files = await readdir(join(tasksBaseDir, listId));
  taskCount = files.filter(f => f.endsWith(".json")).length;
} catch {}

console.log(``);
console.log(`╔══════════════════════════════════════════════════════════════╗`);
console.log(`║  Task Coordination Setup                                     ║`);
console.log(`╠══════════════════════════════════════════════════════════════╣`);
console.log(`║  List ID: ${listId.padEnd(50)}║`);
console.log(`║  Tasks:   ${String(taskCount).padEnd(50)}║`);
console.log(`╚══════════════════════════════════════════════════════════════╝`);
console.log(``);
console.log(`To start Claude with task coordination, run:`);
console.log(``);
console.log(`  CLAUDE_CODE_TASK_LIST_ID=${listId} claude`);
console.log(``);
console.log(`Or use the wrapper script:`);
console.log(``);
console.log(`  ~/.claude/skills/dispatch/scripts/start-session.sh ${resume ? '--resume ' : ''}${listId}`);
console.log(``);

// If we're inside Claude already, warn that this won't help
if (process.env.CLAUDE_CODE_TASK_LIST_ID) {
  console.log(`Note: Current session already has coordination enabled.`);
  console.log(`      Current list: ${process.env.CLAUDE_CODE_TASK_LIST_ID}`);
} else {
  console.log(`⚠️  You must EXIT this Claude session and restart with the command above.`);
  console.log(`   Running this script inside Claude does NOT enable coordination.`);
}
console.log(``);
