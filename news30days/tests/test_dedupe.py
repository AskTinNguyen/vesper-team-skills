"""Tests for news30days deduplication."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib import schema, dedupe


def test_dedupe_identical():
    items = [
        schema.NewsItem(id="1", title="AI coding tools are amazing",
                        url="", source_name="Reuters", source_domain="reuters.com", score=80),
        schema.NewsItem(id="2", title="AI coding tools are amazing",
                        url="", source_name="BBC", source_domain="bbc.com", score=70),
    ]
    result = dedupe.dedupe_news(items)
    assert len(result) == 1
    assert result[0].id == "1"  # Keep higher scored


def test_dedupe_different():
    items = [
        schema.NewsItem(id="1", title="AI coding tools transform development",
                        url="", source_name="Reuters", source_domain="reuters.com", score=80),
        schema.NewsItem(id="2", title="Electric vehicles surge in Europe",
                        url="", source_name="BBC", source_domain="bbc.com", score=70),
    ]
    result = dedupe.dedupe_news(items)
    assert len(result) == 2


def test_dedupe_empty():
    assert dedupe.dedupe_news([]) == []


def test_dedupe_single():
    items = [
        schema.NewsItem(id="1", title="Test", url="", source_name="", source_domain=""),
    ]
    assert len(dedupe.dedupe_news(items)) == 1


if __name__ == "__main__":
    test_dedupe_identical()
    test_dedupe_different()
    test_dedupe_empty()
    test_dedupe_single()
    print("All news30days dedupe tests passed!")
