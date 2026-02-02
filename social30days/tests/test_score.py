"""Tests for social30days scoring."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib import schema, score


def test_log1p_safe():
    assert score.log1p_safe(None) == 0.0
    assert score.log1p_safe(-5) == 0.0
    assert score.log1p_safe(0) == 0.0
    assert score.log1p_safe(100) > 0


def test_compute_social_engagement_raw():
    eng = schema.SocialEngagement(views=100000, likes=5000, shares=1000, comments=200)
    raw = score.compute_social_engagement_raw(eng)
    assert raw is not None
    assert raw > 0


def test_compute_social_engagement_none():
    assert score.compute_social_engagement_raw(None) is None
    eng = schema.SocialEngagement()
    assert score.compute_social_engagement_raw(eng) is None


def test_score_social_items():
    items = [
        schema.SocialItem(
            id="CT1", title="Viral post", url="", platform="instagram",
            date="2026-01-20", date_confidence="high", relevance=0.9,
            engagement=schema.SocialEngagement(views=500000, likes=15000, shares=3000, comments=800),
        ),
        schema.SocialItem(
            id="CT2", title="Low engagement", url="", platform="facebook",
            date="2026-01-20", date_confidence="high", relevance=0.5,
            engagement=schema.SocialEngagement(views=100, likes=5, shares=1, comments=0),
        ),
    ]

    scored = score.score_social_items(items)
    assert scored[0].score > scored[1].score


def test_score_trend_items():
    items = [
        schema.TrendItem(id="GT1", keyword="hot topic", platform="google_trends", trend_score=90),
        schema.TrendItem(id="GT2", keyword="cold topic", platform="google_trends", trend_score=20),
    ]

    scored = score.score_trend_items(items)
    assert scored[0].score > scored[1].score


def test_sort_social_items():
    items = [
        schema.SocialItem(id="1", title="Low", url="", platform="tiktok", score=30),
        schema.SocialItem(id="2", title="High", url="", platform="instagram", score=80),
    ]

    sorted_items = score.sort_social_items(items)
    assert sorted_items[0].id == "2"
    assert sorted_items[1].id == "1"


if __name__ == "__main__":
    test_log1p_safe()
    test_compute_social_engagement_raw()
    test_compute_social_engagement_none()
    test_score_social_items()
    test_score_trend_items()
    test_sort_social_items()
    print("All social30days score tests passed!")
