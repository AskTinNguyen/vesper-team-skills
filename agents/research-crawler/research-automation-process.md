# Research Automation Process

**Adapted from:** Karel Doosterlnck's Codex methodology  

---

## When to Trigger

Start research automation when:
- Exploring unfamiliar codebase/domain before implementation
- Evaluating new tool, framework, or market opportunity
- Weekly knowledge sync
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
gh search issues "topic" --repo YOUR_ORG/*
gh search prs "topic" --state all
gh api search/code -f q="topic org:YOUR_ORG"
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

All research outputs go to: `~/knowledge-base/research/`

### Per-Topic Template
`# Research: [Topic]` → TL;DR → Sources (with links) → Hypotheses → Actions → Open Questions

---

## Compounding Knowledge

### Agent Notes Folder
Each agent maintains: `~/knowledge-base/agent-notes/[agent-name]/`

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

## Agent Roles (Example)

| Agent | Research Focus |
|-------|---------------|
| **Coordinator** | Orchestrates, consolidates, routes |
| **Coder** | Technical implementations, code search |
| **ResearchCrawler** | Deep research, overnight crawls |

### Orchestration Pattern
```
User request → Coordinator
  ├── Spawns Coder (if code research needed)
  ├── Spawns ResearchCrawler (if deep research needed)
  └── Aggregates results, writes to knowledge base
```

---

## Quick Start Checklist

- [ ] Define research question clearly
- [ ] Check existing research in knowledge base
- [ ] Read agent-notes for prior shortcuts
- [ ] Crawl: Slack → GitHub → Web
- [ ] Generate 5+ testable hypotheses
- [ ] Write structured output
- [ ] Commit agent notes
- [ ] Link from relevant project docs

---

*Customize org names and paths for your setup.*
