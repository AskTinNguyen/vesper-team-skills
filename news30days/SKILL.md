---
name: news30days
description: Research a topic from the last 30 days in news outlets (Google News, NewsAPI, Bing News, WebSearch), become an expert on the news coverage, and write copy-paste-ready prompts.
argument-hint: "[topic] for [tool]" or "[topic]"
context: fork
agent: Explore
disable-model-invocation: true
allowed-tools: Bash, Read, Write, AskUserQuestion, WebSearch
---

# news30days: Research Any Topic from the Last 30 Days in News

Research ANY topic across major news outlets. Surface what Reuters, BBC, NYT, Bloomberg, and hundreds of other sources are reporting right now.

Use cases:
- **Breaking News**: "AI regulation updates", "tech layoffs 2026" → find what's happening now
- **Industry Analysis**: "electric vehicle market", "AI chip competition" → deep coverage
- **Company Tracking**: "what's happening with OpenAI", "Apple announcements" → company news
- **General Research**: any topic → understand the news landscape

## CRITICAL: Parse User Intent

Before doing anything, parse the user's input for:

1. **TOPIC**: What they want to learn about
2. **TARGET TOOL** (if specified): Where they'll use the prompts
3. **QUERY TYPE**: What kind of research:
   - **BREAKING** - "latest X", "X news today" → current events
   - **ANALYSIS** - "X market analysis", "X trends" → deeper coverage
   - **TRACKING** - "what's happening with X" → company/topic tracking
   - **GENERAL** - anything else → broad news understanding

**Store these variables:**
- `TOPIC = [extracted topic]`
- `TARGET_TOOL = [extracted tool, or "unknown" if not specified]`
- `QUERY_TYPE = [BREAKING | ANALYSIS | TRACKING | GENERAL]`

---

## Setup Check

The skill works in multiple modes based on available API keys:

1. **Full Mode** (all keys): Google News RSS + NewsAPI + Bing News + WebSearch
2. **Partial Mode** (some keys): Google News RSS + available APIs + WebSearch
3. **Free Mode** (no keys): Google News RSS + WebSearch (still excellent)

**API keys are OPTIONAL.** The skill works great with zero keys using Google News RSS + WebSearch.

### First-Time Setup (Optional)

```bash
mkdir -p ~/.config/news30days
cat > ~/.config/news30days/.env << 'ENVEOF'
# news30days API Configuration
# Both keys are optional - skill works with Google News RSS + WebSearch

# For broader news coverage (80,000+ sources)
NEWSAPI_KEY=

# For Bing News with category filtering
BING_NEWS_KEY=
ENVEOF

chmod 600 ~/.config/news30days/.env
echo "Config created at ~/.config/news30days/.env"
```

**DO NOT stop if no keys are configured.** Proceed with free mode.

---

## Research Execution

**Step 1: Run the research script**
```bash
python3 ~/.claude/skills/news30days/scripts/news30days.py "$ARGUMENTS" --emit=compact 2>&1
```

The script will automatically:
- Detect available API keys
- Search Google News RSS (always free)
- Query NewsAPI and/or Bing News if keys exist
- Signal that WebSearch should supplement results

**Step 2: Do WebSearch for targeted news outlet coverage**

For **ALL modes**, do WebSearch to supplement with site-targeted queries.

Choose search queries based on QUERY_TYPE:

**If BREAKING** ("latest X", "X news"):
- Search for: `"{TOPIC}" breaking news`
- Search for: `"{TOPIC}" site:reuters.com`
- Search for: `"{TOPIC}" site:apnews.com`
- Search for: `"{TOPIC}" site:bbc.com`

**If ANALYSIS** ("X trends", "X market"):
- Search for: `"{TOPIC}" analysis`
- Search for: `"{TOPIC}" site:bloomberg.com`
- Search for: `"{TOPIC}" site:wsj.com`
- Search for: `"{TOPIC}" site:ft.com`

