"""Tests for news30days normalization."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib import normalize, schema


def test_normalize_gnews_items():
    items = [
        {
            "id": "GN1",
            "title": "Test Article",
            "url": "https://reuters.com/article/test",
            "source_name": "Reuters",
            "date": "2026-01-20",
            "snippet": "Test snippet",
            "relevance": 0.8,
        }
    ]

    result = normalize.normalize_gnews_items(items, "2026-01-01", "2026-01-31")
    assert len(result) == 1
    assert isinstance(result[0], schema.NewsItem)
    assert result[0].source_domain == "reuters.com"
    assert result[0].source_authority == 90  # Tier 1


def test_filter_by_date_range():
    items = [
        schema.NewsItem(id="1", title="In range", url="", source_name="", source_domain="",
                        date="2026-01-15"),
        schema.NewsItem(id="2", title="Too old", url="", source_name="", source_domain="",
                        date="2025-12-01"),
        schema.NewsItem(id="3", title="No date", url="", source_name="", source_domain="",
                        date=None),
    ]

    result = normalize.filter_by_date_range(items, "2026-01-01", "2026-01-31")
    assert len(result) == 2  # In range + no date
    assert result[0].id == "1"
    assert result[1].id == "3"


def test_filter_by_date_range_require_date():
    items = [
        schema.NewsItem(id="1", title="Has date", url="", source_name="", source_domain="",
                        date="2026-01-15"),
        schema.NewsItem(id="2", title="No date", url="", source_name="", source_domain="",
                        date=None),
    ]

    result = normalize.filter_by_date_range(items, "2026-01-01", "2026-01-31", require_date=True)
    assert len(result) == 1
    assert result[0].id == "1"


if __name__ == "__main__":
    test_normalize_gnews_items()
    test_filter_by_date_range()
    test_filter_by_date_range_require_date()
    print("All news30days normalize tests passed!")
