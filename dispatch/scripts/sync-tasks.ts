#!/usr/bin/env bun
/**
 * sync-tasks.ts
 *
 * Merge tasks from multiple session-scoped lists into a shared list.
 *
 * Use this to consolidate orphaned tasks from multiple Claude sessions
 * that weren't started with CLAUDE_CODE_TASK_LIST_ID.
 *
 * Usage:
 *   bun run sync-tasks.ts --target <list-id>
 *   bun run sync-tasks.ts --target my-project
 *   bun run sync-tasks.ts --target my-project --include session-123,session-456
 *   bun run sync-tasks.ts --list                 # List all task lists
 *   bun run sync-tasks.ts --target my-project --dry-run
 *
 * This will:
 * 1. Find all session-scoped task lists (UUID or session-* format)
 * 2. Merge their tasks into the target list
 * 3. Update task IDs and dependencies to avoid conflicts
 */

import { readdir, readFile, writeFile, mkdir, stat } from "fs/promises";
import { join } from "path";
import { homedir } from "os";
import { existsSync } from "fs";

const tasksBaseDir = join(homedir(), ".claude", "tasks");
const currentListFile = join(tasksBaseDir, ".current-list-id");
const args = process.argv.slice(2);

interface Task {
  id: string;
  subject: string;
  description?: string;
  status: string;
  owner?: string;
  blockedBy?: string[];
  blocks?: string[];
  activeForm?: string;
  metadata?: Record<string, unknown>;
}

interface TaskList {
  id: string;
  taskCount: number;
  modified: Date;
  isSessionScoped: boolean;
}

// Parse arguments
const dryRun = args.includes("--dry-run") || args.includes("-n");
const verbose = args.includes("--verbose") || args.includes("-v");
const listMode = args.includes("--list") || args.includes("-l");

function getArgValue(flag: string): string | null {
  const idx = args.indexOf(flag);
  if (idx !== -1 && idx + 1 < args.length) {
    return args[idx + 1];
  }
  return null;
}

const targetId = getArgValue("--target") || getArgValue("-t");
const includeList = getArgValue("--include")?.split(",").map(s => s.trim());
const excludeList = getArgValue("--exclude")?.split(",").map(s => s.trim());

if (args.includes("--help") || args.includes("-h")) {
  console.log(`
sync-tasks.ts - Merge tasks from multiple lists into one

Usage:
  bun run sync-tasks.ts --target <list-id> [options]
  bun run sync-tasks.ts --list

Options:
  --target, -t <id>     Target list to merge into (required for sync)
  --include <ids>       Only sync from these lists (comma-separated)
  --exclude <ids>       Exclude these lists from sync (comma-separated)
  --list, -l            List all task lists and their counts
  --dry-run, -n         Show what would be done without making changes
  --verbose, -v         Show detailed output
  --help, -h            Show this help message

Examples:
  # List all task lists
  bun run sync-tasks.ts --list

  # Merge all session-scoped lists into my-project
  bun run sync-tasks.ts --target my-project

  # Preview what would be synced
  bun run sync-tasks.ts --target my-project --dry-run

  # Only sync specific lists
  bun run sync-tasks.ts --target my-project --include session-123,abc-def-ghi

  # Exclude certain lists
  bun run sync-tasks.ts --target my-project --exclude docs-inventory

This script finds session-scoped lists (UUID or session-* format) and
merges their tasks into the target shared list.
`);
  process.exit(0);
}

async function getAllTaskLists(): Promise<TaskList[]> {
  const lists: TaskList[] = [];

  try {
    const entries = await readdir(tasksBaseDir, { withFileTypes: true });

    for (const entry of entries) {
      if (!entry.isDirectory() || entry.name.startsWith(".")) continue;

      const listPath = join(tasksBaseDir, entry.name);
      const listStat = await stat(listPath);

      let taskCount = 0;
      try {
        const files = await readdir(listPath);
        taskCount = files.filter(f => f.endsWith(".json")).length;
      } catch {}

      // Session-scoped lists typically have UUID format or session-timestamp format
      const isSessionScoped = !!entry.name.match(/^[a-f0-9-]{36}$/) ||
                              entry.name.startsWith("session-");

      lists.push({
        id: entry.name,
        taskCount,
        modified: listStat.mtime,
        isSessionScoped,
      });
    }
  } catch {}

  // Sort by modification time
  lists.sort((a, b) => b.modified.getTime() - a.modified.getTime());

  return lists;
}

async function loadTasks(listId: string): Promise<Task[]> {
  const listDir = join(tasksBaseDir, listId);
  const tasks: Task[] = [];

  try {
    const files = await readdir(listDir);
    for (const file of files) {
      if (!file.endsWith(".json")) continue;
      try {
        const content = await readFile(join(listDir, file), "utf-8");
        tasks.push(JSON.parse(content));
      } catch {}
    }
  } catch {}

  return tasks;
}

async function getNextTaskId(listId: string): Promise<number> {
  const tasks = await loadTasks(listId);
  if (tasks.length === 0) return 1;

  const maxId = Math.max(...tasks.map(t => parseInt(t.id, 10) || 0));
  return maxId + 1;
}

