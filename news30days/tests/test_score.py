"""Tests for news30days scoring."""

import sys
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib import schema, score


def test_get_source_authority_tier1():
    assert score.get_source_authority("reuters.com") == 90
    assert score.get_source_authority("bbc.com") == 90
    assert score.get_source_authority("nytimes.com") == 90
    assert score.get_source_authority("www.reuters.com") == 90


def test_get_source_authority_tier2():
    assert score.get_source_authority("techcrunch.com") == 75
    assert score.get_source_authority("theverge.com") == 75
    assert score.get_source_authority("cnbc.com") == 75


def test_get_source_authority_tier3():
    assert score.get_source_authority("9to5mac.com") == 60
    assert score.get_source_authority("cnet.com") == 60


def test_get_source_authority_tier4():
    assert score.get_source_authority("randomblog.com") == 40
    assert score.get_source_authority("unknown.org") == 40
    assert score.get_source_authority("") == 40


def test_score_news_items():
    items = [
        schema.NewsItem(
            id="GN1",
            title="Reuters Article",
            url="https://reuters.com/article",
            source_name="Reuters",
            source_domain="reuters.com",
            date="2026-01-20",
            date_confidence="high",
            relevance=0.9,
            source_authority=90,
        ),
        schema.NewsItem(
            id="GN2",
            title="Blog Post",
            url="https://randomblog.com/post",
            source_name="Random Blog",
            source_domain="randomblog.com",
            date="2026-01-20",
            date_confidence="low",
            relevance=0.5,
            source_authority=40,
        ),
    ]

    scored = score.score_news_items(items)

    # Reuters should score higher than random blog
    assert scored[0].score > scored[1].score
    assert scored[0].subs.authority == 90
    assert scored[1].subs.authority == 40


def test_sort_items():
    items = [
        schema.NewsItem(id="1", title="Low", url="", source_name="", source_domain="",
                        score=30),
        schema.NewsItem(id="2", title="High", url="", source_name="", source_domain="",
                        score=80),
        schema.NewsItem(id="3", title="Med", url="", source_name="", source_domain="",
                        score=50),
    ]

    sorted_items = score.sort_items(items)
    assert sorted_items[0].id == "2"
    assert sorted_items[1].id == "3"
    assert sorted_items[2].id == "1"


if __name__ == "__main__":
    test_get_source_authority_tier1()
    test_get_source_authority_tier2()
    test_get_source_authority_tier3()
    test_get_source_authority_tier4()
    test_score_news_items()
    test_sort_items()
    print("All news30days score tests passed!")
