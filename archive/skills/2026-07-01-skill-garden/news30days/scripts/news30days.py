#!/usr/bin/env python3
"""
news30days - Research a topic from the last 30 days in news outlets.

Usage:
    python3 news30days.py <topic> [options]

Options:
    --mock              Use fixtures instead of real API calls
    --emit=MODE         Output mode: compact|json|md|context|path (default: compact)
    --sources=MODE      Source selection: auto|gnews|newsapi|bing|all (default: auto)
    --quick             Faster research with fewer sources
    --deep              Comprehensive research with more sources
    --debug             Enable verbose debug logging
"""

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

# Add lib to path
SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR))

from lib import (
    cache,
    dates,
    dedupe,
    env,
    http,
    normalize,
    render,
    schema,
    score,
    ui,
    gnews,
    newsapi,
    bing_news,
    news_websearch,
)


def load_fixture(name: str) -> dict:
    """Load a fixture file."""
    fixture_path = SCRIPT_DIR.parent / "fixtures" / name
    if fixture_path.exists():
        with open(fixture_path) as f:
            return json.load(f)
    return {}


def _search_gnews(
    topic: str,
    from_date: str,
    to_date: str,
    depth: str,
    mock: bool,
) -> tuple:
    """Search Google News RSS (runs in thread)."""
    items = []
    error = None

    if mock:
        fixture = load_fixture("gnews_sample.json")
        items = fixture if isinstance(fixture, list) else fixture.get("items", [])
    else:
        try:
            items = gnews.search_gnews(topic, from_date, to_date, depth)
        except Exception as e:
            error = f"{type(e).__name__}: {e}"

    return items, error


def _search_newsapi(
    topic: str,
    api_key: str,
    from_date: str,
    to_date: str,
    depth: str,
    mock: bool,
) -> tuple:
    """Search NewsAPI.org (runs in thread)."""
    items = []
    error = None

    if mock:
        fixture = load_fixture("newsapi_sample.json")
        items = fixture if isinstance(fixture, list) else fixture.get("items", [])
    else:
        try:
            items = newsapi.search_newsapi(api_key, topic, from_date, to_date, depth=depth)
        except Exception as e:
            error = f"{type(e).__name__}: {e}"

    return items, error


def _search_bing(
    topic: str,
    api_key: str,
    from_date: str,
    depth: str,
    mock: bool,
) -> tuple:
    """Search Bing News (runs in thread)."""
    items = []
    error = None

    if mock:
        fixture = load_fixture("bing_news_sample.json")
        items = fixture if isinstance(fixture, list) else fixture.get("items", [])
    else:
        try:
            items = bing_news.search_bing_news(api_key, topic, from_date, depth=depth)
        except Exception as e:
            error = f"{type(e).__name__}: {e}"

    return items, error


def run_research(
    topic: str,
    sources: str,
    config: dict,
    from_date: str,
    to_date: str,
    depth: str = "default",
    mock: bool = False,
    progress: ui.ProgressDisplay = None,
) -> tuple:
    """Run the news research pipeline.

    Returns:
        Tuple of (gnews_items, newsapi_items, bing_items, web_needed,
                  gnews_error, newsapi_error, bing_error)
    """
    gnews_items = []
    newsapi_items = []
    bing_items = []
    gnews_error = None
    newsapi_error = None
    bing_error = None
    web_needed = True  # WebSearch always supplements news research

    # Determine which searches to run
    run_gnews = sources in ("free", "all", "newsapi", "bing")  # Always run Google News RSS
    run_newsapi = sources in ("all", "newsapi") and (mock or config.get("NEWSAPI_KEY"))
    run_bing = sources in ("all", "bing") and (mock or config.get("BING_NEWS_KEY"))

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {}

        if run_gnews:
            if progress:
                progress.start_gnews()
            futures["gnews"] = executor.submit(
                _search_gnews, topic, from_date, to_date, depth, mock
            )

        if run_newsapi:
            if progress:
                progress.start_newsapi()
            futures["newsapi"] = executor.submit(
                _search_newsapi, topic, config.get("NEWSAPI_KEY", ""),
                from_date, to_date, depth, mock
            )

        if run_bing:
            if progress:
                progress.start_bing()
            futures["bing"] = executor.submit(
                _search_bing, topic, config.get("BING_NEWS_KEY", ""),
                from_date, depth, mock
            )

        # Collect results
        if "gnews" in futures:
            try:
                gnews_items, gnews_error = futures["gnews"].result()
                if gnews_error and progress:
                    progress.show_error(f"Google News: {gnews_error}")
            except Exception as e:
                gnews_error = f"{type(e).__name__}: {e}"
                if progress:
                    progress.show_error(f"Google News: {e}")
            if progress:
                progress.end_gnews(len(gnews_items))

        if "newsapi" in futures:
            try:
                newsapi_items, newsapi_error = futures["newsapi"].result()
                if newsapi_error and progress:
                    progress.show_error(f"NewsAPI: {newsapi_error}")
            except Exception as e:
                newsapi_error = f"{type(e).__name__}: {e}"
                if progress:
                    progress.show_error(f"NewsAPI: {e}")
            if progress:
                progress.end_newsapi(len(newsapi_items))

        if "bing" in futures:
            try:
                bing_items, bing_error = futures["bing"].result()
                if bing_error and progress:
                    progress.show_error(f"Bing News: {bing_error}")
            except Exception as e:
                bing_error = f"{type(e).__name__}: {e}"
                if progress:
                    progress.show_error(f"Bing News: {e}")
            if progress:
                progress.end_bing(len(bing_items))

    return gnews_items, newsapi_items, bing_items, web_needed, gnews_error, newsapi_error, bing_error


