#!/usr/bin/env bun
/**
 * archive-tasks.ts
 *
 * Archive tasks from a task list to preserve them as historical logs.
 * Tasks are copied to ~/.claude/tasks-archive/<list-id>-<timestamp>/
 *
 * Usage:
 *   bun run archive-tasks.ts [task-list-id]     # Archive specific list
 *   bun run archive-tasks.ts --all              # Archive all non-empty lists
 *   bun run archive-tasks.ts --completed        # Archive lists where all tasks are completed
 *   bun run archive-tasks.ts --dry-run          # Preview without archiving
 *
 * Task list ID resolution (in order):
 * 1. Explicit argument
 * 2. CLAUDE_CODE_TASK_LIST_ID environment variable
 * 3. Most recent task list with tasks
 */

import { readdir, readFile, writeFile, mkdir, copyFile, stat } from "fs/promises";
import { join } from "path";
import { homedir } from "os";
import { existsSync } from "fs";
import { resolveTaskListId, getTasksDir, getTasksBaseDir } from "./lib/task-list-resolver.js";

interface Task {
  id: string;
  subject: string;
  description?: string;
  status: "pending" | "in_progress" | "completed";
  owner?: string;
  blockedBy?: string[];
  blocks?: string[];
  activeForm?: string;
  metadata?: Record<string, unknown>;
  createdAt?: string;
  updatedAt?: string;
}

interface ArchiveManifest {
  listId: string;
  archivedAt: string;
  taskCount: number;
  completedCount: number;
  pendingCount: number;
  inProgressCount: number;
  tasks: Task[];
}

const tasksBaseDir = getTasksBaseDir();
const archiveBaseDir = join(homedir(), ".claude", "tasks-archive");
const args = process.argv.slice(2);

// Parse arguments
const dryRun = args.includes("--dry-run") || args.includes("-n");
const archiveAll = args.includes("--all") || args.includes("-a");
const archiveCompleted = args.includes("--completed") || args.includes("-c");
const verbose = args.includes("--verbose") || args.includes("-v");
const explicitId = args.find(a => !a.startsWith("-"));

if (args.includes("--help") || args.includes("-h")) {
  console.log(`
archive-tasks.ts - Archive tasks as historical logs

Usage:
  bun run archive-tasks.ts [task-list-id]     Archive specific list
  bun run archive-tasks.ts --all              Archive all non-empty lists
  bun run archive-tasks.ts --completed        Archive lists where all tasks done
  bun run archive-tasks.ts --dry-run          Preview without archiving

Options:
  --all, -a         Archive all non-empty task lists
  --completed, -c   Only archive lists where all tasks are completed
  --dry-run, -n     Show what would be archived without making changes
  --verbose, -v     Show detailed output
  --help, -h        Show this help message

Archive location: ~/.claude/tasks-archive/<list-id>-<timestamp>/

The archive contains:
  - manifest.json: Summary with all task data
  - Individual <task-id>.json files (copies of originals)

Examples:
  # Archive current task list
  bun run archive-tasks.ts

  # Archive specific list
  bun run archive-tasks.ts my-feature

  # Archive all completed task lists
  bun run archive-tasks.ts --completed

  # Preview what would be archived
  bun run archive-tasks.ts --all --dry-run
`);
  process.exit(0);
}

async function loadTasks(listId: string): Promise<Task[]> {
  const listDir = join(tasksBaseDir, listId);
  const tasks: Task[] = [];

  try {
    const files = await readdir(listDir);
    for (const file of files) {
      if (!file.endsWith(".json") || file.startsWith(".")) continue;
      try {
        const content = await readFile(join(listDir, file), "utf-8");
        tasks.push(JSON.parse(content));
      } catch {}
    }
  } catch {}

  return tasks;
}

