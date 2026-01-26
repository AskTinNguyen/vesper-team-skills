#!/usr/bin/env bun
/**
 * migrate-session.ts
 *
 * Migrate tasks from the current session to a shared task list.
 *
 * Use this when you realize mid-session that you forgot to set
 * CLAUDE_CODE_TASK_LIST_ID before starting Claude.
 *
 * Usage:
 *   bun run migrate-session.ts <target-list-id>
 *   bun run migrate-session.ts my-project
 *   bun run migrate-session.ts my-project --dry-run
 *
 * This will:
 * 1. Find the current session's task list
 * 2. Copy all tasks to the target list
 * 3. Output the command to restart Claude with the target list
 */

import { readdir, readFile, writeFile, mkdir, copyFile } from "fs/promises";
import { join } from "path";
import { homedir } from "os";
import { existsSync } from "fs";

const tasksBaseDir = join(homedir(), ".claude", "tasks");
const currentListFile = join(tasksBaseDir, ".current-list-id");
const args = process.argv.slice(2);

// Parse arguments
const dryRun = args.includes("--dry-run") || args.includes("-n");
const verbose = args.includes("--verbose") || args.includes("-v");
const targetId = args.find(a => !a.startsWith("-"));

if (!targetId || args.includes("--help") || args.includes("-h")) {
  console.log(`
migrate-session.ts - Migrate current session tasks to a shared list

Usage:
  bun run migrate-session.ts <target-list-id> [options]

Arguments:
  target-list-id    The shared list ID to migrate tasks to

Options:
  --dry-run, -n     Show what would be done without making changes
  --verbose, -v     Show detailed output
  --help, -h        Show this help message

Examples:
  # Migrate to a new shared list
  bun run migrate-session.ts my-project

  # Preview migration without making changes
  bun run migrate-session.ts my-project --dry-run

This script is useful when you forgot to set CLAUDE_CODE_TASK_LIST_ID
before starting Claude and need to recover your tasks.
`);
  process.exit(targetId ? 0 : 1);
}

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

async function findCurrentSessionList(): Promise<string | null> {
  // Try to find the session-scoped list (UUID format, not custom names)
  try {
    const entries = await readdir(tasksBaseDir, { withFileTypes: true });
    const sessionLists: { id: string; taskCount: number; modified: Date }[] = [];

    for (const entry of entries) {
      if (!entry.isDirectory() || entry.name.startsWith(".")) continue;

      // Session-scoped lists typically have UUID format or session-timestamp format
      const isSessionScoped = entry.name.match(/^[a-f0-9-]{36}$/) ||
                              entry.name.startsWith("session-");

      if (!isSessionScoped) continue;

      const listPath = join(tasksBaseDir, entry.name);
      const { stat } = await import("fs/promises");
      const listStat = await stat(listPath);

      let taskCount = 0;
      try {
        const files = await readdir(listPath);
        taskCount = files.filter(f => f.endsWith(".json")).length;
      } catch {}

      if (taskCount > 0) {
        sessionLists.push({ id: entry.name, taskCount, modified: listStat.mtime });
      }
    }

    if (sessionLists.length === 0) return null;

    // Sort by modification time (most recent first)
    sessionLists.sort((a, b) => b.modified.getTime() - a.modified.getTime());

    return sessionLists[0].id;
  } catch {
    return null;
  }
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

async function migrate(): Promise<void> {
  // Find source list
  const sourceId = await findCurrentSessionList();

  if (!sourceId) {
    console.error("❌ No session-scoped task list found with tasks");
    console.error("");
    console.error("   This script looks for lists with UUID or session-timestamp format.");
    console.error("   Make sure you have created tasks in the current session.");
    console.error("");
    console.error("   Available lists:");
    try {
      const entries = await readdir(tasksBaseDir, { withFileTypes: true });
      for (const entry of entries) {
        if (!entry.isDirectory() || entry.name.startsWith(".")) continue;
        const listPath = join(tasksBaseDir, entry.name);
        const files = await readdir(listPath);
        const taskCount = files.filter(f => f.endsWith(".json")).length;
        console.error(`   - ${entry.name} (${taskCount} tasks)`);
      }
    } catch {}
    process.exit(1);
  }

  if (sourceId === targetId) {
    console.error("❌ Source and target are the same list");
    process.exit(1);
  }

  // Load source tasks
  const sourceTasks = await loadTasks(sourceId);

  if (sourceTasks.length === 0) {
    console.error(`❌ No tasks found in source list: ${sourceId}`);
    process.exit(1);
  }

  console.log("");
  console.log("╔══════════════════════════════════════════════════════════════╗");
  console.log("║  Task Migration                                              ║");
  console.log("╠══════════════════════════════════════════════════════════════╣");
  console.log(`║  Source: ${sourceId.slice(0, 50).padEnd(50)}║`);
  console.log(`║  Target: ${targetId.slice(0, 50).padEnd(50)}║`);
  console.log(`║  Tasks:  ${String(sourceTasks.length).padEnd(50)}║`);
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
  const idMapping: Record<string, string> = {};

  // First pass: create ID mapping
  for (const task of sourceTasks) {
    idMapping[task.id] = String(nextId);
    nextId++;
  }

  // Second pass: migrate tasks with updated IDs
  for (const task of sourceTasks) {
    const newTask: Task = {
      ...task,
      id: idMapping[task.id],
      blockedBy: task.blockedBy?.map(id => idMapping[id] || id) || [],
      blocks: task.blocks?.map(id => idMapping[id] || id) || [],
    };

    const targetPath = join(targetDir, `${newTask.id}.json`);

    if (verbose || dryRun) {
      console.log(`  ${task.id} → ${newTask.id}: ${task.subject.slice(0, 50)}`);
    }

    if (!dryRun) {
      await writeFile(targetPath, JSON.stringify(newTask, null, 2));
    }
  }

  // Update current list file
  if (!dryRun) {
    await writeFile(currentListFile, targetId);
  }

  console.log("");
  if (dryRun) {
    console.log(`✅ Would migrate ${sourceTasks.length} tasks to '${targetId}'`);
  } else {
    console.log(`✅ Migrated ${sourceTasks.length} tasks to '${targetId}'`);
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

  if (!dryRun && sourceTasks.length > 0) {
    console.log("💡 The original tasks remain in the source list.");
    console.log(`   To delete: rm -rf ${join(tasksBaseDir, sourceId)}`);
    console.log("");
  }
}

await migrate();
