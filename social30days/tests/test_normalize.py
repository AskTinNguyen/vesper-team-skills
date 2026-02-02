"""Tests for social30days normalization."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib import normalize, schema


def test_normalize_social_items():
    items = [
        {
            "id": "CT1",
            "title": "Viral AI post",
            "url": "https://instagram.com/p/test",
            "platform": "instagram",
            "author_handle": "techguru",
            "date": "2026-01-20",
            "engagement": {
                "views": 500000,
                "likes": 15000,
                "shares": 3000,
                "comments": 800,
                "platform": "instagram",
            },
            "relevance": 0.9,
        }
    ]

    result = normalize.normalize_social_items(items, "2026-01-01", "2026-01-31")
    assert len(result) == 1
    assert isinstance(result[0], schema.SocialItem)
    assert result[0].platform == "instagram"
    assert result[0].engagement.views == 500000


def test_normalize_trend_items():
    items = [
        {
            "id": "GT1",
            "keyword": "AI coding",
            "platform": "google_trends",
            "trend_score": 85,
            "related_topics": ["cursor", "copilot"],
        }
    ]

    result = normalize.normalize_trend_items(items)
    assert len(result) == 1
    assert isinstance(result[0], schema.TrendItem)
    assert result[0].trend_score == 85


def test_filter_by_date_range():
    items = [
        schema.SocialItem(id="1", title="In range", url="", platform="tiktok",
                          date="2026-01-15"),
        schema.SocialItem(id="2", title="Too old", url="", platform="instagram",
                          date="2025-12-01"),
        schema.SocialItem(id="3", title="No date", url="", platform="facebook",
                          date=None),
    ]

    result = normalize.filter_by_date_range(items, "2026-01-01", "2026-01-31")
    assert len(result) == 2
    assert result[0].id == "1"
    assert result[1].id == "3"


if __name__ == "__main__":
    test_normalize_social_items()
    test_normalize_trend_items()
    test_filter_by_date_range()
    print("All social30days normalize tests passed!")
