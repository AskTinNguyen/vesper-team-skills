#!/usr/bin/env bun
/**
 * task-dashboard.ts
 *
 * Real-time CLI dashboard for task coordination status:
 * - Displays task board (Pending | In Progress | Completed)
 * - Shows dependency graph as ASCII
 * - Highlights blocked tasks and their blockers
 * - Auto-refresh mode with configurable interval
 *
 * Usage:
 *   bun run scripts/task-dashboard.ts [task-list-id]
 *   bun run scripts/task-dashboard.ts [task-list-id] --watch
 *   bun run scripts/task-dashboard.ts [task-list-id] --watch --interval=5
 *
 * Task list ID resolution (in order):
 * 1. Explicit argument
 * 2. CLAUDE_CODE_TASK_LIST_ID environment variable
 * 3. Most recent task list with tasks
 */

import { readdir, readFile } from "fs/promises";
import { join } from "path";
import { homedir } from "os";
import { resolveTaskListId, getTasksDir } from "./lib/task-list-resolver.js";

interface Task {
  id: string;
  subject: string;
  description?: string;
  status: "pending" | "in_progress" | "completed";
  owner?: string;
  blockedBy?: string[];
  blocks?: string[];
  metadata?: {
    model?: string;
    startedAt?: string;
  };
}

interface DashboardData {
  pending: Task[];
  inProgress: Task[];
  completed: Task[];
  blocked: Task[];
  ready: Task[];
}

function parseArgs(): { explicitId?: string; watch: boolean; interval: number } {
  const args = process.argv.slice(2);
  let explicitId: string | undefined;
  let watch = false;
  let interval = 10;

  for (const arg of args) {
    if (arg === "--watch" || arg === "-w") {
      watch = true;
    } else if (arg.startsWith("--interval=")) {
      const parsed = parseInt(arg.split("=")[1], 10);
      interval = isNaN(parsed) || parsed < 1 ? 10 : parsed;
    } else if (!arg.startsWith("--")) {
      explicitId = arg;
    }
  }

  return { explicitId, watch, interval };
}

async function loadTasks(tasksDir: string): Promise<Map<string, Task>> {
  const tasks = new Map<string, Task>();

  try {
    const files = await readdir(tasksDir);

    for (const file of files) {
      if (file.endsWith(".json")) {
        try {
          const content = await readFile(join(tasksDir, file), "utf-8");
          const task = JSON.parse(content) as Task;
          if (task.id) {
            tasks.set(task.id, task);
          }
        } catch {
          // Skip invalid files
        }
      }
    }
  } catch {
    // Directory doesn't exist
  }

  return tasks;
}

function categorizeTasks(tasks: Map<string, Task>): DashboardData {
  const pending: Task[] = [];
  const inProgress: Task[] = [];
  const completed: Task[] = [];
  const blocked: Task[] = [];
  const ready: Task[] = [];

  for (const task of tasks.values()) {
    switch (task.status) {
      case "completed":
        completed.push(task);
        break;
      case "in_progress":
        inProgress.push(task);
        break;
      case "pending":
        pending.push(task);

        // Check if blocked
        const blockedBy = task.blockedBy || [];
        const hasIncompleteBlockers = blockedBy.some(id => {
          const blocker = tasks.get(id);
          return !blocker || blocker.status !== "completed";
        });

        if (hasIncompleteBlockers) {
          blocked.push(task);
        } else {
          ready.push(task);
        }
        break;
    }
  }

  return { pending, inProgress, completed, blocked, ready };
}

function truncate(str: string, maxLen: number): string {
  if (str.length <= maxLen) return str;
  return str.slice(0, maxLen - 3) + "...";
}

function renderProgressBar(completed: number, total: number, width: number = 20): string {
  if (total === 0) return "[" + " ".repeat(width) + "]";

  const progress = Math.round((completed / total) * width);
  const bar = "█".repeat(progress) + "░".repeat(width - progress);
  const percent = Math.round((completed / total) * 100);

  return `[${bar}] ${percent}%`;
}

