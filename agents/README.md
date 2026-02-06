# OpenClaw Agent Templates

Ready-to-use agents you can install on any OpenClaw instance.

---

## Quick Start (5 minutes)

### Step 1: Clone the repo

```bash
git clone https://github.com/AskTinNguyen/vesper-team-skills.git
cd vesper-team-skills
```

### Step 2: Install an agent

```bash
./agents/install.sh jeff              # Agentic coding coach
./agents/install.sh research-crawler  # Overnight research agent
```

### Step 3: Add to OpenClaw config

Edit `~/.openclaw/openclaw.json` and add the agent to `agents.list`:

```json
{
  "agents": {
    "list": [
      // ... your existing agents ...
      
      // Add Jeff (coding coach)
      {
        "id": "jeff",
        "name": "Jeff",
        "workspace": "/Users/YOUR_USERNAME/.openclaw/workspace-jeff",
        "model": { "primary": "anthropic/claude-opus-4-5" }
      },
      
      // Add ResearchCrawler (overnight research)
      {
        "id": "research",
        "name": "ResearchCrawler", 
        "workspace": "/Users/YOUR_USERNAME/.openclaw/workspace-research",
        "model": { "primary": "anthropic/claude-sonnet-4-5" }
      }
    ]
  }
}
```

**Important:** Replace `YOUR_USERNAME` with your actual username.

### Step 4: Allow spawning (if using a coordinator)

If your main agent spawns sub-agents, add to its `subagents.allowAgents`:

```json
{
  "id": "main",
  "subagents": {
    "allowAgents": ["jeff", "research"]
  }
}
```

### Step 5: Restart gateway

```bash
openclaw gateway restart
```

### Step 6: Test it!

```bash
# In your OpenClaw chat:
sessions_spawn(agentId="jeff", task="Hello! Introduce yourself.")
```

---

## Available Agents

### 🔧 Jeff — Agentic Coding Coach

Based on Jeffrey Emanuel's (@doodlestein) Agent Flywheel methodology.

| Field | Value |
|-------|-------|
| **Model** | Opus (for critical thinking) |
| **Best for** | Project planning, task decomposition, multi-agent workflows |
| **Workspace** | `~/.openclaw/workspace-jeff` |

**How to use:**
```
sessions_spawn(agentId="jeff", task="Help me plan a new feature: [DESCRIPTION]")
```

**What Jeff does:**
- Creates structured project plans
- Breaks work into atomic tasks (beads)
- Guides multi-agent coordination
- Uses beads/bv workflow for task management

---

### 🔬 ResearchCrawler — Overnight Autonomous Research

Inspired by Karel Doosterlnck's $10K/month Codex methodology at OpenAI.

| Field | Value |
|-------|-------|
| **Model** | Sonnet (cost-efficient for volume) |
| **Best for** | Deep research, Slack/GitHub mining, hypothesis extraction |
| **Workspace** | `~/.openclaw/workspace-research` |
| **Schedule** | 11 PM nightly (or on-demand) |

**How to use:**
```
sessions_spawn(agentId="research", task="Research [TOPIC]. Crawl Slack, GitHub, and web sources.")
```

**What ResearchCrawler does:**
- Crawls Slack channels for discussions and decisions
- Mines GitHub issues/PRs for context
- Searches web for recent articles and papers
- Writes structured research docs
- Maintains self-improving agent-notes

**Optional: Set up overnight cron:**
```json
{
  "name": "ResearchCrawler Overnight",
  "schedule": { "kind": "cron", "expr": "0 23 * * *", "tz": "YOUR_TIMEZONE" },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "Spawn research: sessions_spawn(agentId='research', task='Process research queue')",
    "timeoutSeconds": 7200
  }
}
```

---

### ⚡ Sidekick-Main — Coordinator Template

Reference template for a primary coordinator agent.

| Field | Value |
|-------|-------|
| **Model** | Opus |
| **Best for** | Primary assistant, agent orchestration |
| **Workspace** | `~/.openclaw/workspace` |

Use this as a starting point for your own coordinator agent.

---

## Customizing Agents

Each agent workspace contains these files you can edit:

| File | Purpose |
|------|---------|
| `AGENTS.md` | Main instructions and protocols |
| `IDENTITY.md` | Name, role, personality |
| `SOUL.md` | Core principles and values |
| `TOOLS.md` | Tool-specific notes and shortcuts |
| `HEARTBEAT.md` | Scheduled check-in behavior |

Feel free to customize these for your use case!

---

## Updating Agents

```bash
cd vesper-team-skills
git pull

# Re-install to get updates (will prompt before overwriting)
./agents/install.sh jeff
```

---

## Troubleshooting

### Agent not found when spawning

1. Check `openclaw.json` has the agent in `agents.list`
2. Check the workspace path is correct
3. Restart gateway: `openclaw gateway restart`

### Permission denied on install.sh

```bash
chmod +x ./agents/install.sh
```

### Agent spawns but fails immediately

Check the agent's transcript for errors:
```bash
ls ~/.openclaw/agents/<agent-name>/sessions/
cat ~/.openclaw/agents/<agent-name>/sessions/<latest>.jsonl | tail -20
```

---

## Contributing New Agents

1. Create folder: `agents/your-agent/`
2. Add workspace files (AGENTS.md, IDENTITY.md, etc.)
3. Add `config.json` with OpenClaw config snippet
4. Update this README
5. Submit PR

---

## Questions?

- OpenClaw docs: https://docs.openclaw.ai
- Community: https://discord.com/invite/clawd
- This repo: https://github.com/AskTinNguyen/vesper-team-skills
