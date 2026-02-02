"""Environment and API key management for news30days skill."""

import os
from pathlib import Path
from typing import Optional, Dict, Any

CONFIG_DIR = Path.home() / ".config" / "news30days"
CONFIG_FILE = CONFIG_DIR / ".env"


def load_env_file(path: Path) -> Dict[str, str]:
    """Load environment variables from a file."""
    env = {}
    if not path.exists():
        return env

    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, _, value = line.partition('=')
                key = key.strip()
                value = value.strip()
                if value and value[0] in ('"', "'") and value[-1] == value[0]:
                    value = value[1:-1]
                if key and value:
                    env[key] = value
    return env


def get_config() -> Dict[str, Any]:
    """Load configuration from ~/.config/news30days/.env and environment."""
    file_env = load_env_file(CONFIG_FILE)

    config = {
        'NEWSAPI_KEY': os.environ.get('NEWSAPI_KEY') or file_env.get('NEWSAPI_KEY'),
        'BING_NEWS_KEY': os.environ.get('BING_NEWS_KEY') or file_env.get('BING_NEWS_KEY'),
    }

    return config


def config_exists() -> bool:
    """Check if configuration file exists."""
    return CONFIG_FILE.exists()


def get_available_sources(config: Dict[str, Any]) -> str:
    """Determine which sources are available based on API keys.

    Returns: 'all', 'newsapi', 'bing', or 'free' (Google News RSS + WebSearch only)
    """
    has_newsapi = bool(config.get('NEWSAPI_KEY'))
    has_bing = bool(config.get('BING_NEWS_KEY'))

    if has_newsapi and has_bing:
        return 'all'
    elif has_newsapi:
        return 'newsapi'
    elif has_bing:
        return 'bing'
    else:
        return 'free'  # Google News RSS + WebSearch (no API keys needed)


def get_missing_keys(config: Dict[str, Any]) -> str:
    """Determine which API keys are missing.

    Returns: 'both', 'newsapi', 'bing', or 'none'
    """
    has_newsapi = bool(config.get('NEWSAPI_KEY'))
    has_bing = bool(config.get('BING_NEWS_KEY'))

    if has_newsapi and has_bing:
        return 'none'
    elif has_newsapi:
        return 'bing'
    elif has_bing:
        return 'newsapi'
    else:
        return 'both'


def validate_sources(requested: str, available: str) -> tuple[str, Optional[str]]:
    """Validate requested sources against available keys.

    Args:
        requested: 'auto', 'gnews', 'newsapi', 'bing', or 'all'
        available: Result from get_available_sources()

    Returns:
        Tuple of (effective_sources, error_message)
    """
    if requested == 'auto':
        return available, None

    if requested == 'gnews':
        return 'free', None  # Google News RSS always available

    if requested == 'newsapi':
        if available in ('all', 'newsapi'):
            return 'newsapi', None
        return 'free', "NEWSAPI_KEY not configured. Falling back to Google News RSS + WebSearch."

    if requested == 'bing':
        if available in ('all', 'bing'):
            return 'bing', None
        return 'free', "BING_NEWS_KEY not configured. Falling back to Google News RSS + WebSearch."

    if requested == 'all':
        if available == 'all':
            return 'all', None
        return available, f"Not all API keys configured. Using {available} mode."

    return requested, None
