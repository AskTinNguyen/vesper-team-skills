# Research Automation Process

**Adapted from:** Karel Doosterlnck's Codex methodology  
**Created:** 2026-02-06

---

## When to Trigger

Start research automation when:
- Exploring unfamiliar codebase/domain before implementation
- Evaluating new tool, framework, or market opportunity
- Weekly knowledge sync (Sundays)
- Before any project >2 days of work

---

## Sources to Crawl

### 1. Slack (via message tool / MCP)
```bash
# Search channels for topic
message search --query "topic" --channels general,dev,research
```
- Extract discussions, decisions, pain points
- Note who knows what (expertise mapping)
- Pull linked documents and screenshots

### 2. GitHub (via gh CLI)
```bash
# Search issues, PRs, discussions
gh search issues "topic" --repo ather-labs/*
gh search prs "topic" --state all
gh api search/code -f q="topic org:ather-labs"
```
- Find prior art and abandoned approaches
- Check discussion threads for context
- Review related branch experiments

### 3. Web (via web_search, web_fetch)
```bash
# Broad search, then deep fetch
web_search "topic site:github.com OR site:arxiv.org"
web_fetch "url" --extractMode markdown
```
- Academic papers (arxiv, papers with code)
- Industry implementations (GitHub repos)
- Recent discussions (HN, Twitter, Discord)

---

## Output Structure

All research outputs go to: `~/tin-knowledgebase/research/`

### Per-Topic Template
`# Research: [Topic]` → TL;DR → Sources (with links) → Hypotheses → Actions → Open Questions

---

## Compounding Knowledge

### Agent Notes Folder
Each agent maintains: `~/tin-knowledgebase/agent-notes/[agent-name]/`

After each research session, commit:
```markdown
# Session: YYYY-MM-DD

## What Worked
- Technique that was effective

## What Didn't
- Approach that failed and why

## Shortcuts Discovered
- Faster way to do X

## Contacts/Expertise
- @person knows about X
```

### Cross-Session Loop
1. Read agent-notes → 2. Research → 3. Commit notes → 4. Weekly consolidation

---

## Agent Roles

| Agent | Research Focus |
|-------|---------------|
| **TinSidekick** | Orchestrates, consolidates, routes |
| **Coder** | Technical implementations, code search |
| **GamingScout** | Gaming industry, Steam, player behavior |
| **MarketWatch** | Market data, competitors, trends |

### Orchestration Pattern
```
User request → TinSidekick
  ├── Spawns Coder (if code research needed)
  ├── Spawns GamingScout (if gaming domain)
  ├── Spawns MarketWatch (if market analysis)
  └── Aggregates results, writes to knowledge base
```

---

## Quick Start Checklist

- [ ] Define research question clearly
- [ ] Check existing research in `tin-knowledgebase/`
- [ ] Read agent-notes for prior shortcuts
- [ ] Crawl: Slack → GitHub → Web
- [ ] Generate 5+ testable hypotheses
- [ ] Write structured output
- [ ] Commit agent notes
- [ ] Link from relevant project docs
