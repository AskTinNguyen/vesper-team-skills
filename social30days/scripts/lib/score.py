"""Social engagement scoring for social30days skill."""

import math
from typing import List, Optional

from . import dates, schema

# Score weights: 40% relevance / 25% recency / 35% engagement
WEIGHT_RELEVANCE = 0.40
WEIGHT_RECENCY = 0.25
WEIGHT_ENGAGEMENT = 0.35

# Trend weights: 50% relevance / 50% trend_score
TREND_WEIGHT_RELEVANCE = 0.50
TREND_WEIGHT_SCORE = 0.50

DEFAULT_ENGAGEMENT = 30
UNKNOWN_ENGAGEMENT_PENALTY = 10


def log1p_safe(x: Optional[int]) -> float:
    """Safe log1p that handles None and negative values."""
    if x is None or x < 0:
        return 0.0
    return math.log1p(x)


def compute_social_engagement_raw(engagement: Optional[schema.SocialEngagement]) -> Optional[float]:
    """Compute raw engagement score for social item.

    Formula: 0.35*log1p(views) + 0.25*log1p(likes) + 0.25*log1p(shares) + 0.15*log1p(comments)
    """
    if engagement is None:
        return None

    if engagement.views is None and engagement.likes is None:
        return None

    views = log1p_safe(engagement.views)
    likes = log1p_safe(engagement.likes)
    shares = log1p_safe(engagement.shares)
    comments = log1p_safe(engagement.comments)

    return 0.35 * views + 0.25 * likes + 0.25 * shares + 0.15 * comments


def normalize_to_100(values: List[Optional[float]], default: float = 50) -> List[Optional[float]]:
    """Normalize a list of values to 0-100 scale."""
    valid = [v for v in values if v is not None]
    if not valid:
        return [default if v is None else 50 for v in values]

    min_val = min(valid)
    max_val = max(valid)
    range_val = max_val - min_val

    if range_val == 0:
        return [50 if v is None else 50 for v in values]

    result = []
    for v in values:
        if v is None:
            result.append(None)
        else:
            result.append(((v - min_val) / range_val) * 100)

    return result


def score_social_items(items: List[schema.SocialItem]) -> List[schema.SocialItem]:
    """Compute scores for social items.

    Formula: 40% relevance + 25% recency + 35% engagement
    """
    if not items:
        return items

    eng_raw = [compute_social_engagement_raw(item.engagement) for item in items]
    eng_normalized = normalize_to_100(eng_raw)

    for i, item in enumerate(items):
        rel_score = int(item.relevance * 100)
        rec_score = dates.recency_score(item.date)

        if eng_normalized[i] is not None:
            eng_score = int(eng_normalized[i])
        else:
            eng_score = DEFAULT_ENGAGEMENT

        item.subs = schema.SubScores(
            relevance=rel_score,
            recency=rec_score,
            engagement=eng_score,
        )

        overall = (
            WEIGHT_RELEVANCE * rel_score +
            WEIGHT_RECENCY * rec_score +
            WEIGHT_ENGAGEMENT * eng_score
        )

        if eng_raw[i] is None:
            overall -= UNKNOWN_ENGAGEMENT_PENALTY

        if item.date_confidence == "low":
            overall -= 10
        elif item.date_confidence == "med":
            overall -= 5

        item.score = max(0, min(100, int(overall)))

    return items


def score_trend_items(items: List[schema.TrendItem]) -> List[schema.TrendItem]:
    """Compute scores for trend items."""
    if not items:
        return items

    for item in items:
        trend_score = min(100, max(0, item.trend_score))

        item.subs = schema.SubScores(
            relevance=trend_score,
            recency=dates.recency_score(item.date) if item.date else 50,
            engagement=trend_score,
        )

        overall = (
            TREND_WEIGHT_RELEVANCE * trend_score +
            TREND_WEIGHT_SCORE * trend_score
        )

        item.score = max(0, min(100, int(overall)))

    return items


def sort_social_items(items: List[schema.SocialItem]) -> List[schema.SocialItem]:
    """Sort social items by score (descending)."""
    def sort_key(item):
        score = -item.score
        date = item.date or "0000-00-00"
        date_key = -int(date.replace("-", ""))
        return (score, date_key, item.title)

    return sorted(items, key=sort_key)


def sort_trend_items(items: List[schema.TrendItem]) -> List[schema.TrendItem]:
    """Sort trend items by score (descending)."""
    return sorted(items, key=lambda x: (-x.score, x.keyword))
