#!/usr/bin/env bun
/**
 * pre-spawn-validation.ts
 *
 * Validates all conditions before spawning a subagent for a task:
 * - Task is not already claimed by another agent
 * - All blockedBy tasks are completed
 * - No file conflicts with other in_progress tasks
 * - Resource limits are not exceeded
 *
 * Usage: bun run scripts/pre-spawn-validation.ts <task-id> [task-list-id]
 *
 * Returns exit code 0 if spawn is allowed, 1 if blocked
 *
 * Task list ID resolution (in order):
 * 1. Explicit second argument
 * 2. CLAUDE_CODE_TASK_LIST_ID environment variable
 * 3. Most recent task list with tasks
 */

import { readdir, readFile } from "fs/promises";
import { join } from "path";
import { homedir } from "os";
import { resolveTaskListId, getTasksDir, enforceSharedList } from "./lib/task-list-resolver.js";

interface Task {
  id: string;
  subject: string;
  description?: string;
  status: "pending" | "in_progress" | "completed";
  owner?: string;
  blockedBy?: string[];
  blocks?: string[];
  metadata?: {
    files?: string[];
    model?: string;
  };
}

interface ValidationCheck {
  name: string;
  passed: boolean;
  message: string;
  severity: "error" | "warning";
}

interface ValidationResult {
  canSpawn: boolean;
  checks: ValidationCheck[];
  recommendedModel: string;
  estimatedComplexity: "low" | "medium" | "high";
}

// Resource limits
const LIMITS = {
  maxTotalAgents: 5,
  maxOpusAgents: 1,
  maxSonnetAgents: 3,
  maxHaikuAgents: 5,
};

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

function extractFilesFromDescription(description?: string): string[] {
  if (!description) return [];

  const files: string[] = [];

  // Match common file path patterns
  const patterns = [
    /(?:^|\s)([\w./\\-]+\.[a-zA-Z]{1,4})(?:\s|$|,|;)/gm,  // file.ext
    /(?:^|\s)(src\/[\w./\\-]+)(?:\s|$|,|;)/gm,            // src/path
    /(?:^|\s)(lib\/[\w./\\-]+)(?:\s|$|,|;)/gm,            // lib/path
    /(?:^|\s)(app\/[\w./\\-]+)(?:\s|$|,|;)/gm,            // app/path
    /(?:^|\s)(test\/[\w./\\-]+)(?:\s|$|,|;)/gm,           // test/path
    /(?:^|\s)(tests\/[\w./\\-]+)(?:\s|$|,|;)/gm,          // tests/path
  ];

  for (const pattern of patterns) {
    let match;
    while ((match = pattern.exec(description)) !== null) {
      files.push(match[1]);
    }
  }

  return [...new Set(files)]; // Dedupe
}

function estimateComplexity(task: Task): "low" | "medium" | "high" {
  const description = task.description || "";
  const subject = task.subject || "";
  const text = `${subject} ${description}`.toLowerCase();

  // High complexity indicators
  const highIndicators = [
    "architecture", "design", "refactor", "migrate", "security",
    "performance", "optimization", "complex", "multiple files",
    "database schema", "api design", "authentication"
  ];

  // Low complexity indicators
  const lowIndicators = [
    "documentation", "readme", "comment", "typo", "rename",
    "simple", "config", "update version", "changelog"
  ];

  const highScore = highIndicators.filter(i => text.includes(i)).length;
  const lowScore = lowIndicators.filter(i => text.includes(i)).length;

  if (highScore >= 2 || text.length > 500) return "high";
  if (lowScore >= 2 || text.length < 100) return "low";
  return "medium";
}

function recommendModel(complexity: "low" | "medium" | "high"): string {
  switch (complexity) {
    case "high": return "opus";
    case "medium": return "sonnet";
    case "low": return "haiku";
  }
}

