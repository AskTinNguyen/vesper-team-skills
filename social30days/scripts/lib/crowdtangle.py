"""CrowdTangle / Meta Content Library integration for social30days skill.

Optional: Requires CROWDTANGLE_TOKEN in ~/.config/social30days/.env
Provides FB/IG post search with real engagement metrics.
"""

from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

from . import http


CROWDTANGLE_BASE = "https://api.crowdtangle.com"


def search_crowdtangle(
    token: str,
    topic: str,
    from_date: str = "",
    to_date: str = "",
    platforms: str = "facebook,instagram",
    depth: str = "default",
) -> List[Dict[str, Any]]:
    """Search CrowdTangle for social media posts.

    Args:
        token: CrowdTangle API token
        topic: Search query
        from_date: Start date (YYYY-MM-DD)
        to_date: End date (YYYY-MM-DD)
        platforms: Comma-separated platform list
        depth: 'quick', 'default', or 'deep'

    Returns:
        List of normalized social item dicts
    """
    count = {"quick": 15, "default": 40, "deep": 80}.get(depth, 40)

    params = {
        "token": token,
        "searchTerm": topic,
        "count": count,
        "sortBy": "total_interactions",
        "platforms": platforms,
    }

    if from_date:
        params["startDate"] = f"{from_date}T00:00:00"
    if to_date:
        params["endDate"] = f"{to_date}T23:59:59"

    url = f"{CROWDTANGLE_BASE}/posts/search?{urlencode(params)}"

    try:
        data = http.get(url)
    except http.HTTPError as e:
        raise RuntimeError(f"CrowdTangle error: {e}")

    return parse_crowdtangle_response(data)


def parse_crowdtangle_response(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Parse CrowdTangle response into normalized items."""
    items = []

    posts = data.get("result", {}).get("posts", [])

    for i, post in enumerate(posts):
        title = post.get("message", post.get("title", ""))[:300]
        url = post.get("postUrl", "")
        platform = post.get("platform", "").lower()

        if not title and not url:
            continue

        # Parse date
        date = None
        published = post.get("date", "")
        if published:
            date = published[:10] if len(published) >= 10 else None

        # Parse engagement
        stats = post.get("statistics", {}).get("actual", {})

        engagement = {
            "views": None,  # CrowdTangle doesn't always provide views
            "likes": stats.get("likeCount") or stats.get("favoriteCount"),
            "shares": stats.get("shareCount"),
            "comments": stats.get("commentCount"),
            "saves": None,
            "platform": platform,
        }

        account = post.get("account", {})
        author_handle = account.get("handle", account.get("name", ""))

        items.append({
            "id": f"CT{i+1}",
            "title": title,
            "url": url,
            "platform": platform,
            "author_handle": author_handle,
            "date": date,
            "engagement": engagement,
            "relevance": 0.6,
            "why_relevant": "",
        })

    return items


def search_crowdtangle_mock(fixture_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return mock CrowdTangle data."""
    return fixture_data
