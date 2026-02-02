"""Near-duplicate detection for social30days skill."""

import re
from typing import List, Set, Tuple, Union

from . import schema


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def get_ngrams(text: str, n: int = 3) -> Set[str]:
    text = normalize_text(text)
    if len(text) < n:
        return {text}
    return {text[i:i+n] for i in range(len(text) - n + 1)}


def jaccard_similarity(set1: Set[str], set2: Set[str]) -> float:
    if not set1 or not set2:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0


def dedupe_social(
    items: List[schema.SocialItem],
    threshold: float = 0.7,
) -> List[schema.SocialItem]:
    """Remove near-duplicate social items, keeping highest-scored."""
    if len(items) <= 1:
        return items

    ngrams = [get_ngrams(item.title) for item in items]

    to_remove = set()
    for i in range(len(items)):
        if i in to_remove:
            continue
        for j in range(i + 1, len(items)):
            if j in to_remove:
                continue
            if jaccard_similarity(ngrams[i], ngrams[j]) >= threshold:
                if items[i].score >= items[j].score:
                    to_remove.add(j)
                else:
                    to_remove.add(i)

    return [item for idx, item in enumerate(items) if idx not in to_remove]


def dedupe_trends(
    items: List[schema.TrendItem],
    threshold: float = 0.7,
) -> List[schema.TrendItem]:
    """Remove near-duplicate trend items."""
    if len(items) <= 1:
        return items

    ngrams = [get_ngrams(item.keyword) for item in items]

    to_remove = set()
    for i in range(len(items)):
        if i in to_remove:
            continue
        for j in range(i + 1, len(items)):
            if j in to_remove:
                continue
            if jaccard_similarity(ngrams[i], ngrams[j]) >= threshold:
                if items[i].score >= items[j].score:
                    to_remove.add(j)
                else:
                    to_remove.add(i)

    return [item for idx, item in enumerate(items) if idx not in to_remove]
