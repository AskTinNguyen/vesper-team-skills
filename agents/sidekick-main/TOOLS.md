# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

---

## agent-browser (CLI)

**What:** Headless browser automation CLI for AI agents  
**Repo:** github.com/vercel-labs/agent-browser (12.4k ⭐)

**When to use:**
- Quick web scraping/automation tasks
- When I need accessibility tree with refs
- CLI-based browser automation (non-OpenClaw contexts)

**Quick commands:**
```bash
agent-browser open <url>      # Navigate
agent-browser snapshot        # Accessibility tree with refs (@e1, @e2...)
agent-browser click @e2       # Click by ref
agent-browser fill @e3 "text" # Fill by ref
agent-browser get text @e1    # Extract text
agent-browser screenshot      # Capture
agent-browser close           # Done
```

**vs OpenClaw browser tool:**
- agent-browser: CLI, refs, fast scripts
- OpenClaw browser: Integrated, CDP, profile mgmt

---

## Slack MCP Server (Thread Reading) — Official Anthropic

**What:** Read Slack thread replies — something `message read` can't do  
**Package:** `@modelcontextprotocol/server-slack` (official Anthropic)  
**Config:** `~/.mcporter/mcporter.json`

**Why needed:** OpenClaw's `message read` only supports channel-level reads. Thread reply reading is a **missing feature** — use MCP as workaround.

**Quick commands:**
```bash
# Read thread replies (the main use case)
mcporter call 'slack-threads.slack_get_thread_replies(channel_id:"C07L2GUNV6Y", thread_ts:"1769484478.611799")'

# Read channel history
mcporter call 'slack-threads.slack_get_channel_history(channel_id:"C07L2GUNV6Y", limit:20)'

# List channels
mcporter call 'slack-threads.slack_list_channels(limit:100)'

# Reply to thread
mcporter call 'slack-threads.slack_reply_to_thread(channel_id:"C07L2GUNV6Y", thread_ts:"...", text:"Hello")'

# Post to channel
mcporter call 'slack-threads.slack_post_message(channel_id:"C07L2GUNV6Y", text:"Hello")'

# Add reaction
mcporter call 'slack-threads.slack_add_reaction(channel_id:"...", timestamp:"...", reaction:"thumbsup")'

# Get users
mcporter call 'slack-threads.slack_get_users(limit:100)'
```

**All available tools:**
- `slack_get_thread_replies` — Read thread replies ✨
- `slack_get_channel_history` — Read channel messages
- `slack_list_channels` — List channels
- `slack_post_message` — Post to channel
- `slack_reply_to_thread` — Reply in thread
- `slack_add_reaction` — Add emoji reaction
- `slack_get_users` — List workspace users
- `slack_get_user_profile` — Get user details

**Key channel IDs:**
- `C034P04K6EA` — #ai-builders
- `C04QKEKPD3M` — #learning-ai
- `C07L2GUNV6Y` — #s2-game

---

Add whatever helps you do your job. This is your cheat sheet.

---

## Jeff Agent (Agentic Coding Coach)

**What:** AI coach based on Jeffrey Emanuel's Agent Flywheel methodology  
**Model:** Opus (critical thinking)  
**Location:** `workspace/agents/jeff-agent/`

**When to spawn:**
- Starting a new feature and want structured planning
- Need to decompose work into AI-agent-friendly tasks (beads)
- Want to adopt the beads/bv workflow
- Need workflow guidance for multi-agent coordination

**How to spawn:**
```
sessions_spawn(agentId="jeff", task="Help me plan [FEATURE DESCRIPTION]")
```

**Jeff slash commands:**
```
/jeff-plan <feature>      # Generate technical plan
/jeff-beads <plan.md>     # Convert to atomic tasks
/jeff-triage              # Analyze graph priorities
/jeff-next                # Get top task
/jeff-decompose <task>    # Split big tasks
/jeff-execute [id]        # Spawn Coder
/jeff-review              # Check progress
```

---

## Beads (bd/bv) — Task Graph System

**What:** Git-backed graph issue tracker for AI agents  
**CLI:** `~/.local/bin/bd` (beads), `~/.local/bin/bv` (viewer)

**Setup in new project:**
```bash
cd <project>
~/.local/bin/bd init                    # Initialize .beads/
~/.local/bin/bd sync --flush-only       # Sync db → JSONL
```

**Key commands:**
```bash
# bd (task management)
bd list                    # List open tasks
bd list --all              # Include closed
bd create "Title" -p 0     # Create P0 task
bd update <id> --status closed  # Close task

# bv (graph analysis)
bv --robot-triage          # Full analysis (THE command)
bv --robot-next            # Single top pick
bv --robot-plan            # Parallel execution tracks
```

**Bead format (CRITICAL):**
```json
{"id":"X","type":"task","status":"open","priority":0,"title":"...","deps":[],...}
```
- **priority MUST be int**: 0=P0, 1=P1, 2=P2, 3=P3
- NOT strings like "high"/"low"

