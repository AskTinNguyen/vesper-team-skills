#!/usr/bin/env bun
/**
 * spawn-agent.ts
 *
 * Generate a Task() call for spawning a subagent.
 *
 * Subagents automatically inherit CLAUDE_CODE_TASK_LIST_ID from the parent
 * session when the parent was started correctly (with the env var set).
 *
 * Usage:
 *   bun run spawn-agent.ts <task-id> [model] [--json]
 *   bun run spawn-agent.ts 1 sonnet
 *   bun run spawn-agent.ts 2 opus --json
 *
 * Output: A Task() call you can paste or use programmatically
 */

import { readFile, readdir } from "fs/promises";
import { join } from "path";
import { homedir } from "os";
import { requireCoordination, getTasksDir } from "./lib/task-list-resolver.js";

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
}

const args = process.argv.slice(2);
const taskId = args.find(a => !a.startsWith("-"));
const model = args.find((a, i) => !a.startsWith("-") && i > 0 && args[i - 1] === taskId) || "sonnet";
const jsonOutput = args.includes("--json");

if (!taskId || args.includes("--help") || args.includes("-h")) {
  console.error(`
spawn-agent.ts - Generate Task() call for spawning a subagent

Usage:
  bun run spawn-agent.ts <task-id> [model] [--json]

Arguments:
  task-id    ID of the task to spawn an agent for
  model      Model to use: haiku, sonnet (default), opus

Options:
  --json     Output JSON instead of Task() call

Examples:
  bun run spawn-agent.ts 1              # Spawn for task 1 with sonnet
  bun run spawn-agent.ts 2 opus         # Spawn for task 2 with opus
  bun run spawn-agent.ts 3 haiku --json # Get JSON output

Note: The parent Claude session must have been started with
CLAUDE_CODE_TASK_LIST_ID set. Subagents inherit this automatically.
`);
  process.exit(1);
}

// Require coordination to be enabled (exits if not)
const listId = requireCoordination();
const tasksDir = getTasksDir(listId);

// Load the task
let task: Task;
try {
  const taskPath = join(tasksDir, `${taskId}.json`);
  const content = await readFile(taskPath, "utf-8");
  task = JSON.parse(content);
} catch (error) {
  console.error(`❌ Could not load task ${taskId}`);

  // List available tasks
  try {
    const files = await readdir(tasksDir);
    const taskIds = files.filter(f => f.endsWith(".json")).map(f => f.replace(".json", ""));
    if (taskIds.length > 0) {
      console.error(`   Available tasks: ${taskIds.join(", ")}`);
    } else {
      console.error(`   No tasks found in ${tasksDir}`);
    }
  } catch {
    console.error(`   Task list directory not found: ${tasksDir}`);
  }

  process.exit(1);
}

// Check if task is ready to spawn
if (task.status === "completed") {
  console.error(`⚠️  Task ${taskId} is already completed`);
  process.exit(1);
}

if (task.status === "in_progress" && task.owner) {
  console.error(`⚠️  Task ${taskId} is already in progress (owner: ${task.owner})`);
  console.error("   Use --force to spawn anyway (not recommended)");
  if (!args.includes("--force")) {
    process.exit(1);
  }
}

// Check blockers
if (task.blockedBy && task.blockedBy.length > 0) {
  const blockers: string[] = [];
  for (const blockerId of task.blockedBy) {
    try {
      const blockerPath = join(tasksDir, `${blockerId}.json`);
      const blockerContent = await readFile(blockerPath, "utf-8");
      const blocker = JSON.parse(blockerContent);
      if (blocker.status !== "completed") {
        blockers.push(`${blockerId} (${blocker.status})`);
      }
    } catch {
      blockers.push(`${blockerId} (not found)`);
    }
  }

  if (blockers.length > 0) {
    console.error(`❌ Task ${taskId} is blocked by: ${blockers.join(", ")}`);
    process.exit(1);
  }
}

// Build the prompt - no need to export env var, it's inherited automatically
const prompt = `## Your Assignment

**Task ID:** ${task.id}
**Subject:** ${task.subject}

### Requirements

${task.description || "No description provided."}

---

## On Completion

When you have FULLY completed this task (tests pass, code works), run:

\`\`\`
TaskUpdate(taskId: "${task.id}", status: "completed")
\`\`\`

If you encounter blockers or cannot complete:
1. Keep status as in_progress
2. Create a new task describing the blocker
3. Report what was accomplished and what remains
`;

const taskCall = {
  subagent_type: "general-purpose",
  model: model,
  prompt: prompt,
  description: `Task ${task.id}: ${task.subject.slice(0, 40)}`,
};

if (jsonOutput) {
  console.log(JSON.stringify(taskCall, null, 2));
} else {
  // Output formatted Task() call
  console.log(`
Task(
  subagent_type: "general-purpose",
  model: "${model}",
  prompt: \`${prompt.replace(/`/g, "\\`")}\`,
  description: "Task ${task.id}: ${task.subject.slice(0, 40)}"
)
`);

  // Reminder to claim the task first
  console.error(`
📋 Before pasting the Task() call above, claim the task:

TaskUpdate(taskId: "${task.id}", status: "in_progress", owner: "coordinator")
`);
}
