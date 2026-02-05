import { Type } from "@sinclair/typebox";
import * as fs from "fs";
import * as path from "path";

// Recursively find all .md files and build command names
function discoverCommands(dir: string, prefix: string = ""): Array<{ name: string; description: string }> {
  const commands: Array<{ name: string; description: string }> = [];
  
  if (!fs.existsSync(dir)) return commands;
  
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  
  for (const entry of entries) {
    if (entry.name.startsWith(".")) continue;
    
    const fullPath = path.join(dir, entry.name);
    
    if (entry.isDirectory()) {
      // Recurse into subdirectory with namespace prefix
      const namespace = prefix ? `${prefix}:${entry.name}` : entry.name;
      commands.push(...discoverCommands(fullPath, namespace));
    } else if (entry.name.endsWith(".md")) {
      const baseName = entry.name.replace(/\.md$/, "");
      const commandName = prefix ? `${prefix}:${baseName}` : baseName;
      
      // Extract description from frontmatter
      const content = fs.readFileSync(fullPath, "utf-8");
      const descMatch = content.match(/^---[\s\S]*?description:\s*["']?(.+?)["']?\s*$/m);
      const description = descMatch?.[1] || "No description";
      
      commands.push({ name: commandName, description });
    }
  }
  
  return commands.sort((a, b) => a.name.localeCompare(b.name));
}

// Resolve command name to file path
function resolveCommandPath(commandsDir: string, commandName: string): string | null {
  // Handle namespaced commands: "workflows:plan" -> "workflows/plan.md"
  const parts = commandName.split(":");
  const fileName = parts.pop() + ".md";
  const subPath = parts.join("/");
  
  const filePath = path.join(commandsDir, subPath, fileName);
  
  if (fs.existsSync(filePath)) {
    return filePath;
  }
  
  return null;
}

export function createSlashTools(commandsDir: string) {
  const slashListTool = {
    name: "slash_list",
    description: "List available slash commands. Use this to see what commands are available.",
    parameters: Type.Object({}),
    
    async execute() {
      try {
        const commands = discoverCommands(commandsDir);
        
        if (commands.length === 0) {
          return {
            content: [{ type: "text" as const, text: `No commands found in ${commandsDir}` }],
          };
        }
        
        const list = commands.map(c => `/${c.name} — ${c.description}`).join("\n");
        
        return {
          content: [{ 
            type: "text" as const, 
            text: `Available commands (${commands.length}):\n\n${list}` 
          }],
        };
      } catch (err) {
        return {
          content: [{ type: "text" as const, text: `Error listing commands: ${err}` }],
          isError: true,
        };
      }
    },
  };

  const slashReadTool = {
    name: "slash_read",
    description: "Read a slash command file. Returns the full command instructions to follow.",
    parameters: Type.Object({
      command: Type.String({ description: "Command name (e.g., 'plan', 'workflows:review')" }),
    }),
    
    async execute({ command }: { command: string }) {
      try {
        const filePath = resolveCommandPath(commandsDir, command);
        
        if (!filePath) {
          // Try to find similar commands
          const all = discoverCommands(commandsDir);
          const similar = all.filter(c => 
            c.name.includes(command) || command.includes(c.name)
          ).slice(0, 5);
          
          let msg = `Command '${command}' not found.`;
          if (similar.length > 0) {
            msg += `\n\nDid you mean:\n${similar.map(c => `  /${c.name}`).join("\n")}`;
          }
          
          return {
            content: [{ type: "text" as const, text: msg }],
            isError: true,
          };
        }
        
        const content = fs.readFileSync(filePath, "utf-8");
        
        return {
          content: [{ 
            type: "text" as const, 
            text: content 
          }],
        };
      } catch (err) {
        return {
          content: [{ type: "text" as const, text: `Error reading command: ${err}` }],
          isError: true,
        };
      }
    },
  };

  return { slashListTool, slashReadTool };
}
