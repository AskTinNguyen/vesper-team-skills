"""Terminal UI utilities for news30days skill."""

import sys
import time
import threading
import random
from typing import Optional

IS_TTY = sys.stderr.isatty()


class Colors:
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'


BANNER = f"""{Colors.BLUE}{Colors.BOLD}
  ███╗   ██╗███████╗██╗    ██╗███████╗██████╗  ██████╗ ██████╗  █████╗ ██╗   ██╗███████╗
  ████╗  ██║██╔════╝██║    ██║██╔════╝╚════██╗██╔═████╗██╔══██╗██╔══██╗╚██╗ ██╔╝██╔════╝
  ██╔██╗ ██║█████╗  ██║ █╗ ██║███████╗ █████╔╝██║██╔██║██║  ██║███████║ ╚████╔╝ ███████╗
  ██║╚██╗██║██╔══╝  ██║███╗██║╚════██║ ╚═══██╗████╔╝██║██║  ██║██╔══██║  ╚██╔╝  ╚════██║
  ██║ ╚████║███████╗╚███╔███╔╝███████║██████╔╝╚██████╔╝██████╔╝██║  ██║   ██║   ███████║
  ╚═╝  ╚═══╝╚══════╝ ╚══╝╚══╝ ╚══════╝╚═════╝  ╚═════╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝
{Colors.RESET}{Colors.DIM}  30 days of news. Every angle covered.{Colors.RESET}
"""

MINI_BANNER = f"""{Colors.BLUE}{Colors.BOLD}/news30days{Colors.RESET} {Colors.DIM}· scanning headlines...{Colors.RESET}"""

GNEWS_MESSAGES = [
    "Scanning Google News headlines...",
    "Reading the latest news...",
    "Checking news feeds...",
    "Finding trending stories...",
    "Gathering headlines...",
]

NEWSAPI_MESSAGES = [
    "Searching NewsAPI archives...",
    "Querying news databases...",
    "Finding articles across outlets...",
    "Scanning news sources...",
]

BING_MESSAGES = [
    "Checking Bing News...",
    "Searching news index...",
    "Finding relevant coverage...",
]

WEBSEARCH_MESSAGES = [
    "Searching news outlets...",
    "Finding targeted coverage...",
    "Scanning major outlets...",
]

PROCESSING_MESSAGES = [
    "Ranking by authority...",
    "Scoring and ranking...",
    "Assessing source credibility...",
    "Removing duplicates...",
    "Organizing findings...",
]

PROMO_MESSAGE = f"""
{Colors.YELLOW}{Colors.BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.RESET}
{Colors.YELLOW}⚡ UNLOCK MORE NEWS SOURCES{Colors.RESET}

{Colors.DIM}Right now you're using Google News RSS + WebSearch. Add API keys to unlock:{Colors.RESET}

  {Colors.BLUE}📰 NewsAPI.org{Colors.RESET} - 80,000+ sources, sorting by relevancy/popularity
     └─ Add NEWSAPI_KEY (free tier: 100 req/day)

  {Colors.CYAN}🔍 Bing News{Colors.RESET} - Category filtering, freshness controls
     └─ Add BING_NEWS_KEY (Azure subscription)

{Colors.DIM}Setup:{Colors.RESET} Edit {Colors.BOLD}~/.config/news30days/.env{Colors.RESET}
{Colors.YELLOW}{Colors.BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.RESET}
"""

PROMO_MESSAGE_PLAIN = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ UNLOCK MORE NEWS SOURCES

Right now you're using Google News RSS + WebSearch. Add API keys to unlock:

  📰 NewsAPI.org - 80,000+ sources, sorting by relevancy/popularity
     └─ Add NEWSAPI_KEY (free tier: 100 req/day)

  🔍 Bing News - Category filtering, freshness controls
     └─ Add BING_NEWS_KEY (Azure subscription)

Setup: Edit ~/.config/news30days/.env
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

PROMO_SINGLE_KEY = {
    "newsapi": f"""
{Colors.DIM}💡 Tip: Add {Colors.BLUE}NEWSAPI_KEY{Colors.RESET}{Colors.DIM} to ~/.config/news30days/.env for 80,000+ news sources!{Colors.RESET}
""",
    "bing": f"""
{Colors.DIM}💡 Tip: Add {Colors.CYAN}BING_NEWS_KEY{Colors.RESET}{Colors.DIM} to ~/.config/news30days/.env for Bing News with category filtering!{Colors.RESET}
""",
}

PROMO_SINGLE_KEY_PLAIN = {
    "newsapi": "\n💡 Tip: Add NEWSAPI_KEY to ~/.config/news30days/.env for 80,000+ news sources!\n",
    "bing": "\n💡 Tip: Add BING_NEWS_KEY to ~/.config/news30days/.env for Bing News with category filtering!\n",
}

SPINNER_FRAMES = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']


class Spinner:
    """Animated spinner for long-running operations."""

    def __init__(self, message: str = "Working", color: str = Colors.CYAN):
        self.message = message
        self.color = color
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.frame_idx = 0
        self.shown_static = False

    def _spin(self):
        while self.running:
            frame = SPINNER_FRAMES[self.frame_idx % len(SPINNER_FRAMES)]
            sys.stderr.write(f"\r{self.color}{frame}{Colors.RESET} {self.message}  ")
            sys.stderr.flush()
            self.frame_idx += 1
            time.sleep(0.08)

    def start(self):
        self.running = True
        if IS_TTY:
            self.thread = threading.Thread(target=self._spin, daemon=True)
            self.thread.start()
        else:
            if not self.shown_static:
                sys.stderr.write(f"⏳ {self.message}\n")
                sys.stderr.flush()
                self.shown_static = True

    def update(self, message: str):
        self.message = message
        if not IS_TTY and not self.shown_static:
            sys.stderr.write(f"⏳ {message}\n")
            sys.stderr.flush()

    def stop(self, final_message: str = ""):
        self.running = False
        if self.thread:
            self.thread.join(timeout=0.2)
        if IS_TTY:
            sys.stderr.write("\r" + " " * 80 + "\r")
        if final_message:
            sys.stderr.write(f"✓ {final_message}\n")
        sys.stderr.flush()


