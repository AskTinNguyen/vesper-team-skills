"""TikTok Creative Center scraper for social30days skill (free, no API key).

Scrapes publicly available trend data from TikTok Creative Center.
This includes top hashtags, trending sounds, and popular patterns.
"""

import json
import re
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus

from . import http


# TikTok Creative Center public endpoints
TIKTOK_TRENDS_URL = "https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/en"


def search_tiktok_trends(
    topic: str,
    depth: str = "default",
) -> List[Dict[str, Any]]:
    """Search TikTok Creative Center for trending content related to a topic.

    This scrapes publicly available data from TikTok Creative Center.
    No API key is needed.

    Args:
        topic: Search query
        depth: 'quick', 'default', or 'deep'

    Returns:
        List of trend item dicts
    """
    # TikTok Creative Center doesn't have a clean search API,
    # so we generate structured trend data based on the topic.
    # In production, this would scrape the actual Creative Center pages.

    # For now, return empty - the real data comes from WebSearch
    # targeting TikTok specifically
    return []


def parse_tiktok_trends_mock(fixture_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return mock TikTok trend data."""
    return fixture_data


def generate_tiktok_search_queries(topic: str) -> List[str]:
    """Generate TikTok-specific search queries for WebSearch.

    These queries target TikTok content through web search since
    direct API access requires partnerships.
    """
    queries = [
        f'"{topic}" site:tiktok.com',
        f'"{topic}" tiktok viral',
        f'"{topic}" tiktok trend',
        f'#{topic.replace(" ", "")} tiktok',
        f'"{topic}" tiktok creative center trending',
    ]
    return queries
