"""Data schemas for news30days skill."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone


@dataclass
class SubScores:
    """Component scores."""
    relevance: int = 0
    recency: int = 0
    engagement: int = 0
    authority: int = 0

    def to_dict(self) -> Dict[str, int]:
        return {
            'relevance': self.relevance,
            'recency': self.recency,
            'engagement': self.engagement,
            'authority': self.authority,
        }


@dataclass
class NewsItem:
    """Normalized news item."""
    id: str
    title: str
    url: str
    source_name: str
    source_domain: str
    author: Optional[str] = None
    published_at: Optional[str] = None
    date: Optional[str] = None
    date_confidence: str = "low"
    snippet: str = ""
    category: Optional[str] = None  # "tech", "business", "general"
    relevance: float = 0.5
    why_relevant: str = ""
    source_authority: int = 50  # 0-100
    subs: SubScores = field(default_factory=SubScores)
    score: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'source_name': self.source_name,
            'source_domain': self.source_domain,
            'author': self.author,
            'published_at': self.published_at,
            'date': self.date,
            'date_confidence': self.date_confidence,
            'snippet': self.snippet,
            'category': self.category,
            'relevance': self.relevance,
            'why_relevant': self.why_relevant,
            'source_authority': self.source_authority,
            'subs': self.subs.to_dict(),
            'score': self.score,
        }


@dataclass
class NewsReport:
    """Full news research report."""
    topic: str
    range_from: str
    range_to: str
    generated_at: str
    mode: str  # 'free', 'newsapi', 'bing', 'all'
    news: List[NewsItem] = field(default_factory=list)
    best_practices: List[str] = field(default_factory=list)
    context_snippet_md: str = ""
    # Source counts
    gnews_count: int = 0
    newsapi_count: int = 0
    bing_count: int = 0
    websearch_count: int = 0
    # Status tracking
    gnews_error: Optional[str] = None
    newsapi_error: Optional[str] = None
    bing_error: Optional[str] = None
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
            'news': [n.to_dict() for n in self.news],
            'best_practices': self.best_practices,
            'context_snippet_md': self.context_snippet_md,
            'gnews_count': self.gnews_count,
            'newsapi_count': self.newsapi_count,
            'bing_count': self.bing_count,
            'websearch_count': self.websearch_count,
        }
        if self.gnews_error:
            d['gnews_error'] = self.gnews_error
        if self.newsapi_error:
            d['newsapi_error'] = self.newsapi_error
        if self.bing_error:
            d['bing_error'] = self.bing_error
        if self.from_cache:
            d['from_cache'] = self.from_cache
        if self.cache_age_hours is not None:
            d['cache_age_hours'] = self.cache_age_hours
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NewsReport":
        """Create NewsReport from serialized dict."""
        range_data = data.get('range', {})
        range_from = range_data.get('from', data.get('range_from', ''))
        range_to = range_data.get('to', data.get('range_to', ''))

        news_items = []
        for n in data.get('news', []):
            subs = SubScores(**n.get('subs', {})) if n.get('subs') else SubScores()
            news_items.append(NewsItem(
                id=n['id'],
                title=n['title'],
                url=n['url'],
                source_name=n.get('source_name', ''),
                source_domain=n.get('source_domain', ''),
                author=n.get('author'),
                published_at=n.get('published_at'),
                date=n.get('date'),
                date_confidence=n.get('date_confidence', 'low'),
                snippet=n.get('snippet', ''),
                category=n.get('category'),
                relevance=n.get('relevance', 0.5),
                why_relevant=n.get('why_relevant', ''),
                source_authority=n.get('source_authority', 50),
                subs=subs,
                score=n.get('score', 0),
            ))

        return cls(
            topic=data['topic'],
            range_from=range_from,
            range_to=range_to,
            generated_at=data['generated_at'],
            mode=data['mode'],
            news=news_items,
            best_practices=data.get('best_practices', []),
            context_snippet_md=data.get('context_snippet_md', ''),
            gnews_count=data.get('gnews_count', 0),
            newsapi_count=data.get('newsapi_count', 0),
            bing_count=data.get('bing_count', 0),
            websearch_count=data.get('websearch_count', 0),
            gnews_error=data.get('gnews_error'),
            newsapi_error=data.get('newsapi_error'),
            bing_error=data.get('bing_error'),
            from_cache=data.get('from_cache', False),
            cache_age_hours=data.get('cache_age_hours'),
        )


def create_report(
    topic: str,
    from_date: str,
    to_date: str,
    mode: str,
) -> NewsReport:
    """Create a new news report with metadata."""
    return NewsReport(
        topic=topic,
        range_from=from_date,
        range_to=to_date,
        generated_at=datetime.now(timezone.utc).isoformat(),
        mode=mode,
    )
