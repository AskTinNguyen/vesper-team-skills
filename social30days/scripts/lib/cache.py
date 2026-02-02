"""Caching utilities for social30days skill."""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

CACHE_DIR = Path.home() / ".cache" / "social30days"
DEFAULT_TTL_HOURS = 24


def ensure_cache_dir():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def get_cache_key(topic: str, from_date: str, to_date: str, sources: str) -> str:
    key_data = f"{topic}|{from_date}|{to_date}|{sources}"
    return hashlib.sha256(key_data.encode()).hexdigest()[:16]


def get_cache_path(cache_key: str) -> Path:
    return CACHE_DIR / f"{cache_key}.json"


def is_cache_valid(cache_path: Path, ttl_hours: int = DEFAULT_TTL_HOURS) -> bool:
    if not cache_path.exists():
        return False
    try:
        stat = cache_path.stat()
        mtime = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
        now = datetime.now(timezone.utc)
        return (now - mtime).total_seconds() / 3600 < ttl_hours
    except OSError:
        return False


def load_cache(cache_key: str, ttl_hours: int = DEFAULT_TTL_HOURS) -> Optional[dict]:
    cache_path = get_cache_path(cache_key)
    if not is_cache_valid(cache_path, ttl_hours):
        return None
    try:
        with open(cache_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def save_cache(cache_key: str, data: dict):
    ensure_cache_dir()
    try:
        with open(get_cache_path(cache_key), 'w') as f:
            json.dump(data, f)
    except OSError:
        pass


def clear_cache():
    if CACHE_DIR.exists():
        for f in CACHE_DIR.glob("*.json"):
            try:
                f.unlink()
            except OSError:
                pass
