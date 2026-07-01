# /news30days

**The news cycle moves fast. This Claude Code skill keeps you informed.** /news30days researches your topic across Google News, NewsAPI, Bing News, and targeted web searches of major outlets. It finds what Reuters, BBC, NYT, Bloomberg, and hundreds of other sources are reporting, ranks by source authority, and writes you prompts grounded in real journalism.

**Best for news research**: discover what major outlets are reporting on any topic, from breaking news to industry analysis to company tracking.

**Works with zero API keys**: Google News RSS + WebSearch provides excellent coverage out of the box. Add NewsAPI or Bing News keys for even more sources.

## Installation

```bash
# Clone the repo
git clone <repo-url> ~/.claude/skills/news30days

# Optional: Add API keys for more sources
mkdir -p ~/.config/news30days
cat > ~/.config/news30days/.env << 'EOF'
NEWSAPI_KEY=your-key-here
BING_NEWS_KEY=your-azure-key-here
EOF
chmod 600 ~/.config/news30days/.env
```

## Usage

```
/news30days [topic]
/news30days [topic] for [tool]
```

Examples:
- `/news30days AI regulation updates`
- `/news30days what's happening with OpenAI`
- `/news30days electric vehicle market analysis`
- `/news30days tech layoffs 2026`

## What It Does

1. **Researches** - Scans Google News, NewsAPI, Bing News, and major outlets
2. **Ranks** - Scores by source authority (Reuters > random blog), recency, and relevance
3. **Synthesizes** - Identifies key stories and patterns across outlets
4. **Delivers** - Writes copy-paste-ready prompts grounded in real journalism

## Source Authority Tiers

| Tier | Score | Examples |
|------|-------|---------|
| Tier 1 | 90 | Reuters, AP, BBC, NYT, WSJ, Bloomberg |
| Tier 2 | 75 | TechCrunch, The Verge, Ars Technica, CNBC, Guardian |
| Tier 3 | 60 | Industry blogs, regional papers, trade pubs |
| Tier 4 | 40 | Personal blogs, unknown domains |

## Options

| Flag | Description |
|------|-------------|
| `--quick` | Faster research, fewer sources |
| `--deep` | Comprehensive research, more sources |
| `--sources=gnews` | Google News RSS only |
| `--sources=newsapi` | NewsAPI only |
| `--debug` | Verbose logging |

## Data Sources

| Source | API Key? | What It Provides |
|--------|----------|-----------------|
| Google News RSS | No (free) | Headlines, links, sources (~100 results) |
| WebSearch (site-targeted) | No (free) | Targeted outlet search (Reuters, BBC, etc.) |
| NewsAPI.org | Optional (free tier) | 80,000+ sources, sorting by relevancy |
| Bing News API | Optional (Azure) | Category filtering, freshness controls |

---

*30 days of news. Every angle covered.*