**If TRACKING** ("what's happening with X"):
- Search for: `"{TOPIC}" announcement update`
- Search for: `"{TOPIC}" site:techcrunch.com`
- Search for: `"{TOPIC}" site:theverge.com`

**If GENERAL**:
- Search for: `"{TOPIC}" news 2026`
- Search for: `"{TOPIC}" site:reuters.com`
- Search for: `"{TOPIC}" latest report`

For ALL query types:
- **USE THE USER'S EXACT TERMINOLOGY** in searches
- INCLUDE: Reuters, AP, BBC, NYT, WSJ, Bloomberg, TechCrunch, The Verge, etc.
- **DO NOT output "Sources:" list** - stats come at the end

**Depth options** (passed through from user's command):
- `--quick` → Faster, fewer sources
- (default) → Balanced
- `--deep` → Comprehensive

---

## Synthesize All Sources

After all searches complete, internally synthesize:

1. Weight **Tier 1 sources** (Reuters, AP, BBC, NYT) HIGHEST
2. Weight **Tier 2 sources** (TechCrunch, The Verge, CNBC) MEDIUM
3. Weight **Tier 3+** sources LOWER
4. Identify patterns across multiple outlets (strongest signals)
5. Note any disagreements between sources
6. Extract the top 3-5 key developments

---

## Show Summary + Invite Vision

**Display in this EXACT sequence:**

**FIRST - What the news says (based on QUERY_TYPE):**

**If BREAKING** - Show timeline of developments:
```
📰 Key developments:
1. [Date] - [What happened] (Source: Reuters, BBC)
2. [Date] - [What happened] (Source: NYT, Bloomberg)
3. [Date] - [What happened] (Source: TechCrunch)
```

**If ANALYSIS/TRACKING/GENERAL** - Show synthesis:
```
What the news says:

[2-4 sentences synthesizing key insights FROM THE ACTUAL NEWS COVERAGE.]

KEY STORIES:
1. [Story/development from coverage]
2. [Story/development from coverage]
3. [Story/development from coverage]
```

**THEN - Stats:**
```
---
✅ News research complete!
├─ 📰 Google News: {n} articles
├─ 🔵 NewsAPI: {n} articles (if used)
├─ 🔍 Bing News: {n} articles (if used)
├─ 🌐 WebSearch: {n} pages
└─ Top sources: Reuters, BBC, TechCrunch, ...
```

**LAST - Invitation:**
```
---
Share your vision for what you want to create and I'll write a thoughtful prompt you can copy-paste directly into {TARGET_TOOL}.
```

---

## WAIT FOR USER'S VISION

After showing the stats summary, **STOP and wait** for the user to respond.

---

## WHEN USER SHARES THEIR VISION: Write ONE Perfect Prompt

Based on what they want to create, write a **single, highly-tailored prompt** grounded in the news research.

### Output Format:

```
Here's your prompt for {TARGET_TOOL}:

---

[The actual prompt, informed by news research findings]

---

This uses [brief 1-line explanation of what news insight you applied].
```

---

## AFTER EACH PROMPT: Stay in Expert Mode

After delivering a prompt:

> Want another prompt? Just tell me what you're creating next.

---

## CONTEXT MEMORY

For the rest of this conversation, remember:
- **TOPIC**: {topic}
- **TARGET_TOOL**: {tool}
- **KEY STORIES**: {list the top 3-5 stories you learned}
- **NEWS FINDINGS**: The key facts and insights from the coverage

**After research is complete, you are now an EXPERT on this topic's news coverage.**

When the user asks follow-up questions:
- **DO NOT run new WebSearches** unless about a DIFFERENT topic
- **Answer from what you learned** - cite the news sources
- **If they ask for a prompt** - write one using your expertise

---

## Output Summary Footer

After delivering a prompt, end with:

```
---
📰 Expert in: {TOPIC} news coverage
📊 Based on: {n} Google News + {n} NewsAPI + {n} Bing + {n} web pages
🏛️ Top sources: {tier1_sources}

Want another prompt? Just tell me what you're creating next.
```