async function getAllTaskLists(): Promise<{ id: string; taskCount: number; allCompleted: boolean }[]> {
  const lists: { id: string; taskCount: number; allCompleted: boolean }[] = [];

  try {
    const entries = await readdir(tasksBaseDir, { withFileTypes: true });

    for (const entry of entries) {
      if (!entry.isDirectory() || entry.name.startsWith(".")) continue;

      const tasks = await loadTasks(entry.name);
      if (tasks.length === 0) continue;

      const allCompleted = tasks.every(t => t.status === "completed");
      lists.push({ id: entry.name, taskCount: tasks.length, allCompleted });
    }
  } catch {}

  return lists;
}

async function archiveTaskList(listId: string): Promise<{ success: boolean; archivePath?: string; error?: string }> {
  const tasks = await loadTasks(listId);

  if (tasks.length === 0) {
    return { success: false, error: "No tasks to archive" };
  }

  // Create archive directory with timestamp
  const timestamp = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
  const archiveName = `${listId}-${timestamp}`;
  const archiveDir = join(archiveBaseDir, archiveName);

  if (dryRun) {
    console.log(`  Would archive to: ${archiveDir}`);
    console.log(`  Tasks: ${tasks.length}`);
    return { success: true, archivePath: archiveDir };
  }

  try {
    await mkdir(archiveDir, { recursive: true });

    // Create manifest with all task data
    const manifest: ArchiveManifest = {
      listId,
      archivedAt: new Date().toISOString(),
      taskCount: tasks.length,
      completedCount: tasks.filter(t => t.status === "completed").length,
      pendingCount: tasks.filter(t => t.status === "pending").length,
      inProgressCount: tasks.filter(t => t.status === "in_progress").length,
      tasks,
    };

    await writeFile(join(archiveDir, "manifest.json"), JSON.stringify(manifest, null, 2));

    // Copy individual task files
    const sourceDir = join(tasksBaseDir, listId);
    for (const task of tasks) {
      const sourceFile = join(sourceDir, `${task.id}.json`);
      const destFile = join(archiveDir, `${task.id}.json`);
      if (existsSync(sourceFile)) {
        await copyFile(sourceFile, destFile);
      }
    }

    return { success: true, archivePath: archiveDir };
  } catch (error) {
    return { success: false, error: String(error) };
  }
}

async function main(): Promise<void> {
  console.log("");
  console.log("📦 Task Archival");
  console.log("═".repeat(60));

  if (dryRun) {
    console.log("🔍 DRY RUN - No changes will be made\n");
  }

  let listsToArchive: string[] = [];

  if (archiveAll || archiveCompleted) {
    const allLists = await getAllTaskLists();

    if (archiveCompleted) {
      listsToArchive = allLists.filter(l => l.allCompleted).map(l => l.id);
      console.log(`Found ${listsToArchive.length} completed task list(s)\n`);
    } else {
      listsToArchive = allLists.map(l => l.id);
      console.log(`Found ${listsToArchive.length} non-empty task list(s)\n`);
    }
  } else {
    const listId = await resolveTaskListId(explicitId);
    if (!listId) {
      console.error("❌ No task list found. Specify a list ID or use --all.");
      process.exit(1);
    }
    listsToArchive = [listId];
  }

  if (listsToArchive.length === 0) {
    console.log("No task lists to archive.");
    process.exit(0);
  }

  let successCount = 0;
  let failCount = 0;

  for (const listId of listsToArchive) {
    console.log(`\n📋 Archiving: ${listId}`);

    const result = await archiveTaskList(listId);

    if (result.success) {
      successCount++;
      if (!dryRun) {
        console.log(`   ✅ Archived to: ${result.archivePath}`);
      }
    } else {
      failCount++;
      console.log(`   ❌ Failed: ${result.error}`);
    }
  }

  console.log("\n" + "═".repeat(60));
  if (dryRun) {
    console.log(`Would archive ${successCount} task list(s)`);
  } else {
    console.log(`✅ Archived ${successCount} task list(s)`);
    if (failCount > 0) {
      console.log(`❌ Failed: ${failCount}`);
    }
  }
  console.log(`\nArchive location: ${archiveBaseDir}`);
  console.log("");
}

await main();
