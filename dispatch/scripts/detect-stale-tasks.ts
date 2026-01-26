#!/usr/bin/env bun
/**
 * detect-stale-tasks.ts
 *
 * Identifies tasks that appear stuck or abandoned:
 * - Tasks in 'in_progress' beyond configurable threshold
 * - Tasks with no recent activity
 * - Orphaned tasks from terminated sessions
 *
 * Usage: bun run scripts/detect-stale-tasks.ts [task-list-id] [--threshold=30] [--reset]
 *
 * Options:
 *   --threshold=N   Minutes before a task is considered stale (default: 30)
 *   --reset         Reset stale tasks to pending status
 *   --json          Output as JSON
 *
 * Task list ID resolution (in order):
 * 1. Explicit argument
 * 2. CLAUDE_CODE_TASK_LIST_ID environment variable
 * 3. Most recent task list with tasks
 */

import { readdir, readFile, writeFile, stat } from "fs/promises";
import { join } from "path";
import { homedir } from "os";
import { resolveTaskListId, getTasksDir } from "./lib/task-list-resolver.js";

interface Task {
  id: string;
  subject: string;
  status: "pending" | "in_progress" | "completed";
  owner?: string;
  startedAt?: string;
  updatedAt?: string;
  blockedBy?: string[];
}

interface StaleTask {
  task: Task;
  reason: string;
  staleDuration: number; // minutes
  filePath: string;
  lastModified: Date;
}

interface DetectionResult {
  staleTasks: StaleTask[];
  healthyTasks: number;
  totalTasks: number;
}

function parseArgs(): { explicitId?: string; threshold: number; reset: boolean; json: boolean } {
  const args = process.argv.slice(2);
  let explicitId: string | undefined;
  let threshold = 30;
  let reset = false;
  let json = false;

  for (const arg of args) {
    if (arg.startsWith("--threshold=")) {
      const parsed = parseInt(arg.split("=")[1], 10);
      threshold = isNaN(parsed) ? 30 : parsed;
    } else if (arg === "--reset") {
      reset = true;
    } else if (arg === "--json") {
      json = true;
    } else if (!arg.startsWith("--")) {
      explicitId = arg;
    }
  }

  return { explicitId, threshold, reset, json };
}

async function getTaskFiles(tasksDir: string): Promise<string[]> {
  try {
    const files = await readdir(tasksDir);
    return files
      .filter(f => f.endsWith(".json"))
      .map(f => join(tasksDir, f));
  } catch {
    console.error(`Error reading tasks directory: ${tasksDir}`);
    return [];
  }
}

async function loadTaskWithMeta(filePath: string): Promise<{ task: Task; lastModified: Date } | null> {
  try {
    const content = await readFile(filePath, "utf-8");
    const task = JSON.parse(content) as Task;
    const stats = await stat(filePath);
    return { task, lastModified: stats.mtime };
  } catch {
    return null;
  }
}

async function detectStaleTasks(
  tasksDir: string,
  thresholdMinutes: number
): Promise<DetectionResult> {
  const taskFiles = await getTaskFiles(tasksDir);
  const staleTasks: StaleTask[] = [];
  let healthyTasks = 0;

  const now = new Date();

  for (const filePath of taskFiles) {
    const result = await loadTaskWithMeta(filePath);
    if (!result) continue;

    const { task, lastModified } = result;

    // Skip completed tasks
    if (task.status === "completed") {
      healthyTasks++;
      continue;
    }

    // Check for stale in_progress tasks
    if (task.status === "in_progress") {
      const ageMinutes = (now.getTime() - lastModified.getTime()) / (1000 * 60);

      if (ageMinutes > thresholdMinutes) {
        staleTasks.push({
          task,
          reason: `In progress for ${Math.round(ageMinutes)} minutes (threshold: ${thresholdMinutes})`,
          staleDuration: Math.round(ageMinutes),
          filePath,
          lastModified,
        });
        continue;
      }
    }

    // Check for very old pending tasks (7 days)
    if (task.status === "pending") {
      const ageDays = (now.getTime() - lastModified.getTime()) / (1000 * 60 * 60 * 24);

      if (ageDays > 7) {
        staleTasks.push({
          task,
          reason: `Pending for ${Math.round(ageDays)} days without updates`,
          staleDuration: Math.round(ageDays * 24 * 60),
          filePath,
          lastModified,
        });
        continue;
      }
    }

    healthyTasks++;
  }

  return {
    staleTasks,
    healthyTasks,
    totalTasks: taskFiles.length,
  };
}

async function resetStaleTasks(staleTasks: StaleTask[]): Promise<number> {
  let resetCount = 0;

  for (const stale of staleTasks) {
    try {
      const updatedTask: Task = {
        ...stale.task,
        status: "pending",
        owner: undefined,
        updatedAt: new Date().toISOString(),
      };

      await writeFile(stale.filePath, JSON.stringify(updatedTask, null, 2));
      resetCount++;
    } catch (error) {
      console.error(`Failed to reset task ${stale.task.id}: ${error}`);
    }
  }

  return resetCount;
}

function formatDuration(minutes: number): string {
  if (minutes < 60) {
    return `${minutes}m`;
  } else if (minutes < 1440) {
    return `${Math.round(minutes / 60)}h`;
  } else {
    return `${Math.round(minutes / 1440)}d`;
  }
}

function formatResult(result: DetectionResult, json: boolean): void {
  if (json) {
    console.log(JSON.stringify(result, null, 2));
    return;
  }

  console.log("\n🔍 Stale Task Detection\n");
  console.log("=".repeat(50));

  console.log("\n📈 Summary:");
  console.log(`   Total tasks: ${result.totalTasks}`);
  console.log(`   Healthy: ${result.healthyTasks}`);
  console.log(`   Stale: ${result.staleTasks.length}`);

  if (result.staleTasks.length > 0) {
    console.log("\n⚠️  Stale Tasks:");
    console.log("");

    for (const stale of result.staleTasks) {
      const duration = formatDuration(stale.staleDuration);
      console.log(`   📋 ${stale.task.id}: ${stale.task.subject}`);
      console.log(`      Status: ${stale.task.status}`);
      console.log(`      Owner: ${stale.task.owner || "none"}`);
      console.log(`      Stale for: ${duration}`);
      console.log(`      Reason: ${stale.reason}`);
      console.log("");
    }
  }

  console.log("=".repeat(50));

  if (result.staleTasks.length === 0) {
    console.log("✅ No stale tasks found");
  } else {
    console.log(`⚠️  Found ${result.staleTasks.length} stale task(s)`);
    console.log("   Run with --reset to reset them to pending status");
  }
  console.log("");
}

// Main execution
const { explicitId, threshold, reset, json } = parseArgs();

const taskListId = await resolveTaskListId(explicitId);
if (!taskListId) {
  console.error("❌ No task list found. Create tasks first or set CLAUDE_CODE_TASK_LIST_ID.");
  process.exit(1);
}

const tasksDir = getTasksDir(taskListId);
const result = await detectStaleTasks(tasksDir, threshold);

if (reset && result.staleTasks.length > 0) {
  const resetCount = await resetStaleTasks(result.staleTasks);
  if (!json) {
    console.log(`\n🔄 Reset ${resetCount} task(s) to pending status\n`);
  }
}

formatResult(result, json);

// Exit with warning code if stale tasks found
if (result.staleTasks.length > 0) {
  process.exit(1);
}
