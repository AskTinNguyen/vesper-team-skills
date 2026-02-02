"""Google Trends integration for social30days skill (free, no API key).

Uses the public Google Trends HTTP endpoints to get trend data.
"""

import json
import re
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus

from . import http


# Google Trends public endpoints
GOOGLE_TRENDS_SUGGESTIONS_URL = "https://trends.google.com/trends/api/autocomplete/{query}"
GOOGLE_TRENDS_INTEREST_URL = "https://trends.google.com/trends/api/widgetdata/multiline"
GOOGLE_TRENDS_RELATED_URL = "https://trends.google.com/trends/api/widgetdata/relatedsearches"


def search_google_trends(
    topic: str,
    depth: str = "default",
) -> List[Dict[str, Any]]:
    """Search Google Trends for interest and related queries.

    Args:
        topic: Search query
        depth: 'quick', 'default', or 'deep'

    Returns:
        List of trend item dicts
    """
    items = []

    # Try to get autocomplete suggestions (public endpoint)
    try:
        suggestions = _get_suggestions(topic)
        for i, suggestion in enumerate(suggestions[:10]):
            items.append({
                "id": f"GT{i+1}",
                "keyword": suggestion.get("title", topic),
                "platform": "google_trends",
                "trend_score": suggestion.get("score", 50),
                "related_topics": [],
                "date": None,
                "url": f"https://trends.google.com/trends/explore?q={quote_plus(suggestion.get('title', topic))}",
            })
    except Exception:
        # Fallback: create a single entry for the topic
        items.append({
            "id": "GT1",
            "keyword": topic,
            "platform": "google_trends",
            "trend_score": 50,
            "related_topics": [],
            "date": None,
            "url": f"https://trends.google.com/trends/explore?q={quote_plus(topic)}",
        })

    return items


def _get_suggestions(topic: str) -> List[Dict[str, Any]]:
    """Get autocomplete suggestions from Google Trends.

    Returns list of suggestion dicts with 'title' and optionally 'score'.
    """
    encoded = quote_plus(topic)
    url = f"https://trends.google.com/trends/api/autocomplete/{encoded}?hl=en-US"

    try:
        raw = http.get_raw(url)
    except http.HTTPError:
        return []

    # Google Trends API responses start with ")]}'" prefix
    if raw.startswith(")]}'"):
        raw = raw[5:]

    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return []

    suggestions = []
    topics = data.get("default", {}).get("topics", [])

    for topic_data in topics:
        title = topic_data.get("title", "")
        mid = topic_data.get("mid", "")
        topic_type = topic_data.get("type", "")

        if title:
            suggestions.append({
                "title": title,
                "mid": mid,
                "type": topic_type,
                "score": 50,  # Default score, would need interest-over-time API for real score
            })

    return suggestions


def search_google_trends_mock(fixture_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return mock Google Trends data."""
    return fixture_data


def generate_trends_search_queries(topic: str) -> List[str]:
    """Generate Google Trends-related search queries for WebSearch."""
    return [
        f'"{topic}" trending google trends',
        f'"{topic}" search interest rising',
        f'"{topic}" trend analysis',
    ]
