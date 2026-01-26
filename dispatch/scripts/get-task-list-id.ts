#!/usr/bin/env bun
/**
 * get-task-list-id.ts
 *
 * Discovers the current or most recent task list ID.
 *
 * Priority:
 * 1. CLAUDE_CODE_TASK_LIST_ID environment variable (if set)
 * 2. Most recently modified task list directory
 *
 * Usage:
 *   bun run scripts/get-task-list-id.ts
 *   export CLAUDE_CODE_TASK_LIST_ID=$(bun run scripts/get-task-list-id.ts)
 */

import { readdir, stat } from "fs/promises";
import { join } from "path";
import { homedir } from "os";

interface TaskListInfo {
  id: string;
  path: string;
  modified: Date;
  taskCount: number;
}

async function getTaskListId(): Promise<string | null> {
  // Priority 1: Environment variable
  const envId = process.env.CLAUDE_CODE_TASK_LIST_ID;
  if (envId) {
    console.error(`✅ Using CLAUDE_CODE_TASK_LIST_ID: ${envId}`);
    return envId;
  }

  // Priority 2: Find most recent task list
  const tasksDir = join(homedir(), ".claude", "tasks");

  try {
    const entries = await readdir(tasksDir, { withFileTypes: true });
    const taskLists: TaskListInfo[] = [];

    for (const entry of entries) {
      if (!entry.isDirectory()) continue;

      const listPath = join(tasksDir, entry.name);
      const listStat = await stat(listPath);

      // Count JSON files (tasks)
      let taskCount = 0;
      try {
        const files = await readdir(listPath);
        taskCount = files.filter(f => f.endsWith(".json")).length;
      } catch {
        // Skip if can't read
      }

      taskLists.push({
        id: entry.name,
        path: listPath,
        modified: listStat.mtime,
        taskCount,
      });
    }

    if (taskLists.length === 0) {
      console.error("❌ No task lists found in ~/.claude/tasks/");
      return null;
    }

    // Sort by modification time (most recent first)
    taskLists.sort((a, b) => b.modified.getTime() - a.modified.getTime());

    // Return most recent with tasks, or just most recent
    const withTasks = taskLists.filter(t => t.taskCount > 0);
    const best = withTasks.length > 0 ? withTasks[0] : taskLists[0];

    console.error(`📋 Found ${taskLists.length} task list(s)`);
    console.error(`✅ Using most recent: ${best.id}`);
    console.error(`   Modified: ${best.modified.toLocaleString()}`);
    console.error(`   Tasks: ${best.taskCount}`);

    return best.id;
  } catch (error) {
    console.error(`❌ Error reading tasks directory: ${error}`);
    return null;
  }
}

async function listAllTaskLists(): Promise<void> {
  const tasksDir = join(homedir(), ".claude", "tasks");

  try {
    const entries = await readdir(tasksDir, { withFileTypes: true });
    const taskLists: TaskListInfo[] = [];

    for (const entry of entries) {
      if (!entry.isDirectory()) continue;

      const listPath = join(tasksDir, entry.name);
      const listStat = await stat(listPath);

      let taskCount = 0;
      try {
        const files = await readdir(listPath);
        taskCount = files.filter(f => f.endsWith(".json")).length;
      } catch {}

      taskLists.push({
        id: entry.name,
        path: listPath,
        modified: listStat.mtime,
        taskCount,
      });
    }

    taskLists.sort((a, b) => b.modified.getTime() - a.modified.getTime());

    console.error("\n📋 Available Task Lists:\n");
    for (const list of taskLists) {
      const age = getRelativeTime(list.modified);
      console.error(`   ${list.id}`);
      console.error(`      Tasks: ${list.taskCount}, Modified: ${age}`);
    }
    console.error("");
  } catch {
    console.error("❌ Could not list task lists");
  }
}

function getRelativeTime(date: Date): string {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMins < 1) return "just now";
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  return `${diffDays}d ago`;
}

// Main
const args = process.argv.slice(2);

if (args.includes("--list") || args.includes("-l")) {
  await listAllTaskLists();
  process.exit(0);
}

if (args.includes("--help") || args.includes("-h")) {
  console.error(`
Usage: get-task-list-id.ts [options]

Discovers the current task list ID for multi-session coordination.

Options:
  --list, -l    List all available task lists
  --help, -h    Show this help

Environment:
  CLAUDE_CODE_TASK_LIST_ID    If set, this value is used directly

Examples:
  # Get current task list ID
  bun run scripts/get-task-list-id.ts

  # Set for current session
  export CLAUDE_CODE_TASK_LIST_ID=$(bun run scripts/get-task-list-id.ts)

  # List all task lists
  bun run scripts/get-task-list-id.ts --list
`);
  process.exit(0);
}

const taskListId = await getTaskListId();

if (taskListId) {
  // Output only the ID to stdout (for capture)
  console.log(taskListId);
  process.exit(0);
} else {
  process.exit(1);
}