function renderDashboard(tasks: Map<string, Task>, taskListId?: string): void {
  const data = categorizeTasks(tasks);
  const total = tasks.size;
  const completedCount = data.completed.length;

  // Clear screen for watch mode
  console.clear();

  // Header
  console.log("\n╔══════════════════════════════════════════════════════════════╗");
  console.log("║                    📋 TASK DASHBOARD                          ║");
  console.log("╠══════════════════════════════════════════════════════════════╣");

  if (taskListId) {
    console.log(`║  Task List: ${truncate(taskListId, 48).padEnd(48)} ║`);
  }

  console.log(`║  ${renderProgressBar(completedCount, total, 30)} ${completedCount}/${total} tasks    ║`);
  console.log("╚══════════════════════════════════════════════════════════════╝\n");

  // Stats row
  console.log("┌─────────────┬─────────────┬─────────────┬─────────────┐");
  console.log("│   PENDING   │ IN PROGRESS │  COMPLETED  │   BLOCKED   │");
  console.log("├─────────────┼─────────────┼─────────────┼─────────────┤");
  console.log(`│     ${String(data.pending.length).padStart(3)}     │     ${String(data.inProgress.length).padStart(3)}     │     ${String(data.completed.length).padStart(3)}     │     ${String(data.blocked.length).padStart(3)}     │`);
  console.log("└─────────────┴─────────────┴─────────────┴─────────────┘\n");

  // Ready to spawn
  if (data.ready.length > 0) {
    console.log("✅ READY TO SPAWN:");
    for (const task of data.ready.slice(0, 5)) {
      console.log(`   ${task.id}: ${truncate(task.subject, 50)}`);
    }
    if (data.ready.length > 5) {
      console.log(`   ... and ${data.ready.length - 5} more`);
    }
    console.log("");
  }

  // In progress
  if (data.inProgress.length > 0) {
    console.log("🔄 IN PROGRESS:");
    for (const task of data.inProgress) {
      const owner = task.owner ? ` (${task.owner})` : "";
      const model = task.metadata?.model ? ` [${task.metadata.model}]` : "";
      console.log(`   ${task.id}: ${truncate(task.subject, 40)}${model}${owner}`);
    }
    console.log("");
  }

  // Blocked
  if (data.blocked.length > 0) {
    console.log("🚫 BLOCKED:");
    for (const task of data.blocked.slice(0, 5)) {
      const blockers = task.blockedBy?.filter(id => {
        const t = tasks.get(id);
        return !t || t.status !== "completed";
      }) || [];
      console.log(`   ${task.id}: ${truncate(task.subject, 35)}`);
      console.log(`      ↳ waiting on: ${blockers.join(", ")}`);
    }
    if (data.blocked.length > 5) {
      console.log(`   ... and ${data.blocked.length - 5} more`);
    }
    console.log("");
  }

  // Dependency graph (simplified)
  if (tasks.size > 0 && tasks.size <= 15) {
    console.log("📊 DEPENDENCY GRAPH:");
    renderSimpleGraph(tasks);
    console.log("");
  }

  // Timestamp
  const now = new Date().toLocaleTimeString();
  console.log(`Last updated: ${now}`);
}

function renderSimpleGraph(tasks: Map<string, Task>): void {
  const taskList = [...tasks.values()];

  // Group by depth level
  const levels = new Map<number, Task[]>();
  const taskDepths = new Map<string, number>();

  function getDepth(taskId: string, visited: Set<string> = new Set()): number {
    if (visited.has(taskId)) return 0;
    if (taskDepths.has(taskId)) return taskDepths.get(taskId)!;

    visited.add(taskId);
    const task = tasks.get(taskId);
    if (!task) return 0;

    const blockedBy = task.blockedBy || [];
    if (blockedBy.length === 0) {
      taskDepths.set(taskId, 0);
      return 0;
    }

    const maxParentDepth = Math.max(...blockedBy.map(id => getDepth(id, visited)));
    const depth = maxParentDepth + 1;
    taskDepths.set(taskId, depth);
    return depth;
  }

  // Compute depths
  for (const task of taskList) {
    const depth = getDepth(task.id);
    const level = levels.get(depth) || [];
    level.push(task);
    levels.set(depth, level);
  }

  // Render levels
  const maxDepth = Math.max(...levels.keys(), 0);

  for (let depth = 0; depth <= maxDepth; depth++) {
    const tasksAtLevel = levels.get(depth) || [];
    const prefix = depth === 0 ? "   " : "   " + "│  ".repeat(depth - 1) + "├──";

    for (const task of tasksAtLevel) {
      const statusIcon = task.status === "completed" ? "✓" :
                        task.status === "in_progress" ? "●" : "○";
      const line = `${prefix} ${statusIcon} ${task.id}`;
      console.log(line);
    }
  }
}

// Main execution
const { explicitId, watch, interval } = parseArgs();

const taskListId = await resolveTaskListId(explicitId);
if (!taskListId) {
  console.error("❌ No task list found. Create tasks first or set CLAUDE_CODE_TASK_LIST_ID.");
  process.exit(1);
}

const tasksDir = getTasksDir(taskListId);

async function refresh(): Promise<void> {
  const tasks = await loadTasks(tasksDir);
  renderDashboard(tasks, taskListId);
}

await refresh();

if (watch) {
  console.log(`\nWatching for changes (refresh every ${interval}s). Press Ctrl+C to exit.`);

  setInterval(async () => {
    await refresh();
  }, interval * 1000);
}
