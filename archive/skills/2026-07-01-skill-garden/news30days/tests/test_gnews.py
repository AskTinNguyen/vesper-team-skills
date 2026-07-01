"""Tests for Google News RSS parsing."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib import gnews


SAMPLE_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>AI coding tools - Google News</title>
    <item>
      <title>AI Coding Tools Transform Development - Reuters</title>
      <link>https://news.google.com/rss/articles/redirect-reuters</link>
      <pubDate>Mon, 20 Jan 2026 14:30:00 GMT</pubDate>
      <description>&lt;p&gt;Major tech companies deploy AI assistants.&lt;/p&gt;</description>
    </item>
    <item>
      <title>GitHub Copilot Usage Doubles - BBC News</title>
      <link>https://news.google.com/rss/articles/redirect-bbc</link>
      <pubDate>Tue, 21 Jan 2026 09:00:00 GMT</pubDate>
      <description>Copilot subscriptions doubled year-over-year.</description>
    </item>
  </channel>
</rss>"""


def test_parse_gnews_rss():
    items = gnews.parse_gnews_rss(SAMPLE_RSS)
    assert len(items) == 2
    assert items[0]["source_name"] == "Reuters"
    assert items[0]["title"] == "AI Coding Tools Transform Development"
    assert items[0]["date"] == "2026-01-20"
    assert items[1]["source_name"] == "BBC News"


def test_parse_gnews_rss_empty():
    items = gnews.parse_gnews_rss("<rss><channel></channel></rss>")
    assert items == []


def test_parse_gnews_rss_invalid():
    items = gnews.parse_gnews_rss("not xml at all")
    assert items == []


def test_parse_rss_date():
    assert gnews._parse_rss_date("Mon, 20 Jan 2026 14:30:00 GMT") == "2026-01-20"
    assert gnews._parse_rss_date("") is None
    assert gnews._parse_rss_date(None) is None


def test_extract_source_from_title():
    assert gnews._extract_source_from_title("AI News - Reuters") == "Reuters"
    assert gnews._extract_source_from_title("Just a title") == ""


def test_clean_title():
    assert gnews._clean_title("AI News - Reuters") == "AI News"
    assert gnews._clean_title("Just a title") == "Just a title"


if __name__ == "__main__":
    test_parse_gnews_rss()
    test_parse_gnews_rss_empty()
    test_parse_gnews_rss_invalid()
    test_parse_rss_date()
    test_extract_source_from_title()
    test_clean_title()
    print("All gnews tests passed!")
