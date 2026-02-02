# /social30days

**Social media trends move at light speed. This Claude Code skill keeps you current.** /social30days researches your topic across TikTok, Instagram, Facebook, and Google Trends. It finds what's going viral, trending hashtags, popular creators, and engagement patterns, then writes you prompts grounded in real social data.

**Best for social media research**: discover viral content, trending hashtags, top creators, and engagement patterns across TikTok, Instagram, and Facebook.

**Works with zero API keys**: TikTok Creative Center + Google Trends + WebSearch provides excellent coverage out of the box. Add CrowdTangle for FB/IG engagement metrics.

## Installation

```bash
# Clone the repo
git clone <repo-url> ~/.claude/skills/social30days

# Optional: Add CrowdTangle for FB/IG engagement data
mkdir -p ~/.config/social30days
cat > ~/.config/social30days/.env << 'EOF'
CROWDTANGLE_TOKEN=your-token-here
EOF
chmod 600 ~/.config/social30days/.env
```

## Usage

```
/social30days [topic]
/social30days [topic] for [tool]
```

Examples:
- `/social30days AI art trends`
- `/social30days trending dance challenges on TikTok`
- `/social30days best hashtags for travel content`
- `/social30days Nike social media strategy`

## What It Does

1. **Researches** - Scans TikTok Creative Center, Google Trends, CrowdTangle, and WebSearch
2. **Ranks** - Scores by engagement (views, likes, shares), recency, and relevance
3. **Synthesizes** - Identifies viral patterns across platforms
4. **Delivers** - Writes copy-paste-ready prompts grounded in real social data

## Scoring

**40% relevance / 25% recency / 35% engagement**

Engagement formula: `0.35*log1p(views) + 0.25*log1p(likes) + 0.25*log1p(shares) + 0.15*log1p(comments)`

## Options

| Flag | Description |
|------|-------------|
| `--quick` | Faster research, fewer sources |
| `--deep` | Comprehensive research, more sources |
| `--sources=free` | Free sources only |
| `--debug` | Verbose logging |

## Data Sources

| Source | API Key? | What It Provides |
|--------|----------|-----------------|
| TikTok Creative Center | No (free) | Top hashtags, trending sounds, popular patterns |
| Google Trends | No (free) | Interest over time, related queries, rising topics |
| WebSearch (site-targeted) | No (free) | Direct platform content (TikTok, IG, FB) |
| CrowdTangle | Optional | FB/IG post search with real engagement metrics |

---

*30 days of social. Every viral moment captured.*
