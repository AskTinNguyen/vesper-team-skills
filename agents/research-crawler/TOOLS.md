# TOOLS.md — ResearchCrawler

## Slack MCP Server

**Package:** `@modelcontextprotocol/server-slack`

```bash
# Read channel history
mcporter call 'slack-threads.slack_get_channel_history(channel_id:"YOUR_CHANNEL_ID", limit:100)'

# Read thread replies (the key capability)
mcporter call 'slack-threads.slack_get_thread_replies(channel_id:"<ID>", thread_ts:"<TS>")'

# List channels
mcporter call 'slack-threads.slack_list_channels(limit:100)'
```

**Add your channel IDs:**
- `CXXXXXXXXXX` — #your-channel-1
- `CXXXXXXXXXX` — #your-channel-2

---

## GitHub CLI

```bash
# Search issues
gh search issues "query" --repo YOUR_ORG/* --json title,body,url,comments

# Search PRs
gh search prs "query" --state all --repo YOUR_ORG/*

# View issue with comments
gh issue view <number> --repo YOUR_ORG/<repo> --comments

# Search code
gh api search/code -f q="query org:YOUR_ORG"
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
| Research docs | `~/knowledge-base/research/` |
| Agent notes | `~/knowledge-base/agent-notes/research-crawler/` |
| Queue | `~/knowledge-base/Areas/RESEARCH-QUEUE.md` |

---

## Session Management

For long research sessions, checkpoint every 30-60 minutes:
1. Save current progress to research doc
2. Commit agent-notes
3. Continue or request re-spawn if needed

---

*Customize the channel IDs, org names, and paths for your setup.*