def main():
    parser = argparse.ArgumentParser(
        description="Research a topic from the last 30 days in news outlets"
    )
    parser.add_argument("topic", nargs="?", help="Topic to research")
    parser.add_argument("--mock", action="store_true", help="Use fixtures")
    parser.add_argument(
        "--emit",
        choices=["compact", "json", "md", "context", "path"],
        default="compact",
        help="Output mode",
    )
    parser.add_argument(
        "--sources",
        choices=["auto", "gnews", "newsapi", "bing", "all"],
        default="auto",
        help="Source selection",
    )
    parser.add_argument("--quick", action="store_true", help="Faster research with fewer sources")
    parser.add_argument("--deep", action="store_true", help="Comprehensive research with more sources")
    parser.add_argument("--debug", action="store_true", help="Enable verbose debug logging")

    args = parser.parse_args()

    if args.debug:
        os.environ["NEWS30DAYS_DEBUG"] = "1"
        from lib import http as http_module
        http_module.DEBUG = True

    # Determine depth
    if args.quick and args.deep:
        print("Error: Cannot use both --quick and --deep", file=sys.stderr)
        sys.exit(1)
    elif args.quick:
        depth = "quick"
    elif args.deep:
        depth = "deep"
    else:
        depth = "default"

    if not args.topic:
        print("Error: Please provide a topic to research.", file=sys.stderr)
        print("Usage: python3 news30days.py <topic> [options]", file=sys.stderr)
        sys.exit(1)

    # Load config
    config = env.get_config()

    # Check available sources
    available = env.get_available_sources(config)

    # Mock mode can work without keys
    if args.mock:
        if args.sources == "auto":
            sources = "free"
        else:
            sources = args.sources
    else:
        sources, error = env.validate_sources(args.sources, available)
        if error:
            print(f"Note: {error}", file=sys.stderr)

    # Get date range
    from_date, to_date = dates.get_date_range(30)

    # Check missing keys for promo
    missing_keys = env.get_missing_keys(config)

    # Initialize progress display
    progress = ui.ProgressDisplay(args.topic, show_banner=True)

    # Show promo for missing keys
    if missing_keys != 'none':
        progress.show_promo(missing_keys)

    # Run research
    gnews_items, newsapi_items, bing_items, web_needed, gnews_error, newsapi_error, bing_error = run_research(
        args.topic, sources, config, from_date, to_date, depth, args.mock, progress,
    )

    # Processing phase
    progress.start_processing()

    # Normalize items
    normalized_gnews = normalize.normalize_gnews_items(gnews_items, from_date, to_date)
    normalized_newsapi = normalize.normalize_newsapi_items(newsapi_items, from_date, to_date)
    normalized_bing = normalize.normalize_bing_items(bing_items, from_date, to_date)

    # Merge all items
    all_items = normalized_gnews + normalized_newsapi + normalized_bing

    # Date filter
    filtered = normalize.filter_by_date_range(all_items, from_date, to_date)

    # Score items
    scored = score.score_news_items(filtered)

    # Sort items
    sorted_items = score.sort_items(scored)

    # Dedupe items
    deduped = dedupe.dedupe_news(sorted_items)

    progress.end_processing()

    # Create report
    report = schema.create_report(args.topic, from_date, to_date, sources)
    report.news = deduped
    report.gnews_count = len(gnews_items)
    report.newsapi_count = len(newsapi_items)
    report.bing_count = len(bing_items)
    report.gnews_error = gnews_error
    report.newsapi_error = newsapi_error
    report.bing_error = bing_error

    # Generate context snippet
    report.context_snippet_md = render.render_context_snippet(report)

    # Write outputs
    render.write_outputs(report)

    # Show completion
    if sources == "free":
        progress.show_free_complete(len(gnews_items))
    else:
        progress.show_complete(len(gnews_items), len(newsapi_items), len(bing_items))

    # Output result
    output_result(report, args.emit, web_needed, args.topic, from_date, to_date, missing_keys)


def output_result(
    report: schema.NewsReport,
    emit_mode: str,
    web_needed: bool = False,
    topic: str = "",
    from_date: str = "",
    to_date: str = "",
    missing_keys: str = "none",
):
    """Output the result based on emit mode."""
    if emit_mode == "compact":
        print(render.render_compact(report, missing_keys=missing_keys))
    elif emit_mode == "json":
        print(json.dumps(report.to_dict(), indent=2))
    elif emit_mode == "md":
        print(render.render_full_report(report))
    elif emit_mode == "context":
        print(report.context_snippet_md)
    elif emit_mode == "path":
        print(render.get_context_path())

    # Output WebSearch instructions if needed (only in compact/md mode)
    if web_needed and emit_mode in ("compact", "md"):
        instructions = news_websearch.get_websearch_instructions(topic, from_date, to_date)
        print(f"\n{'='*60}")
        print(instructions)
        print("="*60)


if __name__ == "__main__":
    main()
