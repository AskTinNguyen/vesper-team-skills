"""Site-targeted WebSearch queries for news outlets.

NOTE: This module generates search queries for Claude's WebSearch tool.
The actual WebSearch execution happens in Claude's session, not in Python.
"""

from typing import List


# Major news outlet domains for site-targeted searches
TIER_1_OUTLETS = [
    "reuters.com",
    "apnews.com",
    "bbc.com",
    "nytimes.com",
    "wsj.com",
    "bloomberg.com",
]

TIER_2_OUTLETS = [
    "techcrunch.com",
    "theverge.com",
    "arstechnica.com",
    "cnbc.com",
    "theguardian.com",
    "wired.com",
]


def generate_search_queries(
    topic: str,
    depth: str = "default",
) -> List[str]:
    """Generate site-targeted WebSearch queries for news outlets.

    Args:
        topic: Search topic
        depth: 'quick', 'default', or 'deep'

    Returns:
        List of search query strings for Claude to use with WebSearch
    """
    queries = []

    # General news queries
    queries.append(f'"{topic}" news')
    queries.append(f'"{topic}" latest')

    if depth == "quick":
        # Just Tier 1
        for outlet in TIER_1_OUTLETS[:3]:
            queries.append(f'"{topic}" site:{outlet}')
    elif depth == "deep":
        # All Tier 1 + Tier 2
        for outlet in TIER_1_OUTLETS:
            queries.append(f'"{topic}" site:{outlet}')
        for outlet in TIER_2_OUTLETS:
            queries.append(f'"{topic}" site:{outlet}')
    else:
        # Default: Tier 1 + some Tier 2
        for outlet in TIER_1_OUTLETS:
            queries.append(f'"{topic}" site:{outlet}')
        for outlet in TIER_2_OUTLETS[:3]:
            queries.append(f'"{topic}" site:{outlet}')

    return queries


def get_websearch_instructions(topic: str, from_date: str, to_date: str) -> str:
    """Generate WebSearch instructions for Claude."""
    queries = generate_search_queries(topic)
    query_list = "\n".join(f"  - {q}" for q in queries[:8])

    return f"""### WEBSEARCH REQUIRED ###
Topic: {topic}
Date range: {from_date} to {to_date}

Claude: Use your WebSearch tool with these queries to find news coverage:
{query_list}

FOCUS ON: Major news outlets, reputable journalism, expert analysis
INCLUDE: Reuters, AP, BBC, NYT, WSJ, Bloomberg, TechCrunch, The Verge
TIMEFRAME: Last 30 days only

After searching, synthesize WebSearch results WITH the Google News/API
results above. Authority-weighted scoring applies."""