**Workflow:**
1. `bd init` in project
2. Generate beads (JSONL) with `/jeff-beads`
3. Import: `cat beads.jsonl | bd import -i /dev/stdin --rename-on-import`
4. Sync: `bd sync --flush-only`
5. Query: `bv --robot-triage`

---

## QMD — Local Knowledge Search

**What:** On-device semantic search for markdown notes, docs, meeting transcripts  
**Repo:** github.com/tobi/qmd  
**Binary:** `~/.bun/bin/qmd`

**When to use:**
- Searching local knowledge bases (notes, docs, memory files)
- When `memory_search` needs local embeddings (no API key)
- Agentic workflows needing structured retrieval

**Quick ref:**
```bash
qmd search "keyword"    # BM25 (fast)
qmd vsearch "concept"   # Semantic (needs embed)
qmd query "question"    # Hybrid + reranking (best)
qmd status              # Show collections
```

Run `qmd --help` for full docs.

---

## Task Orchestration — Agent Types

**What:** Claude Code-style typed agents for OpenClaw  
**Location:** `Areas/task-orchestration/`

**Agent types available:**
| Type | Purpose | Tools |
|------|---------|-------|
| `explore` | Read-only codebase search | Read, grep, find |
| `plan` | Architecture planning | Read, research |
| `general-purpose` | Full capability | All tools |
| `bash` | Command-line only | exec only |

**Quick dispatch:**
```
sessions_spawn(
  agentId="coder",
  task="[AGENT TYPE: EXPLORE]\n\nRead Areas/task-orchestration/agent-types/explore.md\n\nTASK: Find all API endpoints"
)
```

**Tracking:** `Areas/task-orchestration/TASK-QUEUE.md`  
**Protocol:** `Areas/task-orchestration/DISPATCH-PROTOCOL.md`

---

## 🔥 Agent Tools Plugin (MUST USE)

**Source:** `github.com/AskTinNguyen/vesper-team-skills` → `openclaw-plugin/`  
**Installed:** `~/.openclaw/extensions/agent-tools/`

### Tools Provided

| Tool | Purpose |
|------|---------|
| `slash_list()` | List all 44+ available commands |
| `slash_read(command)` | Read command file → follow instructions |
| `task_create(desc, priority?, owner?, blockedBy?)` | Create task |
| `task_update(id, status?, priority?, owner?)` | Update task |
| `task_get(id)` | Get single task |
| `task_list(status?, owner?, unblockedOnly?)` | List/filter tasks |

### Slash Commands

**Commands:** `~/.openclaw/commands/` → symlink to `vesper-team-skills/commands/`

When user sends `/something`:
1. `slash_read("something")` → get instructions
2. Follow the instructions
3. Text after command = `$ARGUMENTS`

**Key commands:**
```
/workflows:plan <feature>     # Create project plan
/workflows:work               # Execute work plan  
/workflows:review             # Multi-agent code review
/changelog [daily|weekly]     # Generate changelog
/simplify-code [target]       # Dual-pass simplification
/lfg <feature>                # Full autonomous workflow
```

**Namespaces:** `workflows:plan` → `commands/workflows/plan.md`

### Task List

**Storage:** `~/.openclaw/tasks/tasks.json`  
**Priority:** `urgent` 🔴 | `high` 🟠 | `normal` 🟡 | `low` ⚪  
**Status:** `pending` ⏳ | `in_progress` 🔄 | `done` ✅

Tasks can have dependencies (`blockedBy`) for sequencing work.

### Installation / Updating

```bash
cd ~/vesper-team-skills && git pull
cd openclaw-plugin && npm install
cp -r . ~/.openclaw/extensions/agent-tools
openclaw gateway restart
```

**Note:** Symlinks don't work — must copy the directory.

---

## Bilibili Scraper Skill

**Location:** `~/.openclaw/skills/bilibili-scraper/SKILL.md`  
**Use for:** Scraping Chinese gaming videos, comments, danmaku (弹幕)

### Quick Start
```bash
# Start browser
browser action=start target=host profile=openclaw

# Open video
browser action=open targetUrl="https://www.bilibili.com/video/BV1xxxxx/"

# Wait for load
browser action=act request='{"kind":"wait","timeMs":3000}'

# Scroll to comments
browser action=act request='{"kind":"evaluate","fn":"window.scrollBy(0,2000)"}'

# Snapshot content
browser action=snapshot compact=true

# Close
browser action=close
```

### What You Can Extract
- **Video metadata:** Title, views, danmaku count
- **Danmaku (弹幕):** Real-time floating comments
- **Comment section:** Top comments with likes
- **Related videos:** Recommended content

### Reference Files
- `examples/scrape-video.md` — Single video deep dive
- `examples/search-videos.md` — Search and multi-video workflow
- `reference/gaming-terms-zh.md` — Chinese gaming vocabulary (打击感, 顿帧, etc.)

### Best Used By
- **GamingScout** — Chinese market research
- **TinSidekick** — Ad-hoc gaming research
