"""Normalization of raw news data to canonical schema."""

from typing import Any, Dict, List
from urllib.parse import urlparse

from . import dates, schema, score as score_module


def filter_by_date_range(
    items: List[schema.NewsItem],
    from_date: str,
    to_date: str,
    require_date: bool = False,
) -> List[schema.NewsItem]:
    """Hard filter: Remove items outside the date range."""
    result = []
    for item in items:
        if item.date is None:
            if not require_date:
                result.append(item)
            continue

        if item.date < from_date:
            continue
        if item.date > to_date:
            continue

        result.append(item)

    return result


def _extract_domain(url: str) -> str:
    """Extract clean domain from URL."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except Exception:
        return ""


def normalize_gnews_items(
    items: List[Dict[str, Any]],
    from_date: str,
    to_date: str,
) -> List[schema.NewsItem]:
    """Normalize Google News RSS items to schema."""
    normalized = []

    for item in items:
        date_str = item.get("date")
        date_confidence = dates.get_date_confidence(date_str, from_date, to_date)
        domain = _extract_domain(item.get("url", ""))

        normalized.append(schema.NewsItem(
            id=item.get("id", ""),
            title=item.get("title", ""),
            url=item.get("url", ""),
            source_name=item.get("source_name", ""),
            source_domain=domain,
            author=item.get("author"),
            published_at=item.get("published_at"),
            date=date_str,
            date_confidence=date_confidence,
            snippet=item.get("snippet", ""),
            category=item.get("category"),
            relevance=item.get("relevance", 0.5),
            why_relevant=item.get("why_relevant", ""),
            source_authority=score_module.get_source_authority(domain),
        ))

    return normalized


def normalize_newsapi_items(
    items: List[Dict[str, Any]],
    from_date: str,
    to_date: str,
) -> List[schema.NewsItem]:
    """Normalize NewsAPI.org items to schema."""
    normalized = []

    for item in items:
        date_str = item.get("date")
        date_confidence = dates.get_date_confidence(date_str, from_date, to_date)
        domain = _extract_domain(item.get("url", ""))

        normalized.append(schema.NewsItem(
            id=item.get("id", ""),
            title=item.get("title", ""),
            url=item.get("url", ""),
            source_name=item.get("source_name", ""),
            source_domain=domain,
            author=item.get("author"),
            published_at=item.get("published_at"),
            date=date_str,
            date_confidence=date_confidence,
            snippet=item.get("snippet", ""),
            category=item.get("category"),
            relevance=item.get("relevance", 0.6),  # Higher default relevance for API results
            why_relevant=item.get("why_relevant", ""),
            source_authority=score_module.get_source_authority(domain),
        ))

    return normalized


def normalize_bing_items(
    items: List[Dict[str, Any]],
    from_date: str,
    to_date: str,
) -> List[schema.NewsItem]:
    """Normalize Bing News items to schema."""
    normalized = []

    for item in items:
        date_str = item.get("date")
        date_confidence = dates.get_date_confidence(date_str, from_date, to_date)
        domain = _extract_domain(item.get("url", ""))

        normalized.append(schema.NewsItem(
            id=item.get("id", ""),
            title=item.get("title", ""),
            url=item.get("url", ""),
            source_name=item.get("source_name", ""),
            source_domain=domain,
            author=item.get("author"),
            published_at=item.get("published_at"),
            date=date_str,
            date_confidence=date_confidence,
            snippet=item.get("snippet", ""),
            category=item.get("category"),
            relevance=item.get("relevance", 0.6),
            why_relevant=item.get("why_relevant", ""),
            source_authority=score_module.get_source_authority(domain),
        ))

    return normalized
