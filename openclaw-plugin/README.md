# OpenClaw Agent Tools Plugin

Slash commands and task list tools for OpenClaw agents.

## What's Included

**Tools:**
- `slash_list` — List all available slash commands
- `slash_read` — Read a command file to execute
- `task_create` — Create tasks with priorities and dependencies
- `task_update` — Update task status/priority/owner
- `task_get` — Get a single task
- `task_list` — List and filter tasks

**Skill:**
- Auto-handles `/command` patterns in user messages

## Installation

See the main [vesper-team-skills README](../README.md) for full setup instructions.

Quick version:
```bash
# From vesper-team-skills root
cd openclaw-plugin && npm install
cp -r . ~/.openclaw/extensions/agent-tools
openclaw plugins enable agent-tools
openclaw gateway restart
```

## Configuration (Optional)

```yaml
plugins:
  entries:
    agent-tools:
      config:
        commandsDir: "~/.openclaw/commands"
        tasksDir: "~/.openclaw/tasks"
```
