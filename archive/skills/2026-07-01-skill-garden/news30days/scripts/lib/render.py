"""Output rendering for news30days skill."""

import json
from pathlib import Path
from typing import List, Optional

from . import schema

OUTPUT_DIR = Path.home() / ".local" / "share" / "news30days" / "out"


def ensure_output_dir():
    """Ensure output directory exists."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _assess_data_freshness(report: schema.NewsReport) -> dict:
    """Assess how much data is actually from the last 30 days."""
    recent = sum(1 for n in report.news if n.date and n.date >= report.range_from)
    total = len(report.news)

    return {
        "total_recent": recent,
        "total_items": total,
        "is_sparse": recent < 5,
        "mostly_evergreen": total > 0 and recent < total * 0.3,
    }


def render_compact(report: schema.NewsReport, limit: int = 20, missing_keys: str = "none") -> str:
    """Render compact output for Claude to synthesize."""
    lines = []

    lines.append(f"## News Research Results: {report.topic}")
    lines.append("")

    freshness = _assess_data_freshness(report)
    if freshness["is_sparse"]:
        lines.append("**⚠️ LIMITED RECENT NEWS** - Few articles from the last 30 days.")
        lines.append(f"Only {freshness['total_recent']} article(s) confirmed from {report.range_from} to {report.range_to}.")
        lines.append("")

    # Cache indicator
    if report.from_cache:
        age_str = f"{report.cache_age_hours:.1f}h old" if report.cache_age_hours else "cached"
        lines.append(f"**⚡ CACHED RESULTS** ({age_str}) - use `--refresh` for fresh data")
        lines.append("")

    lines.append(f"**Date Range:** {report.range_from} to {report.range_to}")
    lines.append(f"**Mode:** {report.mode}")

    # Source counts
    source_parts = []
    if report.gnews_count:
        source_parts.append(f"Google News: {report.gnews_count}")
    if report.newsapi_count:
        source_parts.append(f"NewsAPI: {report.newsapi_count}")
    if report.bing_count:
        source_parts.append(f"Bing: {report.bing_count}")
    if source_parts:
        lines.append(f"**Sources:** {' | '.join(source_parts)}")
    lines.append("")

    # Free mode promo
    if report.mode == "free" and missing_keys == "both":
        lines.append("**📰 FREE MODE** - Using Google News RSS + WebSearch")
        lines.append("")
        lines.append("---")
        lines.append("**⚡ Want more sources?** Add API keys to ~/.config/news30days/.env")
        lines.append("- `NEWSAPI_KEY` → 80,000+ sources, sorting by relevancy")
        lines.append("- `BING_NEWS_KEY` → Category filtering, freshness controls")
        lines.append("---")
        lines.append("")

    # Errors
    if report.gnews_error:
        lines.append(f"**Google News ERROR:** {report.gnews_error}")
        lines.append("")
    if report.newsapi_error:
        lines.append(f"**NewsAPI ERROR:** {report.newsapi_error}")
        lines.append("")
    if report.bing_error:
        lines.append(f"**Bing News ERROR:** {report.bing_error}")
        lines.append("")

    # News items
    if report.news:
        lines.append("### News Articles")
        lines.append("")
        for item in report.news[:limit]:
            date_str = f" ({item.date})" if item.date else " (date unknown)"
            conf_str = f" [date:{item.date_confidence}]" if item.date_confidence != "high" else ""
            auth_label = ""
            if item.source_authority >= 90:
                auth_label = " [Tier1]"
            elif item.source_authority >= 75:
                auth_label = " [Tier2]"

            lines.append(f"**{item.id}** (score:{item.score}) {item.source_name}{date_str}{conf_str}{auth_label}")
            lines.append(f"  {item.title}")
            lines.append(f"  {item.url}")
            if item.snippet:
                lines.append(f"  {item.snippet[:200]}...")
            if item.why_relevant:
                lines.append(f"  *{item.why_relevant}*")
            lines.append("")
    else:
        lines.append("### News Articles")
        lines.append("")
        lines.append("*No relevant news articles found for this topic.*")
        lines.append("")

    return "\n".join(lines)


def render_context_snippet(report: schema.NewsReport) -> str:
    """Render reusable context snippet."""
    lines = []
    lines.append(f"# Context: {report.topic} - News (Last 30 Days)")
    lines.append("")
    lines.append(f"*Generated: {report.generated_at[:10]} | Sources: {report.mode}*")
    lines.append("")

    lines.append("## Key Sources")
    lines.append("")

    for item in report.news[:7]:
        lines.append(f"- [{item.source_name}] {item.title}")

    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("*See full report for detailed sources and analysis.*")
    lines.append("")

    return "\n".join(lines)


def render_full_report(report: schema.NewsReport) -> str:
    """Render full markdown report."""
    lines = []

    lines.append(f"# {report.topic} - News Research Report (Last 30 Days)")
    lines.append("")
    lines.append(f"**Generated:** {report.generated_at}")
    lines.append(f"**Date Range:** {report.range_from} to {report.range_to}")
    lines.append(f"**Mode:** {report.mode}")
    lines.append("")

    if report.news:
        lines.append("## News Articles")
        lines.append("")
        for item in report.news:
            lines.append(f"### {item.id}: {item.title}")
            lines.append("")
            lines.append(f"- **Source:** {item.source_name} ({item.source_domain})")
            lines.append(f"- **URL:** {item.url}")
            lines.append(f"- **Date:** {item.date or 'Unknown'} (confidence: {item.date_confidence})")
            lines.append(f"- **Score:** {item.score}/100 (authority: {item.source_authority})")
            lines.append(f"- **Relevance:** {item.why_relevant}")
            if item.author:
                lines.append(f"- **Author:** {item.author}")
            lines.append("")
            if item.snippet:
                lines.append(f"> {item.snippet}")
                lines.append("")

    return "\n".join(lines)


def write_outputs(report: schema.NewsReport):
    """Write all output files."""
    ensure_output_dir()

    with open(OUTPUT_DIR / "report.json", 'w') as f:
        json.dump(report.to_dict(), f, indent=2)

    with open(OUTPUT_DIR / "report.md", 'w') as f:
        f.write(render_full_report(report))

    with open(OUTPUT_DIR / "news30days.context.md", 'w') as f:
        f.write(render_context_snippet(report))


def get_context_path() -> str:
    """Get path to context file."""
    return str(OUTPUT_DIR / "news30days.context.md")