async function listAllLists(): Promise<void> {
  const lists = await getAllTaskLists();

  if (lists.length === 0) {
    console.log("No task lists found.");
    return;
  }

  console.log("");
  console.log("Task Lists:");
  console.log("═".repeat(80));
  console.log("");

  for (const list of lists) {
    const scope = list.isSessionScoped ? "session" : "shared ";
    const taskLabel = list.taskCount === 1 ? "task" : "tasks";
    const date = list.modified.toISOString().split("T")[0];

    console.log(`  [${scope}] ${list.id}`);
    console.log(`           ${list.taskCount} ${taskLabel}, modified ${date}`);
    console.log("");
  }

  const sessionLists = lists.filter(l => l.isSessionScoped && l.taskCount > 0);
  const totalOrphanedTasks = sessionLists.reduce((sum, l) => sum + l.taskCount, 0);

  if (sessionLists.length > 0) {
    console.log("─".repeat(80));
    console.log(`Found ${sessionLists.length} session-scoped lists with ${totalOrphanedTasks} total tasks.`);
    console.log("");
    console.log("To merge them into a shared list:");
    console.log("  bun run sync-tasks.ts --target my-project");
    console.log("");
  }
}

async function syncTasks(): Promise<void> {
  if (!targetId) {
    console.error("❌ --target is required");
    console.error("   Usage: bun run sync-tasks.ts --target <list-id>");
    process.exit(1);
  }

  const allLists = await getAllTaskLists();

  // Filter source lists
  let sourceLists = allLists.filter(l => {
    // Don't sync target to itself
    if (l.id === targetId) return false;

    // Must have tasks
    if (l.taskCount === 0) return false;

    // Apply include filter
    if (includeList && !includeList.includes(l.id)) return false;

    // Apply exclude filter
    if (excludeList && excludeList.includes(l.id)) return false;

    // Default: only sync session-scoped lists
    if (!includeList && !l.isSessionScoped) return false;

    return true;
  });

  if (sourceLists.length === 0) {
    console.log("No source lists found to sync.");
    console.log("");
    console.log("This script syncs session-scoped lists (UUID or session-* format).");
    console.log("Use --include to specify custom lists to sync.");
    return;
  }

  const totalTasks = sourceLists.reduce((sum, l) => sum + l.taskCount, 0);

  console.log("");
  console.log("╔══════════════════════════════════════════════════════════════╗");
  console.log("║  Task Sync                                                   ║");
  console.log("╠══════════════════════════════════════════════════════════════╣");
  console.log(`║  Target: ${targetId.slice(0, 50).padEnd(50)}║`);
  console.log(`║  Sources: ${String(sourceLists.length).padEnd(49)}║`);
  console.log(`║  Total tasks: ${String(totalTasks).padEnd(45)}║`);
  console.log("╚══════════════════════════════════════════════════════════════╝");
  console.log("");

  if (dryRun) {
    console.log("🔍 DRY RUN - No changes will be made\n");
  }

  // Create target directory
  const targetDir = join(tasksBaseDir, targetId);
  if (!dryRun) {
    await mkdir(targetDir, { recursive: true });
  }

  // Get starting ID for target list
  let nextId = await getNextTaskId(targetId);
  let totalMigrated = 0;

  for (const sourceList of sourceLists) {
    console.log(`\n📁 Syncing from: ${sourceList.id}`);

    const sourceTasks = await loadTasks(sourceList.id);

    // Create ID mapping for this source
    const idMapping: Record<string, string> = {};
    for (const task of sourceTasks) {
      idMapping[task.id] = String(nextId);
      nextId++;
    }

    // Migrate tasks with updated IDs
    for (const task of sourceTasks) {
      const newTask: Task = {
        ...task,
        id: idMapping[task.id],
        blockedBy: task.blockedBy?.map(id => idMapping[id] || id) || [],
        blocks: task.blocks?.map(id => idMapping[id] || id) || [],
        // Add source info to metadata
        metadata: {
          ...task.metadata,
          _syncedFrom: sourceList.id,
          _originalId: task.id,
          _syncedAt: new Date().toISOString(),
        },
      };

      const targetPath = join(targetDir, `${newTask.id}.json`);

      if (verbose || dryRun) {
        console.log(`   ${task.id} → ${newTask.id}: ${task.subject.slice(0, 45)}`);
      }

      if (!dryRun) {
        await writeFile(targetPath, JSON.stringify(newTask, null, 2));
      }

      totalMigrated++;
    }

    console.log(`   ✓ ${sourceTasks.length} tasks`);
  }

  // Update current list file
  if (!dryRun) {
    await writeFile(currentListFile, targetId);
  }

  console.log("");
  console.log("═".repeat(60));
  if (dryRun) {
    console.log(`\n✅ Would sync ${totalMigrated} tasks to '${targetId}'`);
  } else {
    console.log(`\n✅ Synced ${totalMigrated} tasks to '${targetId}'`);
  }

  console.log("");
  console.log("To use the shared list, restart Claude with:");
  console.log("");
  console.log(`  CLAUDE_CODE_TASK_LIST_ID=${targetId} claude`);
  console.log("");
  console.log("Or use the wrapper script:");
  console.log("");
  console.log(`  ~/.claude/skills/dispatch/scripts/start-session.sh ${targetId}`);
  console.log("");

  if (!dryRun && totalMigrated > 0) {
    console.log("💡 Original tasks remain in source lists.");
    console.log("   To clean up orphaned lists:");
    for (const source of sourceLists) {
      console.log(`   rm -rf ${join(tasksBaseDir, source.id)}`);
    }
    console.log("");
  }
}

// Main
if (listMode) {
  await listAllLists();
} else {
  await syncTasks();
}
