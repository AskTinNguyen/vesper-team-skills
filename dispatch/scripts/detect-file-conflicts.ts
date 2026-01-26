#!/usr/bin/env bun
/**
 * detect-file-conflicts.ts
 *
 * Analyzes tasks for potential file conflicts:
 * - Extracts file paths from task descriptions
 * - Identifies overlapping file ownership between parallel tasks
 * - Suggests blockedBy relationships to resolve conflicts
 *
 * Usage: bun run scripts/detect-file-conflicts.ts [task-list-id]
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
  blockedBy?: string[];
  metadata?: {
    files?: string[];
  };
}

interface FileOwnership {
  file: string;
  tasks: string[];
}

interface Conflict {
  file: string;
  tasks: Task[];
  severity: "high" | "medium" | "low";
  suggestion: string;
}

interface ConflictReport {
  conflicts: Conflict[];
  fileOwnership: FileOwnership[];
  safeParallelGroups: string[][];
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
    console.error(`Error reading tasks directory: ${tasksDir}`);
  }

  return tasks;
}

function extractFiles(task: Task): string[] {
  // Use explicit metadata if available
  if (task.metadata?.files && task.metadata.files.length > 0) {
    return task.metadata.files;
  }

  const text = `${task.subject || ""} ${task.description || ""}`;
  const files: string[] = [];

  // Common file patterns
  const patterns = [
    // Explicit file paths
    /(?:file|path|modify|edit|create|update|change)s?\s*[:\s]+([^\s,]+\.[a-zA-Z]{1,5})/gi,
    // Standard paths
    /((?:src|lib|app|test|tests|spec|components|pages|api|services|utils|hooks|models|controllers|views)\/[\w./\\-]+)/g,
    // Files with extensions
    /\b([\w-]+\.(?:ts|tsx|js|jsx|py|rb|go|rs|java|css|scss|html|json|yaml|yml|md|sql))\b/g,
  ];

  for (const pattern of patterns) {
    let match;
    while ((match = pattern.exec(text)) !== null) {
      const file = match[1].trim();
      if (file.length > 2 && !files.includes(file)) {
        files.push(file);
      }
    }
  }

  // Also extract directory patterns
  const dirPatterns = [
    /(?:in|under|within)\s+(?:the\s+)?([a-zA-Z]+\/[\w-]+)/gi,
    /\b(components\/[\w-]+)/g,
    /\b(pages\/[\w-]+)/g,
  ];

  for (const pattern of dirPatterns) {
    let match;
    while ((match = pattern.exec(text)) !== null) {
      const dir = match[1].trim();
      if (!files.includes(dir)) {
        files.push(dir);
      }
    }
  }

  return files;
}

function filesOverlap(file1: string, file2: string): boolean {
  // Exact match
  if (file1 === file2) return true;

  // Normalize paths
  const norm1 = file1.replace(/\\/g, "/").toLowerCase();
  const norm2 = file2.replace(/\\/g, "/").toLowerCase();

  if (norm1 === norm2) return true;

  // One is parent directory of the other
  if (norm1.startsWith(norm2 + "/") || norm2.startsWith(norm1 + "/")) {
    return true;
  }

  // Same base filename in same directory structure
  const base1 = norm1.split("/").pop() || "";
  const base2 = norm2.split("/").pop() || "";

  if (base1 === base2 && base1.includes(".")) {
    // Same filename - likely a conflict
    return true;
  }

  return false;
}

function analyzeConflicts(tasks: Map<string, Task>): ConflictReport {
  // Only consider non-completed tasks
  const activeTasks = [...tasks.values()].filter(t => t.status !== "completed");

  // Build file ownership map
  const fileToTasks = new Map<string, Task[]>();

  for (const task of activeTasks) {
    const files = extractFiles(task);

    for (const file of files) {
      const existing = fileToTasks.get(file) || [];
      existing.push(task);
      fileToTasks.set(file, existing);
    }
  }

  // Find conflicts (files owned by multiple tasks)
  const conflicts: Conflict[] = [];
  const seenConflicts = new Set<string>();

  for (const task1 of activeTasks) {
    const files1 = extractFiles(task1);

    for (const task2 of activeTasks) {
      if (task1.id >= task2.id) continue; // Avoid duplicates

      const files2 = extractFiles(task2);

      // Check if tasks already have dependency
      const hasDependency =
        task1.blockedBy?.includes(task2.id) ||
        task2.blockedBy?.includes(task1.id);

      for (const f1 of files1) {
        for (const f2 of files2) {
          if (filesOverlap(f1, f2)) {
            const conflictKey = [task1.id, task2.id].sort().join("-");
            if (seenConflicts.has(conflictKey)) continue;
            seenConflicts.add(conflictKey);

            // Determine severity
            let severity: "high" | "medium" | "low" = "medium";
            if (f1 === f2) {
              severity = "high"; // Exact same file
            } else if (hasDependency) {
              severity = "low"; // Already serialized
            }

            let suggestion: string;
            if (hasDependency) {
              suggestion = "Already serialized via dependency";
            } else {
              suggestion = `Add: TaskUpdate(taskId: "${task2.id}", addBlockedBy: ["${task1.id}"])`;
            }

            conflicts.push({
              file: f1 === f2 ? f1 : `${f1} / ${f2}`,
              tasks: [task1, task2],
              severity,
              suggestion,
            });
          }
        }
      }
    }
  }

  // Sort by severity
  conflicts.sort((a, b) => {
    const order = { high: 0, medium: 1, low: 2 };
    return order[a.severity] - order[b.severity];
  });

  // Build file ownership report
  const fileOwnership: FileOwnership[] = [];
  for (const [file, owningTasks] of fileToTasks) {
    if (owningTasks.length > 0) {
      fileOwnership.push({
        file,
        tasks: owningTasks.map(t => t.id),
      });
    }
  }

  // Identify safe parallel groups (tasks with no file overlap)
  const safeParallelGroups = computeSafeGroups(activeTasks);

  return {
    conflicts,
    fileOwnership,
    safeParallelGroups,
  };
}

function computeSafeGroups(tasks: Task[]): string[][] {
  const groups: string[][] = [];
  const assigned = new Set<string>();

  for (const task of tasks) {
    if (assigned.has(task.id)) continue;

    const group = [task.id];
    const taskFiles = extractFiles(task);

    for (const other of tasks) {
      if (other.id === task.id || assigned.has(other.id)) continue;

      const otherFiles = extractFiles(other);

      // Check if there's any overlap with any task in the current group
      let hasOverlap = false;
      for (const gTaskId of group) {
        const gTask = tasks.find(t => t.id === gTaskId);
        if (!gTask) continue; // Skip if task not found
        const gFiles = extractFiles(gTask);

        for (const f1 of otherFiles) {
          for (const f2 of gFiles) {
            if (filesOverlap(f1, f2)) {
              hasOverlap = true;
              break;
            }
          }
          if (hasOverlap) break;
        }
        if (hasOverlap) break;
      }

      if (!hasOverlap) {
        group.push(other.id);
        assigned.add(other.id);
      }
    }

    if (group.length > 0) {
      group.forEach(id => assigned.add(id));
      groups.push(group);
    }
  }

  return groups;
}

function formatReport(report: ConflictReport): void {
  console.log("\n📁 File Conflict Analysis\n");
  console.log("=".repeat(50));

  // File ownership summary
  console.log("\n📋 File Ownership:");
  if (report.fileOwnership.length === 0) {
    console.log("   No files detected in task descriptions");
  } else {
    for (const ownership of report.fileOwnership.slice(0, 20)) {
      console.log(`   ${ownership.file}`);
      console.log(`      Tasks: ${ownership.tasks.join(", ")}`);
    }
    if (report.fileOwnership.length > 20) {
      console.log(`   ... and ${report.fileOwnership.length - 20} more files`);
    }
  }

  // Conflicts
  console.log("\n⚠️  Potential Conflicts:");
  if (report.conflicts.length === 0) {
    console.log("   No conflicts detected");
  } else {
    for (const conflict of report.conflicts) {
      const icon = conflict.severity === "high" ? "🔴" :
                   conflict.severity === "medium" ? "🟡" : "🟢";
      console.log(`\n   ${icon} ${conflict.severity.toUpperCase()}: ${conflict.file}`);
      console.log(`      Tasks: ${conflict.tasks.map(t => `${t.id} (${t.subject})`).join(" vs ")}`);
      console.log(`      ${conflict.suggestion}`);
    }
  }

  // Safe parallel groups
  console.log("\n✅ Safe Parallel Groups:");
  if (report.safeParallelGroups.length === 0) {
    console.log("   No safe parallel execution possible");
  } else {
    for (let i = 0; i < report.safeParallelGroups.length; i++) {
      const group = report.safeParallelGroups[i];
      console.log(`   Group ${i + 1}: [${group.join(", ")}]`);
    }
  }

  console.log("\n" + "=".repeat(50));

  const highCount = report.conflicts.filter(c => c.severity === "high").length;
  if (highCount > 0) {
    console.log(`❌ ${highCount} high-severity conflict(s) - add dependencies before parallel execution`);
  } else if (report.conflicts.length > 0) {
    console.log(`⚠️  ${report.conflicts.length} potential conflict(s) - review before parallel execution`);
  } else {
    console.log("✅ No conflicts detected - safe for parallel execution");
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
const tasks = await loadTasks(tasksDir);

if (tasks.size === 0) {
  console.log("No tasks found in task list");
  process.exit(0);
}

const report = analyzeConflicts(tasks);
formatReport(report);

// Exit with error if high-severity conflicts
const highConflicts = report.conflicts.filter(c => c.severity === "high").length;
process.exit(highConflicts > 0 ? 1 : 0);
