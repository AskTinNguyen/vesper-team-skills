# OpenClaw Agent Templates

Shareable agent templates for OpenClaw instances. Each agent includes:
- Workspace files (AGENTS.md, IDENTITY.md, SOUL.md, TOOLS.md, HEARTBEAT.md)
- Config snippet for `openclaw.json`
- Knowledge files where applicable

## Available Agents

| Agent | Purpose | Model |
|-------|---------|-------|
| **jeff** | Agentic coding coach (Jeffrey Emanuel methodology) | Opus |
| **research-crawler** | Overnight autonomous research | Sonnet |
| **sidekick-main** | Coordinator template (reference) | Opus |

## Installation

### Quick Install (Recommended)

```bash
# Clone the repo
git clone https://github.com/AskTinNguyen/vesper-team-skills.git
cd vesper-team-skills

# Install an agent
./agents/install.sh jeff
./agents/install.sh research-crawler
```

### Manual Install

1. **Copy workspace files:**
```bash
cp -r agents/jeff ~/.openclaw/workspace-jeff
```

2. **Add to OpenClaw config** (`~/.openclaw/openclaw.json`):
```json
{
  "agents": {
    "list": [
      // ... existing agents ...
      {
        "id": "jeff",
        "name": "Jeff",
        "workspace": "/Users/YOUR_USER/.openclaw/workspace-jeff",
        "model": {
          "primary": "anthropic/claude-opus-4-5"
        }
      }
    ]
  }
}
```

3. **Add to subagents allowlist** (if using coordinator):
```json
{
  "agents": {
    "list": [
      {
        "id": "main",
        "subagents": {
          "allowAgents": ["jeff", "research"]
        }
      }
    ]
  }
}
```

4. **Restart gateway:**
```bash
openclaw gateway restart
```

## Agent Details

### Jeff (Agentic Coding Coach)
Based on Jeffrey Emanuel's Agent Flywheel methodology.

**Best for:**
- Project planning and task decomposition
- Converting plans to beads (atomic tasks)
- Multi-agent workflow guidance

**Spawn command:**
```
sessions_spawn(agentId="jeff", task="Help me plan [FEATURE]")
```

### ResearchCrawler (Overnight Autonomy)
Inspired by Karel Doosterlnck's $10K/month Codex methodology.

**Best for:**
- Deep Slack/GitHub/web crawling
- Hypothesis extraction from discussions
- Expertise mapping
- Self-improving via agent-notes

**Schedule:** Runs at 11 PM, processes research queue

**Cron setup:**
```json
{
  "schedule": {"kind": "cron", "expr": "0 23 * * *", "tz": "Asia/Saigon"},
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "Spawn research agent: sessions_spawn(agentId='research', task='Start overnight crawl...')"
  }
}
```

### Sidekick-Main (Coordinator Template)
Reference template for a coordinator agent.

**Best for:**
- Primary assistant duties
- Agent orchestration
- WhatsApp/Slack responses

## Customization

Each agent's files are designed to be customized:

1. **AGENTS.md** — Main instructions, modify for your use case
2. **IDENTITY.md** — Personality and role
3. **SOUL.md** — Core principles
4. **TOOLS.md** — Tool-specific notes and shortcuts
5. **HEARTBEAT.md** — Scheduled check-in behavior

## Contributing

To add a new agent template:

1. Create folder: `agents/your-agent/`
2. Add workspace files
3. Add `config.json` with OpenClaw config snippet
4. Update this README
5. Submit PR

## License

MIT
