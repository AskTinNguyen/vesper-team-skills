"""Output rendering for social30days skill."""

import json
from pathlib import Path
from typing import Optional

from . import schema

OUTPUT_DIR = Path.home() / ".local" / "share" / "social30days" / "out"


def ensure_output_dir():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def render_compact(report: schema.SocialReport, limit: int = 20, missing_keys: str = "none") -> str:
    """Render compact output for Claude to synthesize."""
    lines = []

    lines.append(f"## Social Media Research Results: {report.topic}")
    lines.append("")

    lines.append(f"**Date Range:** {report.range_from} to {report.range_to}")
    lines.append(f"**Mode:** {report.mode}")

    source_parts = []
    if report.tiktok_count:
        source_parts.append(f"TikTok Creative: {report.tiktok_count}")
    if report.google_trends_count:
        source_parts.append(f"Google Trends: {report.google_trends_count}")
    if report.crowdtangle_count:
        source_parts.append(f"CrowdTangle: {report.crowdtangle_count}")
    if source_parts:
        lines.append(f"**Sources:** {' | '.join(source_parts)}")
    lines.append("")

    # Free mode promo
    if report.mode == "free" and missing_keys == "crowdtangle":
        lines.append("**📱 FREE MODE** - Using TikTok Creative + Google Trends + WebSearch")
        lines.append("")
        lines.append("---")
        lines.append("**⚡ Want engagement metrics?** Add CrowdTangle token to ~/.config/social30days/.env")
        lines.append("- `CROWDTANGLE_TOKEN` → FB/IG post data with real engagement numbers")
        lines.append("---")
        lines.append("")

    # Errors
    if report.tiktok_error:
        lines.append(f"**TikTok Creative ERROR:** {report.tiktok_error}")
        lines.append("")
    if report.google_trends_error:
        lines.append(f"**Google Trends ERROR:** {report.google_trends_error}")
        lines.append("")
    if report.crowdtangle_error:
        lines.append(f"**CrowdTangle ERROR:** {report.crowdtangle_error}")
        lines.append("")

    # Trend items
    if report.trends:
        lines.append("### Trending Topics")
        lines.append("")
        for item in report.trends[:10]:
            related = ", ".join(item.related_topics[:5]) if item.related_topics else "none"
            lines.append(f"**{item.id}** (score:{item.score}) [{item.platform}] {item.keyword}")
            lines.append(f"  Trend score: {item.trend_score}/100 | Related: {related}")
            if item.url:
                lines.append(f"  {item.url}")
            lines.append("")

    # Social items
    if report.social:
        lines.append("### Social Media Posts")
        lines.append("")
        for item in report.social[:limit]:
            date_str = f" ({item.date})" if item.date else " (date unknown)"
            conf_str = f" [date:{item.date_confidence}]" if item.date_confidence != "high" else ""

            eng_str = ""
            if item.engagement:
                eng = item.engagement
                parts = []
                if eng.views is not None:
                    parts.append(f"{eng.views:,}views")
                if eng.likes is not None:
                    parts.append(f"{eng.likes:,}likes")
                if eng.shares is not None:
                    parts.append(f"{eng.shares:,}shares")
                if parts:
                    eng_str = f" [{', '.join(parts)}]"

            platform_icon = {"tiktok": "🎵", "instagram": "📸", "facebook": "📘"}.get(item.platform, "📱")

            lines.append(f"**{item.id}** (score:{item.score}) {platform_icon} {item.platform}{date_str}{conf_str}{eng_str}")
            lines.append(f"  {item.title}")
            lines.append(f"  {item.url}")
            if item.author_handle:
                lines.append(f"  @{item.author_handle}")
            if item.why_relevant:
                lines.append(f"  *{item.why_relevant}*")
            lines.append("")
    elif not report.trends:
        lines.append("### Social Media Posts")
        lines.append("")
        lines.append("*No relevant social media posts found for this topic.*")
        lines.append("")

    return "\n".join(lines)


def render_context_snippet(report: schema.SocialReport) -> str:
    """Render reusable context snippet."""
    lines = []
    lines.append(f"# Context: {report.topic} - Social Media (Last 30 Days)")
    lines.append("")
    lines.append(f"*Generated: {report.generated_at[:10]} | Sources: {report.mode}*")
    lines.append("")

    lines.append("## Key Trends")
    lines.append("")
    for item in report.trends[:5]:
        lines.append(f"- [{item.platform}] {item.keyword} (score: {item.trend_score})")

    lines.append("")
    lines.append("## Top Social Posts")
    lines.append("")
    for item in report.social[:5]:
        lines.append(f"- [{item.platform}] {item.title}")

    lines.append("")
    return "\n".join(lines)


def render_full_report(report: schema.SocialReport) -> str:
    """Render full markdown report."""
    lines = []

    lines.append(f"# {report.topic} - Social Media Research Report (Last 30 Days)")
    lines.append("")
    lines.append(f"**Generated:** {report.generated_at}")
    lines.append(f"**Date Range:** {report.range_from} to {report.range_to}")
    lines.append(f"**Mode:** {report.mode}")
    lines.append("")

    if report.trends:
        lines.append("## Trending Topics")
        lines.append("")
        for item in report.trends:
            lines.append(f"### {item.id}: {item.keyword}")
            lines.append(f"- **Platform:** {item.platform}")
            lines.append(f"- **Trend Score:** {item.trend_score}/100")
            lines.append(f"- **Related:** {', '.join(item.related_topics)}")
            lines.append("")

    if report.social:
        lines.append("## Social Media Posts")
        lines.append("")
        for item in report.social:
            lines.append(f"### {item.id}: {item.title}")
            lines.append(f"- **Platform:** {item.platform}")
            lines.append(f"- **URL:** {item.url}")
            lines.append(f"- **Date:** {item.date or 'Unknown'}")
            lines.append(f"- **Score:** {item.score}/100")
            if item.engagement:
                eng = item.engagement
                lines.append(f"- **Engagement:** {eng.views or '?'} views, {eng.likes or '?'} likes")
            lines.append("")

    return "\n".join(lines)


def write_outputs(report: schema.SocialReport):
    """Write all output files."""
    ensure_output_dir()

    with open(OUTPUT_DIR / "report.json", 'w') as f:
        json.dump(report.to_dict(), f, indent=2)

    with open(OUTPUT_DIR / "report.md", 'w') as f:
        f.write(render_full_report(report))

    with open(OUTPUT_DIR / "social30days.context.md", 'w') as f:
        f.write(render_context_snippet(report))


def get_context_path() -> str:
    return str(OUTPUT_DIR / "social30days.context.md")
