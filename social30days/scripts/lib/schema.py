"""Data schemas for social30days skill."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone


@dataclass
class SubScores:
    """Component scores."""
    relevance: int = 0
    recency: int = 0
    engagement: int = 0

    def to_dict(self) -> Dict[str, int]:
        return {
            'relevance': self.relevance,
            'recency': self.recency,
            'engagement': self.engagement,
        }


@dataclass
class SocialEngagement:
    """Social media engagement metrics."""
    views: Optional[int] = None
    likes: Optional[int] = None
    shares: Optional[int] = None
    comments: Optional[int] = None
    saves: Optional[int] = None
    platform: str = ""  # "tiktok", "instagram", "facebook"

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        if self.views is not None:
            d['views'] = self.views
        if self.likes is not None:
            d['likes'] = self.likes
        if self.shares is not None:
            d['shares'] = self.shares
        if self.comments is not None:
            d['comments'] = self.comments
        if self.saves is not None:
            d['saves'] = self.saves
        if self.platform:
            d['platform'] = self.platform
        return d if d else None


@dataclass
class SocialItem:
    """Normalized social media item."""
    id: str
    title: str
    url: str
    platform: str  # "tiktok", "instagram", "facebook"
    author_handle: str = ""
    date: Optional[str] = None
    date_confidence: str = "low"
    engagement: Optional[SocialEngagement] = None
    trend_category: Optional[str] = None  # "hashtag", "audio", "effect"
    relevance: float = 0.5
    why_relevant: str = ""
    subs: SubScores = field(default_factory=SubScores)
    score: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'platform': self.platform,
            'author_handle': self.author_handle,
            'date': self.date,
            'date_confidence': self.date_confidence,
            'engagement': self.engagement.to_dict() if self.engagement else None,
            'trend_category': self.trend_category,
            'relevance': self.relevance,
            'why_relevant': self.why_relevant,
            'subs': self.subs.to_dict(),
            'score': self.score,
        }


@dataclass
class TrendItem:
    """Trending topic/hashtag item."""
    id: str
    keyword: str
    platform: str  # "google_trends", "tiktok_creative"
    trend_score: int = 0  # 0-100
    related_topics: List[str] = field(default_factory=list)
    date: Optional[str] = None
    url: Optional[str] = None
    subs: SubScores = field(default_factory=SubScores)
    score: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'keyword': self.keyword,
            'platform': self.platform,
            'trend_score': self.trend_score,
            'related_topics': self.related_topics,
            'date': self.date,
            'url': self.url,
            'subs': self.subs.to_dict(),
            'score': self.score,
        }


@dataclass
class SocialReport:
    """Full social media research report."""
    topic: str
    range_from: str
    range_to: str
    generated_at: str
    mode: str  # 'free', 'all'
    social: List[SocialItem] = field(default_factory=list)
    trends: List[TrendItem] = field(default_factory=list)
    best_practices: List[str] = field(default_factory=list)
    context_snippet_md: str = ""
    # Source counts
    tiktok_count: int = 0
    google_trends_count: int = 0
    websearch_count: int = 0
    crowdtangle_count: int = 0
    # Status tracking
    tiktok_error: Optional[str] = None
    google_trends_error: Optional[str] = None
    websearch_error: Optional[str] = None
    crowdtangle_error: Optional[str] = None
    # Cache info
    from_cache: bool = False
    cache_age_hours: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {
            'topic': self.topic,
            'range': {
                'from': self.range_from,
                'to': self.range_to,
            },
            'generated_at': self.generated_at,
            'mode': self.mode,
            'social': [s.to_dict() for s in self.social],
            'trends': [t.to_dict() for t in self.trends],
            'best_practices': self.best_practices,
            'context_snippet_md': self.context_snippet_md,
            'tiktok_count': self.tiktok_count,
            'google_trends_count': self.google_trends_count,
            'websearch_count': self.websearch_count,
            'crowdtangle_count': self.crowdtangle_count,
        }
        if self.tiktok_error:
            d['tiktok_error'] = self.tiktok_error
        if self.google_trends_error:
            d['google_trends_error'] = self.google_trends_error
        if self.websearch_error:
            d['websearch_error'] = self.websearch_error
        if self.crowdtangle_error:
            d['crowdtangle_error'] = self.crowdtangle_error
        if self.from_cache:
            d['from_cache'] = self.from_cache
        if self.cache_age_hours is not None:
            d['cache_age_hours'] = self.cache_age_hours
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SocialReport":
        """Create SocialReport from serialized dict."""
        range_data = data.get('range', {})
        range_from = range_data.get('from', data.get('range_from', ''))
        range_to = range_data.get('to', data.get('range_to', ''))

        social_items = []
        for s in data.get('social', []):
            eng = None
            if s.get('engagement'):
                eng = SocialEngagement(**s['engagement'])
            subs = SubScores(**s.get('subs', {})) if s.get('subs') else SubScores()
            social_items.append(SocialItem(
                id=s['id'], title=s['title'], url=s['url'],
                platform=s.get('platform', ''),
                author_handle=s.get('author_handle', ''),
                date=s.get('date'),
                date_confidence=s.get('date_confidence', 'low'),
                engagement=eng,
                trend_category=s.get('trend_category'),
                relevance=s.get('relevance', 0.5),
                why_relevant=s.get('why_relevant', ''),
                subs=subs, score=s.get('score', 0),
            ))

        trend_items = []
        for t in data.get('trends', []):
            subs = SubScores(**t.get('subs', {})) if t.get('subs') else SubScores()
            trend_items.append(TrendItem(
                id=t['id'], keyword=t['keyword'],
                platform=t.get('platform', ''),
                trend_score=t.get('trend_score', 0),
                related_topics=t.get('related_topics', []),
                date=t.get('date'), url=t.get('url'),
                subs=subs, score=t.get('score', 0),
            ))

        return cls(
            topic=data['topic'],
            range_from=range_from, range_to=range_to,
            generated_at=data['generated_at'],
            mode=data['mode'],
            social=social_items, trends=trend_items,
            best_practices=data.get('best_practices', []),
            context_snippet_md=data.get('context_snippet_md', ''),
            tiktok_count=data.get('tiktok_count', 0),
            google_trends_count=data.get('google_trends_count', 0),
            websearch_count=data.get('websearch_count', 0),
            crowdtangle_count=data.get('crowdtangle_count', 0),
            tiktok_error=data.get('tiktok_error'),
            google_trends_error=data.get('google_trends_error'),
            websearch_error=data.get('websearch_error'),
            crowdtangle_error=data.get('crowdtangle_error'),
            from_cache=data.get('from_cache', False),
            cache_age_hours=data.get('cache_age_hours'),
        )


def create_report(topic: str, from_date: str, to_date: str, mode: str) -> SocialReport:
    """Create a new social report with metadata."""
    return SocialReport(
        topic=topic,
        range_from=from_date,
        range_to=to_date,
        generated_at=datetime.now(timezone.utc).isoformat(),
        mode=mode,
    )