class ProgressDisplay:
    """Progress display for news research phases."""

    def __init__(self, topic: str, show_banner: bool = True):
        self.topic = topic
        self.spinner: Optional[Spinner] = None
        self.start_time = time.time()

        if show_banner:
            self._show_banner()

    def _show_banner(self):
        if IS_TTY:
            sys.stderr.write(MINI_BANNER + "\n")
            sys.stderr.write(f"{Colors.DIM}Topic: {Colors.RESET}{Colors.BOLD}{self.topic}{Colors.RESET}\n\n")
        else:
            sys.stderr.write(f"/news30days · scanning: {self.topic}\n")
        sys.stderr.flush()

    def start_gnews(self):
        msg = random.choice(GNEWS_MESSAGES)
        self.spinner = Spinner(f"{Colors.GREEN}Google News{Colors.RESET} {msg}", Colors.GREEN)
        self.spinner.start()

    def end_gnews(self, count: int):
        if self.spinner:
            self.spinner.stop(f"{Colors.GREEN}Google News{Colors.RESET} Found {count} articles")

    def start_newsapi(self):
        msg = random.choice(NEWSAPI_MESSAGES)
        self.spinner = Spinner(f"{Colors.BLUE}NewsAPI{Colors.RESET} {msg}", Colors.BLUE)
        self.spinner.start()

    def end_newsapi(self, count: int):
        if self.spinner:
            self.spinner.stop(f"{Colors.BLUE}NewsAPI{Colors.RESET} Found {count} articles")

    def start_bing(self):
        msg = random.choice(BING_MESSAGES)
        self.spinner = Spinner(f"{Colors.CYAN}Bing News{Colors.RESET} {msg}", Colors.CYAN)
        self.spinner.start()

    def end_bing(self, count: int):
        if self.spinner:
            self.spinner.stop(f"{Colors.CYAN}Bing News{Colors.RESET} Found {count} articles")

    def start_websearch(self):
        msg = random.choice(WEBSEARCH_MESSAGES)
        self.spinner = Spinner(f"{Colors.YELLOW}WebSearch{Colors.RESET} {msg}", Colors.YELLOW)
        self.spinner.start()

    def end_websearch(self):
        if self.spinner:
            self.spinner.stop(f"{Colors.YELLOW}WebSearch{Colors.RESET} Claude will search news outlets")

    def start_processing(self):
        msg = random.choice(PROCESSING_MESSAGES)
        self.spinner = Spinner(f"{Colors.PURPLE}Processing{Colors.RESET} {msg}", Colors.PURPLE)
        self.spinner.start()

    def end_processing(self):
        if self.spinner:
            self.spinner.stop()

    def show_complete(self, gnews_count: int, newsapi_count: int = 0, bing_count: int = 0):
        elapsed = time.time() - self.start_time
        total = gnews_count + newsapi_count + bing_count
        if IS_TTY:
            sys.stderr.write(f"\n{Colors.GREEN}{Colors.BOLD}✓ News research complete{Colors.RESET} ")
            sys.stderr.write(f"{Colors.DIM}({elapsed:.1f}s){Colors.RESET}\n")
            parts = []
            if gnews_count:
                parts.append(f"{Colors.GREEN}Google News:{Colors.RESET} {gnews_count}")
            if newsapi_count:
                parts.append(f"{Colors.BLUE}NewsAPI:{Colors.RESET} {newsapi_count}")
            if bing_count:
                parts.append(f"{Colors.CYAN}Bing:{Colors.RESET} {bing_count}")
            sys.stderr.write(f"  {'  '.join(parts)}  ({total} total)\n\n")
        else:
            sys.stderr.write(f"✓ News research complete ({elapsed:.1f}s) - {total} articles\n")
        sys.stderr.flush()

    def show_free_complete(self, gnews_count: int):
        elapsed = time.time() - self.start_time
        if IS_TTY:
            sys.stderr.write(f"\n{Colors.GREEN}{Colors.BOLD}✓ News research complete{Colors.RESET} ")
            sys.stderr.write(f"{Colors.DIM}({elapsed:.1f}s){Colors.RESET}\n")
            sys.stderr.write(f"  {Colors.GREEN}Google News:{Colors.RESET} {gnews_count} articles + WebSearch\n\n")
        else:
            sys.stderr.write(f"✓ News research complete ({elapsed:.1f}s) - {gnews_count} articles + WebSearch\n")
        sys.stderr.flush()

    def show_error(self, message: str):
        sys.stderr.write(f"{Colors.RED}✗ Error:{Colors.RESET} {message}\n")
        sys.stderr.flush()

    def show_promo(self, missing: str = "both"):
        """Show promotional message for missing API keys."""
        if missing == "both":
            if IS_TTY:
                sys.stderr.write(PROMO_MESSAGE)
            else:
                sys.stderr.write(PROMO_MESSAGE_PLAIN)
        elif missing in PROMO_SINGLE_KEY:
            if IS_TTY:
                sys.stderr.write(PROMO_SINGLE_KEY[missing])
            else:
                sys.stderr.write(PROMO_SINGLE_KEY_PLAIN[missing])
        sys.stderr.flush()
