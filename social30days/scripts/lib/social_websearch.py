"""Site-targeted WebSearch queries for social media platforms.

NOTE: This module generates search queries for Claude's WebSearch tool.
The actual WebSearch execution happens in Claude's session, not in Python.
"""

from typing import List


def generate_search_queries(
    topic: str,
    depth: str = "default",
) -> List[str]:
    """Generate site-targeted WebSearch queries for social platforms.

    Args:
        topic: Search topic
        depth: 'quick', 'default', or 'deep'

    Returns:
        List of search query strings for Claude to use with WebSearch
    """
    queries = []

    # TikTok queries
    queries.append(f'"{topic}" site:tiktok.com')
    queries.append(f'"{topic}" tiktok viral')

    # Instagram queries
    queries.append(f'"{topic}" site:instagram.com')
    queries.append(f'"{topic}" instagram viral')

    # Facebook queries
    queries.append(f'"{topic}" site:facebook.com')

    # General social
    queries.append(f'"{topic}" viral social media')
    queries.append(f'"{topic}" trending social')

    if depth == "deep":
        # Additional depth queries
        queries.append(f'"{topic}" tiktok trend 2026')
        queries.append(f'"{topic}" instagram reels trending')
        queries.append(f'"{topic}" facebook viral post')
        queries.append(f'#{topic.replace(" ", "")} viral')
        queries.append(f'"{topic}" social media engagement')

    return queries


def get_websearch_instructions(topic: str, from_date: str, to_date: str) -> str:
    """Generate WebSearch instructions for Claude."""
    queries = generate_search_queries(topic)
    query_list = "\n".join(f"  - {q}" for q in queries[:10])

    return f"""### WEBSEARCH REQUIRED ###
Topic: {topic}
Date range: {from_date} to {to_date}

Claude: Use your WebSearch tool with these queries to find social media content:
{query_list}

FOCUS ON: Viral content, trending posts, engagement metrics
PLATFORMS: TikTok, Instagram, Facebook
INCLUDE: Viral posts, trending hashtags, popular creators, engagement data
TIMEFRAME: Last 30 days only

After searching, synthesize WebSearch results WITH the TikTok Creative Center
and Google Trends data above. Social engagement scoring applies."""
