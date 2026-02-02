"""Tests for social30days deduplication."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib import schema, dedupe


def test_dedupe_social_identical():
    items = [
        schema.SocialItem(id="1", title="AI coding tools are amazing viral post",
                          url="", platform="tiktok", score=80),
        schema.SocialItem(id="2", title="AI coding tools are amazing viral post",
                          url="", platform="instagram", score=70),
    ]
    result = dedupe.dedupe_social(items)
    assert len(result) == 1
    assert result[0].id == "1"


def test_dedupe_social_different():
    items = [
        schema.SocialItem(id="1", title="AI coding revolution",
                          url="", platform="tiktok", score=80),
        schema.SocialItem(id="2", title="Best dance challenge 2026",
                          url="", platform="instagram", score=70),
    ]
    result = dedupe.dedupe_social(items)
    assert len(result) == 2


def test_dedupe_trends():
    items = [
        schema.TrendItem(id="1", keyword="AI coding", platform="google_trends", score=80),
        schema.TrendItem(id="2", keyword="AI coding", platform="tiktok_creative", score=70),
    ]
    result = dedupe.dedupe_trends(items)
    assert len(result) == 1


def test_dedupe_empty():
    assert dedupe.dedupe_social([]) == []
    assert dedupe.dedupe_trends([]) == []


if __name__ == "__main__":
    test_dedupe_social_identical()
    test_dedupe_social_different()
    test_dedupe_trends()
    test_dedupe_empty()
    print("All social30days dedupe tests passed!")
