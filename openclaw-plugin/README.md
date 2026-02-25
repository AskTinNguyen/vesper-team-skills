# OpenClaw Agent Tools Plugin

Slash commands and task list tools for OpenClaw agents.

## What You Get

**Slash Commands (44 commands):**
- `slash_list()` — List all available commands
- `slash_read(command)` — Read & execute commands

**Task Management:**
- `task_create(desc, priority?, owner?, blockedBy?)` — Create tasks
- `task_update(id, status?, priority?, owner?)` — Update tasks
- `task_get(id)` — Get single task
- `task_list(status?, owner?, unblockedOnly?)` — List/filter tasks

**Key Commands:** `/workflows:plan`, `/workflows:work`, `/workflows:review`, `/simplify-code`, `/changelog`, `/lfg`

---

## Installation

### One-Time Setup

```bash
# Clone the repo (or pull if you have it)
git clone https://github.com/AskTinNguyen/vesper-team-skills.git ~/vesper-team-skills

# Install plugin dependencies
cd ~/vesper-team-skills/openclaw-plugin && npm install

# Copy plugin to OpenClaw extensions (symlinks don't work!)
cp -r ~/vesper-team-skills/openclaw-plugin ~/.openclaw/extensions/agent-tools

# Symlink slash commands
ln -sf ~/vesper-team-skills/commands ~/.openclaw/commands

# Enable and restart
openclaw plugins enable agent-tools
openclaw gateway restart
```

### Updating

```bash
cd ~/vesper-team-skills && git pull

# If plugin code changed:
cp -r ~/vesper-team-skills/openclaw-plugin ~/.openclaw/extensions/agent-tools
openclaw gateway restart
```

---

## Usage

### Slash Commands

When a user sends `/something`, call:
```
slash_read("something")
```

Then follow the instructions in the returned file. Text after the command becomes `$ARGUMENTS`.

**Examples:**
- `/changelog weekly` → `slash_read("changelog")` with args "weekly"
- `/workflows:plan auth system` → `slash_read("workflows:plan")` with args "auth system"

### Task List

**Create:**
```
task_create("Fix auth bug", priority="urgent", owner="coder")
```

**Update:**
```
task_update(id="abc123", status="done")
```

**List:**
```
task_list()                           # All tasks
task_list(status="pending")           # Only pending
task_list(owner="coder")              # By owner
task_list(unblockedOnly=true)         # Ready to work
```

**Priorities:** `urgent` 🔴 | `high` 🟠 | `normal` 🟡 | `low` ⚪

**Dependencies:** Use `blockedBy` array to sequence work.

---

## Configuration (Optional)

```yaml
plugins:
  entries:
    agent-tools:
      config:
        commandsDir: "~/.openclaw/commands"
        tasksDir: "~/.openclaw/tasks"
```

---

## Troubleshooting

**Plugin not loading?**
- Symlinks don't work — must `cp -r` the directory
- Check `openclaw plugins list` for status
- Restart gateway after changes

**Commands not found?**
- Ensure `~/.openclaw/commands` symlink exists
- Check `ls -la ~/.openclaw/commands`

---

## Source

Part of [vesper-team-skills](https://github.com/AskTinNguyen/vesper-team-skills) by Ather Labs.
