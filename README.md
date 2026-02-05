# Vesper Team Skills

Shared commands, skills, and tools for AI agents at Atherlab.

## What's Included

### `/commands/` — Slash Commands (44 total)
Claude Code-style commands for planning, coding, reviewing, and automation.

**Key commands:**
- `/workflows:plan` — Create structured project plans
- `/workflows:work` — Execute work plans
- `/workflows:review` — Multi-agent code review
- `/simplify-code` — Dual-pass code simplification
- `/changelog` — Generate engaging changelogs
- `/lfg` — Full autonomous engineering workflow

### `/openclaw-plugin/` — OpenClaw Agent Tools
Plugin that enables slash commands and task lists in OpenClaw.

**Tools provided:**
- `slash_list`, `slash_read` — Command discovery and execution
- `task_create`, `task_update`, `task_get`, `task_list` — Task coordination

---

## Installation (OpenClaw)

### 1. Clone this repo

```bash
git clone https://github.com/AskTinNguyen/vesper-team-skills.git ~/vesper-team-skills
```

### 2. Install the plugin

```bash
# Install dependencies
cd ~/vesper-team-skills/openclaw-plugin
npm install

# Copy to OpenClaw extensions
cp -r ~/vesper-team-skills/openclaw-plugin ~/.openclaw/extensions/agent-tools

# Enable the plugin
openclaw plugins enable agent-tools
```

### 3. Link the commands

```bash
ln -sf ~/vesper-team-skills/commands ~/.openclaw/commands
```

### 4. Restart OpenClaw

```bash
openclaw gateway restart
```

### 5. Verify

```bash
openclaw plugins list | grep agent-tools
# Should show: agent-tools | loaded
```

---

## Updating

```bash
cd ~/vesper-team-skills
git pull

# If plugin code changed, re-copy:
cp -r ~/vesper-team-skills/openclaw-plugin ~/.openclaw/extensions/agent-tools
openclaw gateway restart
```

---

## Usage

### Slash Commands

Just type `/command` in your message:
```
/changelog weekly
/workflows:plan Build a notification system
/simplify-code file:src/utils.ts
```

### Tasks

```
Create a task: Fix the login bug
What tasks do we have?
Mark task abc123 as done
```

---

## Adding New Commands

1. Create `commands/your-command.md` with YAML frontmatter:

```markdown
---
name: your-command
description: What it does
argument-hint: "[optional args]"
---

Your command instructions here.
Use $ARGUMENTS for user input.
```

2. Commit and push
3. Team members run `git pull` — no restart needed

---

## License

MIT — Atherlab
