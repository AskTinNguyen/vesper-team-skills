"""Google News RSS integration for news30days skill (free, no API key needed)."""

import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus, urlparse

from . import http


GNEWS_RSS_URL = "https://news.google.com/rss/search"


def _parse_rss_date(date_str: str) -> Optional[str]:
    """Parse RSS date format to YYYY-MM-DD.

    RSS uses RFC 822: e.g., "Mon, 20 Jan 2026 14:30:00 GMT"
    """
    if not date_str:
        return None

    formats = [
        "%a, %d %b %Y %H:%M:%S %Z",
        "%a, %d %b %Y %H:%M:%S %z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S%z",
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue

    return None


def _extract_source_from_title(title: str) -> str:
    """Extract source name from Google News title format.

    Google News appends ' - Source Name' to titles.
    """
    if " - " in title:
        parts = title.rsplit(" - ", 1)
        if len(parts) == 2:
            return parts[1].strip()
    return ""


def _clean_title(title: str) -> str:
    """Remove source attribution from Google News title."""
    if " - " in title:
        parts = title.rsplit(" - ", 1)
        if len(parts) == 2:
            return parts[0].strip()
    return title


def search_gnews(
    topic: str,
    from_date: str = "",
    to_date: str = "",
    depth: str = "default",
) -> List[Dict[str, Any]]:
    """Search Google News RSS for a topic.

    Args:
        topic: Search query
        from_date: Start date (YYYY-MM-DD), used for filtering
        to_date: End date (YYYY-MM-DD), used for filtering
        depth: 'quick' (fewer), 'default', or 'deep' (more)

    Returns:
        List of normalized article dicts
    """
    # Build the RSS URL with query
    encoded_topic = quote_plus(topic)

    # Add date parameters if available
    params = f"q={encoded_topic}&hl=en-US&gl=US&ceid=US:en"

    # Google News RSS supports 'when:Xd' for recent results
    if from_date:
        params += "&when:30d"

    url = f"{GNEWS_RSS_URL}?{params}"

    try:
        raw_xml = http.get_raw(url)
    except http.HTTPError as e:
        raise RuntimeError(f"Google News RSS error: {e}")

    return parse_gnews_rss(raw_xml, from_date, to_date, depth)


def parse_gnews_rss(
    xml_content: str,
    from_date: str = "",
    to_date: str = "",
    depth: str = "default",
) -> List[Dict[str, Any]]:
    """Parse Google News RSS XML into normalized items.

    Args:
        xml_content: Raw XML string
        from_date: Start date filter
        to_date: End date filter
        depth: Controls max results

    Returns:
        List of article dicts
    """
    items = []

    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError:
        return items

    # Google News RSS uses standard RSS 2.0 format
    channel = root.find("channel")
    if channel is None:
        return items

    max_items = {"quick": 15, "default": 40, "deep": 80}.get(depth, 40)

    for i, item_elem in enumerate(channel.findall("item")):
        if i >= max_items:
            break

        raw_title = item_elem.findtext("title", "")
        link = item_elem.findtext("link", "")
        pub_date = item_elem.findtext("pubDate", "")
        description = item_elem.findtext("description", "")

        if not raw_title or not link:
            continue

        # Extract source and clean title
        source_name = _extract_source_from_title(raw_title)
        title = _clean_title(raw_title)

        # Parse date
        date = _parse_rss_date(pub_date)

        # Date filter
        if date and from_date and date < from_date:
            continue
        if date and to_date and date > to_date:
            continue

        # Clean description (Google News wraps in HTML)
        snippet = re.sub(r'<[^>]+>', '', description or "").strip()

        items.append({
            "id": f"GN{i+1}",
            "title": title[:300],
            "url": link,
            "source_name": source_name,
            "published_at": pub_date,
            "date": date,
            "snippet": snippet[:500],
            "relevance": 0.5,  # Default, will be adjusted by Claude
            "why_relevant": "",
        })

    return items


def search_gnews_mock(fixture_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return mock Google News data for testing."""
    return fixture_data
