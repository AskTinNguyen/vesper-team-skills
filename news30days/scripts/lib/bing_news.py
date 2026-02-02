"""Bing News API integration for news30days skill (optional, requires Azure key)."""

from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus, urlencode

from . import http


BING_NEWS_BASE = "https://api.bing.microsoft.com/v7.0/news/search"


def search_bing_news(
    api_key: str,
    topic: str,
    from_date: str = "",
    freshness: str = "Month",
    depth: str = "default",
) -> List[Dict[str, Any]]:
    """Search Bing News API for articles.

    Args:
        api_key: Bing News API key (Azure subscription)
        topic: Search query
        from_date: Start date (unused, Bing uses freshness parameter)
        freshness: 'Day', 'Week', or 'Month'
        depth: 'quick', 'default', or 'deep'

    Returns:
        List of normalized article dicts
    """
    count = {"quick": 15, "default": 40, "deep": 80}.get(depth, 40)

    params = {
        "q": topic,
        "count": count,
        "freshness": freshness,
        "mkt": "en-US",
        "sortBy": "Relevance",
    }

    url = f"{BING_NEWS_BASE}?{urlencode(params)}"

    headers = {
        "Ocp-Apim-Subscription-Key": api_key,
    }

    try:
        data = http.get(url, headers=headers)
    except http.HTTPError as e:
        raise RuntimeError(f"Bing News error: {e}")

    return parse_bing_response(data)


def parse_bing_response(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Parse Bing News response into normalized items."""
    items = []

    articles = data.get("value", [])

    for i, article in enumerate(articles):
        title = article.get("name", "")
        url = article.get("url", "")

        if not title or not url:
            continue

        # Parse date
        published_at = article.get("datePublished", "")
        date = None
        if published_at:
            date = published_at[:10] if len(published_at) >= 10 else None

        # Extract source
        providers = article.get("provider", [])
        source_name = providers[0].get("name", "") if providers else ""

        items.append({
            "id": f"BN{i+1}",
            "title": title[:300],
            "url": url,
            "source_name": source_name,
            "author": None,
            "published_at": published_at,
            "date": date,
            "snippet": (article.get("description") or "")[:500],
            "category": article.get("category"),
            "relevance": 0.6,
            "why_relevant": "",
        })

    return items


def search_bing_mock(fixture_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return mock Bing News data for testing."""
    return fixture_data
