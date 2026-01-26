#!/usr/bin/env bun
/**
 * list-archives.ts
 *
 * List and inspect archived task lists.
 *
 * Usage:
 *   bun run list-archives.ts                    # List all archives
 *   bun run list-archives.ts <archive-name>     # Show archive details
 *   bun run list-archives.ts --restore <name>   # Restore archive to active tasks
 */

import { readdir, readFile, copyFile, mkdir } from "fs/promises";
import { join } from "path";
import { homedir } from "os";
import { existsSync } from "fs";

interface ArchiveManifest {
  listId: string;
  archivedAt: string;
  taskCount: number;
  completedCount?: number;
  pendingCount?: number;
  inProgressCount?: number;
  sourceDir?: string;
}

interface Task {
  id: string;
  subject: string;
  status: string;
  owner?: string;
}

const archiveBaseDir = join(homedir(), ".claude", "tasks-archive");
const tasksBaseDir = join(homedir(), ".claude", "tasks");
const args = process.argv.slice(2);

const restoreMode = args.includes("--restore") || args.includes("-r");
const archiveName = args.find(a => !a.startsWith("-"));

if (args.includes("--help") || args.includes("-h")) {
  console.log(`
list-archives.ts - List and inspect archived task lists

Usage:
  bun run list-archives.ts                    List all archives
  bun run list-archives.ts <archive-name>     Show archive details
  bun run list-archives.ts --restore <name>   Restore archive to active tasks

Options:
  --restore, -r     Restore an archive back to active task list
  --help, -h        Show this help message

Archive location: ~/.claude/tasks-archive/

Examples:
  # List all archives
  bun run list-archives.ts

  # View specific archive
  bun run list-archives.ts my-feature-20260125-143022

  # Restore an archive
  bun run list-archives.ts --restore my-feature-20260125-143022
`);
  process.exit(0);
}

async function listArchives(): Promise<void> {
  if (!existsSync(archiveBaseDir)) {
    console.log("\nNo archives found.");
    console.log(`Archive location: ${archiveBaseDir}\n`);
    return;
  }

  const entries = await readdir(archiveBaseDir, { withFileTypes: true });
  const archives: { name: string; manifest: ArchiveManifest }[] = [];

  for (const entry of entries) {
    if (!entry.isDirectory()) continue;

    const manifestPath = join(archiveBaseDir, entry.name, "manifest.json");
    if (existsSync(manifestPath)) {
      try {
        const manifest = JSON.parse(await readFile(manifestPath, "utf-8")) as ArchiveManifest;
        archives.push({ name: entry.name, manifest });
      } catch {}
    }
  }

  if (archives.length === 0) {
    console.log("\nNo archives found.");
    return;
  }

  // Sort by archived date (most recent first)
  archives.sort((a, b) =>
    new Date(b.manifest.archivedAt).getTime() - new Date(a.manifest.archivedAt).getTime()
  );

  console.log("\n📦 Task Archives\n");
  console.log("═".repeat(70));

  for (const { name, manifest } of archives) {
    const date = new Date(manifest.archivedAt).toLocaleString();
    const stats = [];
    if (manifest.completedCount !== undefined) stats.push(`✓${manifest.completedCount}`);
    if (manifest.pendingCount !== undefined) stats.push(`○${manifest.pendingCount}`);
    if (manifest.inProgressCount !== undefined) stats.push(`●${manifest.inProgressCount}`);

    const statsStr = stats.length > 0 ? ` [${stats.join(" ")}]` : "";

    console.log(`\n  ${name}`);
    console.log(`    List: ${manifest.listId}`);
    console.log(`    Date: ${date}`);
    console.log(`    Tasks: ${manifest.taskCount}${statsStr}`);
  }

  console.log("\n" + "═".repeat(70));
  console.log(`\nTotal: ${archives.length} archive(s)`);
  console.log(`Location: ${archiveBaseDir}\n`);
}

async function showArchiveDetails(name: string): Promise<void> {
  const archiveDir = join(archiveBaseDir, name);

  if (!existsSync(archiveDir)) {
    console.error(`❌ Archive not found: ${name}`);
    console.error(`\nRun without arguments to list available archives.`);
    process.exit(1);
  }

  const manifestPath = join(archiveDir, "manifest.json");
  if (!existsSync(manifestPath)) {
    console.error(`❌ Invalid archive (no manifest): ${name}`);
    process.exit(1);
  }

  const manifest = JSON.parse(await readFile(manifestPath, "utf-8")) as ArchiveManifest;

  // Load tasks
  const tasks: Task[] = [];
  const files = await readdir(archiveDir);
  for (const file of files) {
    if (file.endsWith(".json") && file !== "manifest.json") {
      try {
        const task = JSON.parse(await readFile(join(archiveDir, file), "utf-8")) as Task;
        tasks.push(task);
      } catch {}
    }
  }

  // Sort tasks by ID
  tasks.sort((a, b) => parseInt(a.id) - parseInt(b.id));

  console.log("\n📦 Archive Details\n");
  console.log("═".repeat(60));
  console.log(`\nName:     ${name}`);
  console.log(`List ID:  ${manifest.listId}`);
  console.log(`Archived: ${new Date(manifest.archivedAt).toLocaleString()}`);
  console.log(`Tasks:    ${manifest.taskCount}`);

  if (tasks.length > 0) {
    console.log("\nTasks:");
    for (const task of tasks) {
      const statusIcon = task.status === "completed" ? "✓" : task.status === "in_progress" ? "●" : "○";
      const ownerStr = task.owner ? ` (${task.owner})` : "";
      console.log(`  ${statusIcon} ${task.id}: ${task.subject}${ownerStr}`);
    }
  }

  console.log("\n" + "═".repeat(60));
  console.log(`\nTo restore: bun run list-archives.ts --restore ${name}\n`);
}

async function restoreArchive(name: string): Promise<void> {
  const archiveDir = join(archiveBaseDir, name);

  if (!existsSync(archiveDir)) {
    console.error(`❌ Archive not found: ${name}`);
    process.exit(1);
  }

  const manifestPath = join(archiveDir, "manifest.json");
  if (!existsSync(manifestPath)) {
    console.error(`❌ Invalid archive (no manifest): ${name}`);
    process.exit(1);
  }

  const manifest = JSON.parse(await readFile(manifestPath, "utf-8")) as ArchiveManifest;
  const targetDir = join(tasksBaseDir, manifest.listId);

  // Check if target already has tasks
  if (existsSync(targetDir)) {
    const existingFiles = await readdir(targetDir);
    const existingTasks = existingFiles.filter(f => f.endsWith(".json")).length;
    if (existingTasks > 0) {
      console.error(`❌ Task list '${manifest.listId}' already has ${existingTasks} task(s).`);
      console.error(`   Delete or rename it first, then try again.`);
      process.exit(1);
    }
  }

  // Create target directory
  await mkdir(targetDir, { recursive: true });

  // Copy task files (not manifest)
  const files = await readdir(archiveDir);
  let restoredCount = 0;

  for (const file of files) {
    if (file.endsWith(".json") && file !== "manifest.json") {
      await copyFile(join(archiveDir, file), join(targetDir, file));
      restoredCount++;
    }
  }

  console.log(`\n✅ Restored ${restoredCount} task(s) to '${manifest.listId}'`);
  console.log(`\nTo use this list:`);
  console.log(`  cc ${manifest.listId}\n`);
}

// Main
if (restoreMode && archiveName) {
  await restoreArchive(archiveName);
} else if (archiveName) {
  await showArchiveDetails(archiveName);
} else {
  await listArchives();
}
