"""Normalization of raw social data to canonical schema."""

from typing import Any, Dict, List

from . import dates, schema


def filter_by_date_range(
    items: List[schema.SocialItem],
    from_date: str,
    to_date: str,
    require_date: bool = False,
) -> List[schema.SocialItem]:
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


def normalize_social_items(
    items: List[Dict[str, Any]],
    from_date: str,
    to_date: str,
) -> List[schema.SocialItem]:
    """Normalize raw social items to schema."""
    normalized = []

    for item in items:
        date_str = item.get("date")
        date_confidence = dates.get_date_confidence(date_str, from_date, to_date)

        engagement = None
        eng_raw = item.get("engagement")
        if isinstance(eng_raw, dict):
            engagement = schema.SocialEngagement(
                views=eng_raw.get("views"),
                likes=eng_raw.get("likes"),
                shares=eng_raw.get("shares"),
                comments=eng_raw.get("comments"),
                saves=eng_raw.get("saves"),
                platform=eng_raw.get("platform", ""),
            )

        normalized.append(schema.SocialItem(
            id=item.get("id", ""),
            title=item.get("title", ""),
            url=item.get("url", ""),
            platform=item.get("platform", ""),
            author_handle=item.get("author_handle", ""),
            date=date_str,
            date_confidence=date_confidence,
            engagement=engagement,
            trend_category=item.get("trend_category"),
            relevance=item.get("relevance", 0.5),
            why_relevant=item.get("why_relevant", ""),
        ))

    return normalized


def normalize_trend_items(
    items: List[Dict[str, Any]],
) -> List[schema.TrendItem]:
    """Normalize raw trend items to schema."""
    normalized = []

    for item in items:
        normalized.append(schema.TrendItem(
            id=item.get("id", ""),
            keyword=item.get("keyword", ""),
            platform=item.get("platform", ""),
            trend_score=item.get("trend_score", 0),
            related_topics=item.get("related_topics", []),
            date=item.get("date"),
            url=item.get("url"),
        ))

    return normalized
