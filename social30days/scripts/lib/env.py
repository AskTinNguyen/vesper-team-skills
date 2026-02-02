"""Environment and API key management for social30days skill."""

import os
from pathlib import Path
from typing import Optional, Dict, Any

CONFIG_DIR = Path.home() / ".config" / "social30days"
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
    """Load configuration from ~/.config/social30days/.env and environment."""
    file_env = load_env_file(CONFIG_FILE)

    config = {
        'CROWDTANGLE_TOKEN': os.environ.get('CROWDTANGLE_TOKEN') or file_env.get('CROWDTANGLE_TOKEN'),
    }

    return config


def config_exists() -> bool:
    return CONFIG_FILE.exists()


def get_available_sources(config: Dict[str, Any]) -> str:
    """Determine which sources are available.

    Returns: 'all' (with CrowdTangle) or 'free' (public scraping + WebSearch)
    """
    has_crowdtangle = bool(config.get('CROWDTANGLE_TOKEN'))

    if has_crowdtangle:
        return 'all'
    else:
        return 'free'  # TikTok Creative + Google Trends + WebSearch (no keys needed)


def get_missing_keys(config: Dict[str, Any]) -> str:
    """Determine which API keys are missing."""
    has_crowdtangle = bool(config.get('CROWDTANGLE_TOKEN'))

    if has_crowdtangle:
        return 'none'
    else:
        return 'crowdtangle'


def validate_sources(requested: str, available: str) -> tuple[str, Optional[str]]:
    """Validate requested sources against available keys."""
    if requested == 'auto':
        return available, None

    if requested == 'free':
        return 'free', None

    if requested == 'crowdtangle':
        if available == 'all':
            return 'all', None
        return 'free', "CROWDTANGLE_TOKEN not configured. Using free sources."

    return requested, None
