# TOOLS.md — ResearchCrawler

## Slack MCP Server

**Package:** `@modelcontextprotocol/server-slack`

```bash
# Read channel history
mcporter call 'slack-threads.slack_get_channel_history(channel_id:"C034P04K6EA", limit:100)'

# Read thread replies (the key capability)
mcporter call 'slack-threads.slack_get_thread_replies(channel_id:"<ID>", thread_ts:"<TS>")'

# List channels
mcporter call 'slack-threads.slack_list_channels(limit:100)'
```

**Key channel IDs:**
- `C034P04K6EA` — #ai-builders
- `C04QKEKPD3M` — #learning-ai
- `C07L2GUNV6Y` — #s2-game

---

## GitHub CLI

```bash
# Search issues
gh search issues "query" --repo sipherxyz/* --json title,body,url,comments

# Search PRs
gh search prs "query" --state all --repo sipherxyz/*

# View issue with comments
gh issue view <number> --repo sipherxyz/<repo> --comments

# Search code
gh api search/code -f q="query org:sipherxyz"
```

---

## Web Research

```bash
# Search
web_search "query site:arxiv.org"

# Fetch and extract
web_fetch "url" --extractMode markdown --maxChars 50000
```

---

## Output Locations

| Type | Path |
|------|------|
| Research docs | `~/tin-knowledgebase/research/` |
| Agent notes | `~/tin-knowledgebase/agent-notes/research-crawler/` |
| Queue | `~/tin-knowledgebase/Areas/RESEARCH-QUEUE.md` |

---

## Session Management

For long research sessions, checkpoint every 30-60 minutes:
1. Save current progress to research doc
2. Commit agent-notes
3. Continue or request re-spawn if needed
