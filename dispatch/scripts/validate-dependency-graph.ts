#!/usr/bin/env bun
/**
 * validate-dependency-graph.ts
 *
 * Validates the task dependency graph for correctness:
 * - Detects circular dependencies using DFS
 * - Identifies orphaned tasks (no connections)
 * - Validates all blockedBy references point to existing tasks
 * - Computes critical path and parallel execution groups
 *
 * Usage: bun run scripts/validate-dependency-graph.ts [task-list-id]
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
  status: "pending" | "in_progress" | "completed";
  blockedBy?: string[];
  blocks?: string[];
  owner?: string;
}

interface ValidationResult {
  valid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
  stats: GraphStats;
}

interface ValidationError {
  type: "circular_dependency" | "missing_reference" | "self_reference";
  message: string;
  taskIds: string[];
}

interface ValidationWarning {
  type: "orphaned_task" | "long_chain" | "wide_parallelism";
  message: string;
  taskIds: string[];
}

interface GraphStats {
  totalTasks: number;
  pendingTasks: number;
  inProgressTasks: number;
  completedTasks: number;
  maxDepth: number;
  parallelGroups: string[][];
  criticalPath: string[];
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
  } catch (error) {
    console.error(`Error reading tasks directory: ${tasksDir}`);
    console.error("Make sure the task list exists.");
    process.exit(1);
  }

  return tasks;
}

function detectCycles(tasks: Map<string, Task>): ValidationError[] {
  const errors: ValidationError[] = [];
  const visited = new Set<string>();
  const recursionStack = new Set<string>();
  const cyclePaths: string[][] = [];

  function dfs(taskId: string, path: string[]): boolean {
    visited.add(taskId);
    recursionStack.add(taskId);

    const task = tasks.get(taskId);
    if (!task) return false;

    const dependencies = task.blockedBy || [];

    for (const depId of dependencies) {
      if (!visited.has(depId)) {
        if (dfs(depId, [...path, depId])) {
          return true;
        }
      } else if (recursionStack.has(depId)) {
        // Found cycle
        const cycleStart = path.indexOf(depId);
        const cycle = cycleStart >= 0
          ? path.slice(cycleStart).concat(depId)
          : [...path, depId];
        cyclePaths.push(cycle);
        return true;
      }
    }

    recursionStack.delete(taskId);
    return false;
  }

  for (const taskId of tasks.keys()) {
    if (!visited.has(taskId)) {
      dfs(taskId, [taskId]);
    }
  }

  for (const cycle of cyclePaths) {
    errors.push({
      type: "circular_dependency",
      message: `Circular dependency detected: ${cycle.join(" → ")}`,
      taskIds: cycle,
    });
  }

  return errors;
}

function validateReferences(tasks: Map<string, Task>): ValidationError[] {
  const errors: ValidationError[] = [];

  for (const [taskId, task] of tasks) {
    // Check self-reference
    if (task.blockedBy?.includes(taskId)) {
      errors.push({
        type: "self_reference",
        message: `Task ${taskId} references itself in blockedBy`,
        taskIds: [taskId],
      });
    }

    // Check missing references
    for (const depId of task.blockedBy || []) {
      if (!tasks.has(depId)) {
        errors.push({
          type: "missing_reference",
          message: `Task ${taskId} references non-existent task ${depId} in blockedBy`,
          taskIds: [taskId, depId],
        });
      }
    }

    for (const blockId of task.blocks || []) {
      if (!tasks.has(blockId)) {
        errors.push({
          type: "missing_reference",
          message: `Task ${taskId} references non-existent task ${blockId} in blocks`,
          taskIds: [taskId, blockId],
        });
      }
    }
  }

  return errors;
}

function findOrphanedTasks(tasks: Map<string, Task>): ValidationWarning[] {
  const warnings: ValidationWarning[] = [];
  const hasIncoming = new Set<string>();
  const hasOutgoing = new Set<string>();

  for (const [taskId, task] of tasks) {
    if (task.blockedBy && task.blockedBy.length > 0) {
      hasIncoming.add(taskId);
      task.blockedBy.forEach(id => hasOutgoing.add(id));
    }
    if (task.blocks && task.blocks.length > 0) {
      hasOutgoing.add(taskId);
      task.blocks.forEach(id => hasIncoming.add(id));
    }
  }

  const orphaned: string[] = [];
  for (const taskId of tasks.keys()) {
    if (!hasIncoming.has(taskId) && !hasOutgoing.has(taskId)) {
      orphaned.push(taskId);
    }
  }

  if (orphaned.length > 0 && tasks.size > 1) {
    warnings.push({
      type: "orphaned_task",
      message: `Found ${orphaned.length} task(s) with no dependencies: ${orphaned.join(", ")}`,
      taskIds: orphaned,
    });
  }

  return warnings;
}

function computeParallelGroups(tasks: Map<string, Task>): string[][] {
  const groups: string[][] = [];
  const completed = new Set<string>();

  // Add already completed tasks
  for (const [taskId, task] of tasks) {
    if (task.status === "completed") {
      completed.add(taskId);
    }
  }

  let remaining = new Set(
    [...tasks.keys()].filter(id => !completed.has(id))
  );

  while (remaining.size > 0) {
    const group: string[] = [];

    for (const taskId of remaining) {
      const task = tasks.get(taskId);
      if (!task) continue; // Skip if task was removed
      const blockedBy = task.blockedBy || [];

      // Task is ready if all its dependencies are completed
      const isReady = blockedBy.every(depId => completed.has(depId));

      if (isReady) {
        group.push(taskId);
      }
    }

    if (group.length === 0) {
      // No progress possible - likely circular dependency
      break;
    }

    groups.push(group);
    group.forEach(id => {
      completed.add(id);
      remaining.delete(id);
    });
  }

  return groups;
}

function computeCriticalPath(tasks: Map<string, Task>): string[] {
  const depths = new Map<string, number>();
  const paths = new Map<string, string[]>();

  function getDepth(taskId: string, visited: Set<string> = new Set()): number {
    if (visited.has(taskId)) return 0; // Cycle protection
    if (depths.has(taskId)) return depths.get(taskId)!;

    visited.add(taskId);
    const task = tasks.get(taskId);
    if (!task) return 0;

    const blockedBy = task.blockedBy || [];
    if (blockedBy.length === 0) {
      depths.set(taskId, 1);
      paths.set(taskId, [taskId]);
      return 1;
    }

    let maxDepth = 0;
    let longestPath: string[] = [];

    for (const depId of blockedBy) {
      const depDepth = getDepth(depId, visited);
      if (depDepth > maxDepth) {
        maxDepth = depDepth;
        longestPath = paths.get(depId) || [];
      }
    }

    const depth = maxDepth + 1;
    depths.set(taskId, depth);
    paths.set(taskId, [...longestPath, taskId]);

    return depth;
  }

  let maxDepth = 0;
  let criticalPath: string[] = [];

  for (const taskId of tasks.keys()) {
    const depth = getDepth(taskId);
    if (depth > maxDepth) {
      maxDepth = depth;
      criticalPath = paths.get(taskId) || [];
    }
  }

  return criticalPath;
}

function computeStats(tasks: Map<string, Task>): GraphStats {
  let pending = 0, inProgress = 0, completed = 0;

  for (const task of tasks.values()) {
    switch (task.status) {
      case "pending": pending++; break;
      case "in_progress": inProgress++; break;
      case "completed": completed++; break;
    }
  }

  const parallelGroups = computeParallelGroups(tasks);
  const criticalPath = computeCriticalPath(tasks);

  return {
    totalTasks: tasks.size,
    pendingTasks: pending,
    inProgressTasks: inProgress,
    completedTasks: completed,
    maxDepth: criticalPath.length,
    parallelGroups,
    criticalPath,
  };
}

async function validateGraph(tasksDir: string): Promise<ValidationResult> {
  const tasks = await loadTasks(tasksDir);

  if (tasks.size === 0) {
    return {
      valid: true,
      errors: [],
      warnings: [],
      stats: {
        totalTasks: 0,
        pendingTasks: 0,
        inProgressTasks: 0,
        completedTasks: 0,
        maxDepth: 0,
        parallelGroups: [],
        criticalPath: [],
      },
    };
  }

  const errors: ValidationError[] = [
    ...detectCycles(tasks),
    ...validateReferences(tasks),
  ];

  const warnings: ValidationWarning[] = [
    ...findOrphanedTasks(tasks),
  ];

  const stats = computeStats(tasks);

  // Add warning for very deep chains
  if (stats.maxDepth > 10) {
    warnings.push({
      type: "long_chain",
      message: `Dependency chain depth of ${stats.maxDepth} may cause slow execution`,
      taskIds: stats.criticalPath,
    });
  }

  // Add warning for wide parallelism
  const maxParallel = Math.max(...stats.parallelGroups.map(g => g.length), 0);
  if (maxParallel > 5) {
    warnings.push({
      type: "wide_parallelism",
      message: `Group with ${maxParallel} parallel tasks may exceed resource limits`,
      taskIds: stats.parallelGroups.find(g => g.length === maxParallel) || [],
    });
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings,
    stats,
  };
}

function formatResult(result: ValidationResult): void {
  console.log("\n📊 Task Dependency Graph Validation\n");
  console.log("=".repeat(50));

  // Stats
  console.log("\n📈 Statistics:");
  console.log(`   Total tasks: ${result.stats.totalTasks}`);
  console.log(`   Pending: ${result.stats.pendingTasks}`);
  console.log(`   In Progress: ${result.stats.inProgressTasks}`);
  console.log(`   Completed: ${result.stats.completedTasks}`);
  console.log(`   Max depth: ${result.stats.maxDepth}`);

  // Parallel groups
  if (result.stats.parallelGroups.length > 0) {
    console.log("\n🔀 Execution Phases:");
    result.stats.parallelGroups.forEach((group, i) => {
      console.log(`   Phase ${i + 1}: [${group.join(", ")}]`);
    });
  }

  // Critical path
  if (result.stats.criticalPath.length > 0) {
    console.log("\n🛤️  Critical Path:");
    console.log(`   ${result.stats.criticalPath.join(" → ")}`);
  }

  // Errors
  if (result.errors.length > 0) {
    console.log("\n❌ Errors:");
    for (const error of result.errors) {
      console.log(`   [${error.type}] ${error.message}`);
    }
  }

  // Warnings
  if (result.warnings.length > 0) {
    console.log("\n⚠️  Warnings:");
    for (const warning of result.warnings) {
      console.log(`   [${warning.type}] ${warning.message}`);
    }
  }

  // Summary
  console.log("\n" + "=".repeat(50));
  if (result.valid) {
    console.log("✅ Graph is valid");
  } else {
    console.log("❌ Graph has errors - fix before proceeding");
  }
  console.log("");
}

// Main execution
const explicitId = process.argv[2];
const taskListId = await resolveTaskListId(explicitId);

if (!taskListId) {
  console.error("❌ No task list found. Create tasks first or set CLAUDE_CODE_TASK_LIST_ID.");
  process.exit(1);
}

const tasksDir = getTasksDir(taskListId);
const result = await validateGraph(tasksDir);
formatResult(result);

// Exit with error code if invalid
if (!result.valid) {
  process.exit(1);
}
