"""News scoring with source authority for news30days skill."""

import math
from typing import List, Optional
from urllib.parse import urlparse

from . import dates, schema

# Score weights: 40% relevance / 30% recency / 15% engagement / 15% source authority
WEIGHT_RELEVANCE = 0.40
WEIGHT_RECENCY = 0.30
WEIGHT_ENGAGEMENT = 0.15
WEIGHT_AUTHORITY = 0.15

# Default values
DEFAULT_ENGAGEMENT = 30
UNKNOWN_ENGAGEMENT_PENALTY = 5

# Source authority tiers
TIER_1_DOMAINS = {
    "reuters.com", "apnews.com", "bbc.com", "bbc.co.uk",
    "nytimes.com", "wsj.com", "bloomberg.com", "washingtonpost.com",
    "ft.com", "economist.com", "ap.org",
}
TIER_1_SCORE = 90

TIER_2_DOMAINS = {
    "techcrunch.com", "theverge.com", "arstechnica.com", "cnbc.com",
    "theguardian.com", "wired.com", "cnn.com", "nbcnews.com",
    "abcnews.go.com", "forbes.com", "businessinsider.com",
    "engadget.com", "zdnet.com", "venturebeat.com", "protocol.com",
    "axios.com", "politico.com", "theatlantic.com", "newyorker.com",
    "latimes.com", "usatoday.com", "time.com", "nature.com",
    "science.org", "scientificamerican.com",
}
TIER_2_SCORE = 75

TIER_3_DOMAINS = {
    "9to5mac.com", "9to5google.com", "macrumors.com", "tomshardware.com",
    "pcmag.com", "cnet.com", "howtogeek.com", "tomsguide.com",
    "androidauthority.com", "xda-developers.com", "slashdot.org",
    "hackernews.com", "theregister.com", "semafor.com",
    "restofworld.org", "themarkup.org", "vice.com",
    "gizmodo.com", "lifehacker.com", "bgr.com",
}
TIER_3_SCORE = 60

TIER_4_SCORE = 40  # Everything else


def get_source_authority(domain: str) -> int:
    """Get source authority score based on domain.

    Tier 1 (90): Reuters, AP, BBC, NYT, WSJ, Bloomberg
    Tier 2 (75): TechCrunch, The Verge, Ars Technica, CNBC, Guardian
    Tier 3 (60): Industry blogs, regional papers, trade pubs
    Tier 4 (40): Personal blogs, unknown domains
    """
    if not domain:
        return TIER_4_SCORE

    # Normalize domain
    domain = domain.lower().strip()
    if domain.startswith("www."):
        domain = domain[4:]

    if domain in TIER_1_DOMAINS:
        return TIER_1_SCORE
    elif domain in TIER_2_DOMAINS:
        return TIER_2_SCORE
    elif domain in TIER_3_DOMAINS:
        return TIER_3_SCORE
    else:
        return TIER_4_SCORE


def score_news_items(items: List[schema.NewsItem]) -> List[schema.NewsItem]:
    """Compute scores for news items.

    Formula: 40% relevance + 30% recency + 15% engagement + 15% source authority
    """
    if not items:
        return items

    for item in items:
        # Relevance subscore (model-provided, convert to 0-100)
        rel_score = int(item.relevance * 100)

        # Recency subscore
        rec_score = dates.recency_score(item.date)

        # Engagement subscore (news items don't have engagement metrics from APIs)
        eng_score = DEFAULT_ENGAGEMENT

        # Authority subscore
        auth_score = item.source_authority or get_source_authority(item.source_domain)
        item.source_authority = auth_score

        # Store subscores
        item.subs = schema.SubScores(
            relevance=rel_score,
            recency=rec_score,
            engagement=eng_score,
            authority=auth_score,
        )

        # Compute overall score
        overall = (
            WEIGHT_RELEVANCE * rel_score +
            WEIGHT_RECENCY * rec_score +
            WEIGHT_ENGAGEMENT * eng_score +
            WEIGHT_AUTHORITY * auth_score
        )

        # Apply penalty for low date confidence
        if item.date_confidence == "low":
            overall -= 10
        elif item.date_confidence == "med":
            overall -= 5

        item.score = max(0, min(100, int(overall)))

    return items


def sort_items(items: List[schema.NewsItem]) -> List[schema.NewsItem]:
    """Sort items by score (descending), then date, then authority."""
    def sort_key(item):
        score = -item.score
        date = item.date or "0000-00-00"
        date_key = -int(date.replace("-", ""))
        auth_key = -item.source_authority
        return (score, date_key, auth_key, item.title)

    return sorted(items, key=sort_key)
