"""Terminal UI utilities for social30days skill."""

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


MINI_BANNER = f"""{Colors.PURPLE}{Colors.BOLD}/social30days{Colors.RESET} {Colors.DIM}· scanning social media...{Colors.RESET}"""

TIKTOK_MESSAGES = [
    "Checking TikTok Creative Center...",
    "Finding trending hashtags...",
    "Scanning viral content...",
    "Discovering trending sounds...",
]

TRENDS_MESSAGES = [
    "Checking Google Trends...",
    "Analyzing search interest...",
    "Finding related queries...",
    "Tracking trend momentum...",
]

WEBSEARCH_MESSAGES = [
    "Searching social platforms...",
    "Finding viral posts...",
    "Scanning Instagram and Facebook...",
]

CROWDTANGLE_MESSAGES = [
    "Querying CrowdTangle...",
    "Fetching FB/IG engagement data...",
    "Finding top-performing posts...",
]

PROCESSING_MESSAGES = [
    "Scoring by engagement...",
    "Ranking viral content...",
    "Finding patterns...",
    "Removing duplicates...",
]

PROMO_MESSAGE = f"""
{Colors.YELLOW}{Colors.BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.RESET}
{Colors.YELLOW}⚡ UNLOCK ENGAGEMENT METRICS{Colors.RESET}

{Colors.DIM}Using free sources (TikTok Creative + Google Trends + WebSearch).{Colors.RESET}
{Colors.DIM}Add CrowdTangle for FB/IG engagement data:{Colors.RESET}

  {Colors.BLUE}📘 CrowdTangle{Colors.RESET} - Real engagement metrics for Facebook/Instagram
     └─ Add CROWDTANGLE_TOKEN (Meta Content Library access)

{Colors.DIM}Setup:{Colors.RESET} Edit {Colors.BOLD}~/.config/social30days/.env{Colors.RESET}
{Colors.YELLOW}{Colors.BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.RESET}
"""

PROMO_MESSAGE_PLAIN = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ UNLOCK ENGAGEMENT METRICS

Using free sources (TikTok Creative + Google Trends + WebSearch).
Add CrowdTangle for FB/IG engagement data:

  📘 CrowdTangle - Real engagement metrics for Facebook/Instagram
     └─ Add CROWDTANGLE_TOKEN (Meta Content Library access)

Setup: Edit ~/.config/social30days/.env
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

SPINNER_FRAMES = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']


class Spinner:
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
            sys.stderr.write(f"/social30days · scanning: {self.topic}\n")
        sys.stderr.flush()

    def start_tiktok(self):
        msg = random.choice(TIKTOK_MESSAGES)
        self.spinner = Spinner(f"{Colors.PURPLE}TikTok{Colors.RESET} {msg}", Colors.PURPLE)
        self.spinner.start()

    def end_tiktok(self, count: int):
        if self.spinner:
            self.spinner.stop(f"{Colors.PURPLE}TikTok{Colors.RESET} Found {count} trends")

    def start_trends(self):
        msg = random.choice(TRENDS_MESSAGES)
        self.spinner = Spinner(f"{Colors.BLUE}Google Trends{Colors.RESET} {msg}", Colors.BLUE)
        self.spinner.start()

    def end_trends(self, count: int):
        if self.spinner:
            self.spinner.stop(f"{Colors.BLUE}Google Trends{Colors.RESET} Found {count} trends")

    def start_websearch(self):
        msg = random.choice(WEBSEARCH_MESSAGES)
        self.spinner = Spinner(f"{Colors.GREEN}WebSearch{Colors.RESET} {msg}", Colors.GREEN)
        self.spinner.start()

    def end_websearch(self):
        if self.spinner:
            self.spinner.stop(f"{Colors.GREEN}WebSearch{Colors.RESET} Claude will search social platforms")

    def start_crowdtangle(self):
        msg = random.choice(CROWDTANGLE_MESSAGES)
        self.spinner = Spinner(f"{Colors.CYAN}CrowdTangle{Colors.RESET} {msg}", Colors.CYAN)
        self.spinner.start()

    def end_crowdtangle(self, count: int):
        if self.spinner:
            self.spinner.stop(f"{Colors.CYAN}CrowdTangle{Colors.RESET} Found {count} posts")

    def start_processing(self):
        msg = random.choice(PROCESSING_MESSAGES)
        self.spinner = Spinner(f"{Colors.YELLOW}Processing{Colors.RESET} {msg}", Colors.YELLOW)
        self.spinner.start()

    def end_processing(self):
        if self.spinner:
            self.spinner.stop()

    def show_complete(self, tiktok_count: int = 0, trends_count: int = 0, crowdtangle_count: int = 0):
        elapsed = time.time() - self.start_time
        total = tiktok_count + trends_count + crowdtangle_count
        if IS_TTY:
            sys.stderr.write(f"\n{Colors.GREEN}{Colors.BOLD}✓ Social research complete{Colors.RESET} ")
            sys.stderr.write(f"{Colors.DIM}({elapsed:.1f}s){Colors.RESET}\n")
            parts = []
            if tiktok_count:
                parts.append(f"{Colors.PURPLE}TikTok:{Colors.RESET} {tiktok_count}")
            if trends_count:
                parts.append(f"{Colors.BLUE}Trends:{Colors.RESET} {trends_count}")
            if crowdtangle_count:
                parts.append(f"{Colors.CYAN}CrowdTangle:{Colors.RESET} {crowdtangle_count}")
            if parts:
                sys.stderr.write(f"  {'  '.join(parts)}  ({total} total + WebSearch)\n\n")
        else:
            sys.stderr.write(f"✓ Social research complete ({elapsed:.1f}s) - {total} items + WebSearch\n")
        sys.stderr.flush()

    def show_error(self, message: str):
        sys.stderr.write(f"{Colors.RED}✗ Error:{Colors.RESET} {message}\n")
        sys.stderr.flush()

    def show_promo(self, missing: str = "crowdtangle"):
        if IS_TTY:
            sys.stderr.write(PROMO_MESSAGE)
        else:
            sys.stderr.write(PROMO_MESSAGE_PLAIN)
        sys.stderr.flush()
