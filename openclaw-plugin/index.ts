import type { OpenClawPluginApi } from "openclaw/plugin-sdk";
import { createSlashTools } from "./src/slash-tools.js";
import { createTaskTools } from "./src/task-tools.js";
import * as path from "path";
import * as os from "os";

interface PluginConfig {
  commandsDir?: string;
  tasksDir?: string;
}

function resolvePath(p: string): string {
  if (p.startsWith("~")) {
    return path.join(os.homedir(), p.slice(1));
  }
  return p;
}

const plugin = {
  id: "agent-tools",
  name: "Atherlab Agent Tools",
  description: "Slash commands and task list tools for OpenClaw agents",
  configSchema: {
    type: "object",
    additionalProperties: false,
    properties: {
      commandsDir: { type: "string" },
      tasksDir: { type: "string" },
    },
  },

  register(api: OpenClawPluginApi) {
    // Get config with defaults
    const config = (api.config?.plugins?.entries?.["agent-tools"]?.config ?? {}) as PluginConfig;
    
    const commandsDir = resolvePath(config.commandsDir ?? "~/.openclaw/commands");
    const tasksDir = resolvePath(config.tasksDir ?? "~/.openclaw/tasks");

    // Register slash command tools
    const { slashListTool, slashReadTool } = createSlashTools(commandsDir);
    api.registerTool(slashListTool);
    api.registerTool(slashReadTool);

    // Register task tools
    const { taskCreateTool, taskUpdateTool, taskGetTool, taskListTool } = createTaskTools(tasksDir);
    api.registerTool(taskCreateTool);
    api.registerTool(taskUpdateTool);
    api.registerTool(taskGetTool);
    api.registerTool(taskListTool);

    api.logger.info(`[agent-tools] Loaded: slash_list, slash_read, task_create, task_update, task_get, task_list`);
    api.logger.info(`[agent-tools] Commands: ${commandsDir}`);
    api.logger.info(`[agent-tools] Tasks: ${tasksDir}`);
  },
};

export default plugin;
