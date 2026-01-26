/**
 * Shared utility to resolve task list ID.
 *
 * The task list ID is determined by CLAUDE_CODE_TASK_LIST_ID environment
 * variable, which must be set BEFORE starting Claude.
 *
 * If not set, Claude uses the session ID, which means subagents will
 * have isolated task lists and coordination will fail.
 */

import { readdir, stat, readFile } from "fs/promises";
import { join } from "path";
import { homedir } from "os";
import { existsSync } from "fs";

const tasksBaseDir = join(homedir(), ".claude", "tasks");
const currentListFile = join(tasksBaseDir, ".current-list-id");

/**
 * Get the current task list ID from environment.
 * Returns null if not set (meaning coordination is not enabled).
 */
export function getTaskListId(): string | null {
  return process.env.CLAUDE_CODE_TASK_LIST_ID || null;
}

/**
 * Check if task coordination is enabled.
 */
export function isCoordinationEnabled(): boolean {
  return !!process.env.CLAUDE_CODE_TASK_LIST_ID;
}

/**
 * Get the tasks directory for a specific list ID.
 */
export function getTasksDir(taskListId: string): string {
  return join(tasksBaseDir, taskListId);
}

/**
 * Get the base tasks directory.
 */
export function getTasksBaseDir(): string {
  return tasksBaseDir;
}

/**
 * Get the current list ID from the .current-list-id file.
 * This is useful for resuming sessions.
 */
export async function getCurrentListIdFromFile(): Promise<string | null> {
  if (existsSync(currentListFile)) {
    try {
      return (await readFile(currentListFile, "utf-8")).trim();
    } catch {
      return null;
    }
  }
  return null;
}

/**
 * Find the most recent task list that has tasks.
 * Useful for --resume functionality.
 */
export async function findMostRecentListWithTasks(): Promise<{ id: string; taskCount: number } | null> {
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

/**
 * Print a warning if coordination is not enabled.
 * Call this in scripts that require shared task access.
 */
export function warnIfNotCoordinated(): void {
  if (!isCoordinationEnabled()) {
    console.error("");
    console.error("⚠️  Task coordination is NOT enabled");
    console.error("");
    console.error("   CLAUDE_CODE_TASK_LIST_ID is not set.");
    console.error("   This means subagents will have isolated task lists.");
    console.error("");
    console.error("   To enable coordination, restart Claude with:");
    console.error("   CLAUDE_CODE_TASK_LIST_ID=my-project claude");
    console.error("");
    console.error("   Or use the wrapper script:");
    console.error("   ~/.claude/skills/dispatch/scripts/start-session.sh");
    console.error("");
  }
}

/**
 * Require coordination to be enabled. Exit if not.
 * Use this in scripts that MUST have shared task access.
 */
export function requireCoordination(): string {
  const listId = getTaskListId();
  if (!listId) {
    console.error("");
    console.error("❌ Task coordination is required but not enabled");
    console.error("");
    console.error("   CLAUDE_CODE_TASK_LIST_ID is not set.");
    console.error("   This script requires a shared task list.");
    console.error("");
    console.error("   To enable coordination, restart Claude with:");
    console.error("   CLAUDE_CODE_TASK_LIST_ID=my-project claude");
    console.error("");
    process.exit(1);
  }
  return listId;
}

// Legacy exports for backwards compatibility
// These are deprecated and will be removed in a future version

/** @deprecated Use getTaskListId() instead */
export async function resolveTaskListId(explicitId?: string): Promise<string | null> {
  if (explicitId && !explicitId.startsWith("--")) {
    return explicitId;
  }
  return getTaskListId() || (await findMostRecentListWithTasks())?.id || null;
}

/** @deprecated Use warnIfNotCoordinated() instead */
export function warnIfNoSharedList(): void {
  warnIfNotCoordinated();
}

/** @deprecated Use requireCoordination() instead */
export function enforceSharedList(): boolean {
  if (!isCoordinationEnabled()) {
    warnIfNotCoordinated();
    return false;
  }
  return true;
}

/** @deprecated Use getCurrentListIdFromFile() instead */
export async function getCurrentListId(): Promise<string | null> {
  return getTaskListId() || getCurrentListIdFromFile();
}