async function validateSpawn(taskId: string, tasksDir: string): Promise<ValidationResult> {
  const tasks = await loadTasks(tasksDir);
  const checks: ValidationCheck[] = [];

  // Check 1: Task exists
  const task = tasks.get(taskId);
  if (!task) {
    checks.push({
      name: "task_exists",
      passed: false,
      message: `Task ${taskId} not found`,
      severity: "error",
    });
    return {
      canSpawn: false,
      checks,
      recommendedModel: "sonnet",
      estimatedComplexity: "medium",
    };
  }

  checks.push({
    name: "task_exists",
    passed: true,
    message: `Task ${taskId} found: "${task.subject}"`,
    severity: "error",
  });

  // Check 2: Task is not already in progress
  if (task.status === "in_progress") {
    checks.push({
      name: "not_in_progress",
      passed: false,
      message: `Task is already in progress${task.owner ? ` (owner: ${task.owner})` : ""}`,
      severity: "error",
    });
  } else if (task.status === "completed") {
    checks.push({
      name: "not_completed",
      passed: false,
      message: "Task is already completed",
      severity: "error",
    });
  } else {
    checks.push({
      name: "status_valid",
      passed: true,
      message: "Task is pending and available",
      severity: "error",
    });
  }

  // Check 3: All blockedBy tasks are completed
  const blockedBy = task.blockedBy || [];
  const incompleteBlockers: string[] = [];

  for (const blockerId of blockedBy) {
    const blocker = tasks.get(blockerId);
    if (!blocker) {
      incompleteBlockers.push(`${blockerId} (not found)`);
    } else if (blocker.status !== "completed") {
      incompleteBlockers.push(`${blockerId} (${blocker.status})`);
    }
  }

  if (incompleteBlockers.length > 0) {
    checks.push({
      name: "dependencies_met",
      passed: false,
      message: `Blocked by incomplete tasks: ${incompleteBlockers.join(", ")}`,
      severity: "error",
    });
  } else if (blockedBy.length > 0) {
    checks.push({
      name: "dependencies_met",
      passed: true,
      message: `All ${blockedBy.length} dependencies completed`,
      severity: "error",
    });
  } else {
    checks.push({
      name: "dependencies_met",
      passed: true,
      message: "No dependencies",
      severity: "error",
    });
  }

  // Check 4: Resource limits
  const inProgressTasks = [...tasks.values()].filter(t => t.status === "in_progress");
  const totalInProgress = inProgressTasks.length;

  if (totalInProgress >= LIMITS.maxTotalAgents) {
    checks.push({
      name: "resource_limit",
      passed: false,
      message: `At max capacity: ${totalInProgress}/${LIMITS.maxTotalAgents} agents running`,
      severity: "error",
    });
  } else {
    checks.push({
      name: "resource_limit",
      passed: true,
      message: `Resource available: ${totalInProgress}/${LIMITS.maxTotalAgents} agents running`,
      severity: "error",
    });
  }

  // Check 5: File conflicts with in_progress tasks
  const taskFiles = task.metadata?.files || extractFilesFromDescription(task.description);
  const conflicts: string[] = [];

  for (const otherTask of inProgressTasks) {
    if (otherTask.id === taskId) continue;

    const otherFiles = otherTask.metadata?.files || extractFilesFromDescription(otherTask.description);
    const overlap = taskFiles.filter(f => otherFiles.some(of =>
      f === of || f.includes(of) || of.includes(f)
    ));

    if (overlap.length > 0) {
      conflicts.push(`Task ${otherTask.id} may touch: ${overlap.join(", ")}`);
    }
  }

  if (conflicts.length > 0) {
    checks.push({
      name: "no_file_conflicts",
      passed: false,
      message: `Potential file conflicts:\n      ${conflicts.join("\n      ")}`,
      severity: "warning",
    });
  } else {
    checks.push({
      name: "no_file_conflicts",
      passed: true,
      message: "No detected file conflicts",
      severity: "warning",
    });
  }

  // Check 6: Description quality
  const descLength = (task.description || "").length;
  if (descLength < 50) {
    checks.push({
      name: "description_quality",
      passed: false,
      message: `Description too short (${descLength} chars). Add more detail for subagent clarity.`,
      severity: "warning",
    });
  } else {
    checks.push({
      name: "description_quality",
      passed: true,
      message: `Description has ${descLength} characters`,
      severity: "warning",
    });
  }

  // Compute result
  const hasErrors = checks.some(c => c.severity === "error" && !c.passed);
  const complexity = estimateComplexity(task);

  return {
    canSpawn: !hasErrors,
    checks,
    recommendedModel: recommendModel(complexity),
    estimatedComplexity: complexity,
  };
}

function formatResult(result: ValidationResult, taskId: string): void {
  console.log("\n🔍 Pre-Spawn Validation\n");
  console.log("=".repeat(50));
  console.log(`Task: ${taskId}`);
  console.log(`Complexity: ${result.estimatedComplexity}`);
  console.log(`Recommended model: ${result.recommendedModel}`);
  console.log("");

  console.log("Checks:");
  for (const check of result.checks) {
    const icon = check.passed ? "✅" : (check.severity === "error" ? "❌" : "⚠️");
    console.log(`   ${icon} ${check.name}: ${check.message}`);
  }

  console.log("\n" + "=".repeat(50));

  if (result.canSpawn) {
    console.log("✅ READY TO SPAWN");
    console.log(`   Recommended: Task(model: "${result.recommendedModel}", ...)`);
  } else {
    console.log("❌ SPAWN BLOCKED");
    console.log("   Fix errors above before spawning agent");
  }
  console.log("");
}

// Main execution
const taskId = process.argv[2];
const explicitListId = process.argv[3];

if (!taskId || taskId.startsWith("--")) {
  console.error("Usage: bun run pre-spawn-validation.ts <task-id> [task-list-id]");
  process.exit(1);
}

const taskListId = await resolveTaskListId(explicitListId);
if (!taskListId) {
  console.error("❌ No task list found. Create tasks first or set CLAUDE_CODE_TASK_LIST_ID.");
  process.exit(1);
}

// ENFORCE shared task list - block spawn if not set up
if (!enforceSharedList()) {
  console.error("💡 Tip: Run init-session.ts first, then retry.");
  process.exit(1);
}

const tasksDir = getTasksDir(taskListId);
const result = await validateSpawn(taskId, tasksDir);
formatResult(result, taskId);

// Output JSON for programmatic use
if (process.argv.includes("--json")) {
  console.log(JSON.stringify(result, null, 2));
}

process.exit(result.canSpawn ? 0 : 1);
