"""NewsAPI.org integration for news30days skill (optional, requires API key)."""

from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus, urlencode

from . import http


NEWSAPI_BASE = "https://newsapi.org/v2"


def search_newsapi(
    api_key: str,
    topic: str,
    from_date: str = "",
    to_date: str = "",
    sort_by: str = "relevancy",
    depth: str = "default",
) -> List[Dict[str, Any]]:
    """Search NewsAPI.org for articles.

    Args:
        api_key: NewsAPI.org API key
        topic: Search query
        from_date: Start date (YYYY-MM-DD)
        to_date: End date (YYYY-MM-DD)
        sort_by: 'relevancy', 'popularity', or 'publishedAt'
        depth: 'quick', 'default', or 'deep'

    Returns:
        List of normalized article dicts
    """
    page_size = {"quick": 20, "default": 50, "deep": 100}.get(depth, 50)

    params = {
        "q": topic,
        "sortBy": sort_by,
        "pageSize": page_size,
        "language": "en",
    }

    if from_date:
        params["from"] = from_date
    if to_date:
        params["to"] = to_date

    url = f"{NEWSAPI_BASE}/everything?{urlencode(params)}"

    headers = {
        "X-Api-Key": api_key,
    }

    try:
        data = http.get(url, headers=headers)
    except http.HTTPError as e:
        raise RuntimeError(f"NewsAPI error: {e}")

    return parse_newsapi_response(data)


def parse_newsapi_response(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Parse NewsAPI response into normalized items."""
    items = []

    if data.get("status") != "ok":
        error_msg = data.get("message", "Unknown error")
        raise RuntimeError(f"NewsAPI returned error: {error_msg}")

    articles = data.get("articles", [])

    for i, article in enumerate(articles):
        title = article.get("title", "")
        url = article.get("url", "")

        if not title or not url:
            continue

        # Skip "[Removed]" articles (NewsAPI placeholder)
        if title == "[Removed]":
            continue

        # Parse date
        published_at = article.get("publishedAt", "")
        date = None
        if published_at:
            # NewsAPI uses ISO format: 2026-01-20T14:30:00Z
            date = published_at[:10] if len(published_at) >= 10 else None

        source = article.get("source", {})
        source_name = source.get("name", "")

        items.append({
            "id": f"NA{i+1}",
            "title": title[:300],
            "url": url,
            "source_name": source_name,
            "author": article.get("author"),
            "published_at": published_at,
            "date": date,
            "snippet": (article.get("description") or "")[:500],
            "relevance": 0.6,  # Higher default for API results
            "why_relevant": "",
        })

    return items


def search_newsapi_mock(fixture_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return mock NewsAPI data for testing."""
    return fixture_data
