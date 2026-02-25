import { Type } from "@sinclair/typebox";
import * as fs from "fs";
import * as path from "path";
import { randomUUID } from "crypto";

interface Task {
  id: string;
  description: string;
  status: "pending" | "in_progress" | "done";
  priority: "urgent" | "high" | "normal" | "low";
  owner?: string;
  blockedBy: string[];
  createdAt: string;
  updatedAt: string;
}

function getTasksFile(tasksDir: string): string {
  return path.join(tasksDir, "tasks.json");
}

function loadTasks(tasksDir: string): Task[] {
  const file = getTasksFile(tasksDir);
  if (!fs.existsSync(file)) {
    return [];
  }
  return JSON.parse(fs.readFileSync(file, "utf-8"));
}

function saveTasks(tasksDir: string, tasks: Task[]): void {
  fs.mkdirSync(tasksDir, { recursive: true });
  fs.writeFileSync(getTasksFile(tasksDir), JSON.stringify(tasks, null, 2));
}

function isBlocked(task: Task, allTasks: Task[]): boolean {
  if (!task.blockedBy || task.blockedBy.length === 0) return false;
  return task.blockedBy.some(blockerId => {
    const blocker = allTasks.find(t => t.id === blockerId);
    return blocker && blocker.status !== "done";
  });
}

function formatTask(task: Task, allTasks: Task[]): string {
  const statusIcon = task.status === "pending" ? "⏳" : task.status === "in_progress" ? "🔄" : "✅";
  const priorityIcon = task.priority === "urgent" ? "🔴" : task.priority === "high" ? "🟠" : task.priority === "normal" ? "🟡" : "⚪";
  const blocked = isBlocked(task, allTasks) ? " 🚫 BLOCKED" : "";
  const owner = task.owner ? ` (@${task.owner})` : "";
  const blockedBy = task.blockedBy?.length > 0 ? ` [waiting: ${task.blockedBy.join(", ")}]` : "";
  
  return `${statusIcon} ${priorityIcon} [${task.id}] ${task.description}${owner}${blocked}${blockedBy}`;
}

export function createTaskTools(tasksDir: string) {
  const taskCreateTool = {
    name: "task_create",
    description: "Create a new task. Tasks can have dependencies (blockedBy) and priorities.",
    parameters: Type.Object({
      description: Type.String({ description: "Task description" }),
      priority: Type.Optional(Type.Union([
        Type.Literal("urgent"),
        Type.Literal("high"),
        Type.Literal("normal"),
        Type.Literal("low"),
      ])),
      owner: Type.Optional(Type.String({ description: "Owner/assignee" })),
      blockedBy: Type.Optional(Type.Array(Type.String(), { description: "Task IDs that must complete first" })),
    }),
    
    async execute(params: { description: string; priority?: string; owner?: string; blockedBy?: string[] }) {
      try {
        const tasks = loadTasks(tasksDir);
        
        const task: Task = {
          id: randomUUID().slice(0, 8),
          description: params.description,
          status: "pending",
          priority: (params.priority as Task["priority"]) || "normal",
          owner: params.owner,
          blockedBy: params.blockedBy || [],
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        };
        
        tasks.push(task);
        saveTasks(tasksDir, tasks);
        
        return {
          content: [{ 
            type: "text" as const, 
            text: `✅ Task created:\n${formatTask(task, tasks)}` 
          }],
        };
      } catch (err) {
        return {
          content: [{ type: "text" as const, text: `Error creating task: ${err}` }],
          isError: true,
        };
      }
    },
  };

  const taskUpdateTool = {
    name: "task_update",
    description: "Update a task's status, priority, or owner.",
    parameters: Type.Object({
      id: Type.String({ description: "Task ID" }),
      status: Type.Optional(Type.Union([
        Type.Literal("pending"),
        Type.Literal("in_progress"),
        Type.Literal("done"),
      ])),
      priority: Type.Optional(Type.Union([
        Type.Literal("urgent"),
        Type.Literal("high"),
        Type.Literal("normal"),
        Type.Literal("low"),
      ])),
      owner: Type.Optional(Type.String()),
    }),
    
    async execute(params: { id: string; status?: string; priority?: string; owner?: string }) {
      try {
        const tasks = loadTasks(tasksDir);
        const task = tasks.find(t => t.id === params.id);
        
        if (!task) {
          return {
            content: [{ type: "text" as const, text: `Task '${params.id}' not found.` }],
            isError: true,
          };
        }
        
        if (params.status) task.status = params.status as Task["status"];
        if (params.priority) task.priority = params.priority as Task["priority"];
        if (params.owner !== undefined) task.owner = params.owner;
        task.updatedAt = new Date().toISOString();
        
        saveTasks(tasksDir, tasks);
        
        return {
          content: [{ 
            type: "text" as const, 
            text: `✅ Task updated:\n${formatTask(task, tasks)}` 
          }],
        };
      } catch (err) {
        return {
          content: [{ type: "text" as const, text: `Error updating task: ${err}` }],
          isError: true,
        };
      }
    },
  };

  const taskGetTool = {
    name: "task_get",
    description: "Get a single task by ID.",
    parameters: Type.Object({
      id: Type.String({ description: "Task ID" }),
    }),
    
    async execute({ id }: { id: string }) {
      try {
        const tasks = loadTasks(tasksDir);
        const task = tasks.find(t => t.id === id);
        
        if (!task) {
          return {
            content: [{ type: "text" as const, text: `Task '${id}' not found.` }],
            isError: true,
          };
        }
        
        return {
          content: [{ 
            type: "text" as const, 
            text: JSON.stringify(task, null, 2) 
          }],
        };
      } catch (err) {
        return {
          content: [{ type: "text" as const, text: `Error getting task: ${err}` }],
          isError: true,
        };
      }
    },
  };

  const taskListTool = {
    name: "task_list",
    description: "List tasks with optional filters.",
    parameters: Type.Object({
      status: Type.Optional(Type.String({ description: "Filter by status" })),
      owner: Type.Optional(Type.String({ description: "Filter by owner" })),
      unblockedOnly: Type.Optional(Type.Boolean({ description: "Only show unblocked tasks" })),
    }),
    
    async execute(params: { status?: string; owner?: string; unblockedOnly?: boolean }) {
      try {
        let tasks = loadTasks(tasksDir);
        
        if (params.status) {
          tasks = tasks.filter(t => t.status === params.status);
        }
        if (params.owner) {
          tasks = tasks.filter(t => t.owner === params.owner);
        }
        if (params.unblockedOnly) {
          const allTasks = loadTasks(tasksDir);
          tasks = tasks.filter(t => !isBlocked(t, allTasks));
        }
        
        if (tasks.length === 0) {
          return {
            content: [{ type: "text" as const, text: "No tasks found." }],
          };
        }
        
        const allTasks = loadTasks(tasksDir);
        const list = tasks.map(t => formatTask(t, allTasks)).join("\n");
        
        return {
          content: [{ 
            type: "text" as const, 
            text: `📋 Tasks (${tasks.length}):\n\n${list}` 
          }],
        };
      } catch (err) {
        return {
          content: [{ type: "text" as const, text: `Error listing tasks: ${err}` }],
          isError: true,
        };
      }
    },
  };

  return { taskCreateTool, taskUpdateTool, taskGetTool, taskListTool };
}
