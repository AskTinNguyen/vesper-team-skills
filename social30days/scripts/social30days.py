#!/usr/bin/env python3
"""
social30days - Research a topic from the last 30 days on social media.

Usage:
    python3 social30days.py <topic> [options]

Options:
    --mock              Use fixtures instead of real API calls
    --emit=MODE         Output mode: compact|json|md|context|path (default: compact)
    --sources=MODE      Source selection: auto|free|crowdtangle (default: auto)
    --quick             Faster research with fewer sources
    --deep              Comprehensive research with more sources
    --debug             Enable verbose debug logging
"""

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
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
    tiktok_creative,
    google_trends,
    social_websearch,
    crowdtangle,
)


def load_fixture(name: str) -> dict:
    """Load a fixture file."""
    fixture_path = SCRIPT_DIR.parent / "fixtures" / name
    if fixture_path.exists():
        with open(fixture_path) as f:
            return json.load(f)
    return {}


def _search_tiktok(topic: str, depth: str, mock: bool) -> tuple:
    """Search TikTok Creative Center (runs in thread)."""
    items = []
    error = None

    if mock:
        fixture = load_fixture("tiktok_sample.json")
        items = fixture if isinstance(fixture, list) else fixture.get("items", [])
    else:
        try:
            items = tiktok_creative.search_tiktok_trends(topic, depth)
        except Exception as e:
            error = f"{type(e).__name__}: {e}"

    return items, error


def _search_google_trends(topic: str, depth: str, mock: bool) -> tuple:
    """Search Google Trends (runs in thread)."""
    items = []
    error = None

    if mock:
        fixture = load_fixture("google_trends_sample.json")
        items = fixture if isinstance(fixture, list) else fixture.get("items", [])
    else:
        try:
            items = google_trends.search_google_trends(topic, depth)
        except Exception as e:
            error = f"{type(e).__name__}: {e}"

    return items, error


def _search_crowdtangle(topic: str, token: str, from_date: str, to_date: str, depth: str, mock: bool) -> tuple:
    """Search CrowdTangle (runs in thread)."""
    items = []
    error = None

    if mock:
        fixture = load_fixture("crowdtangle_sample.json")
        items = fixture if isinstance(fixture, list) else fixture.get("items", [])
    else:
        try:
            items = crowdtangle.search_crowdtangle(token, topic, from_date, to_date, depth=depth)
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
    """Run the social media research pipeline.

    Returns:
        Tuple of (tiktok_items, trends_items, crowdtangle_items, web_needed,
                  tiktok_error, trends_error, crowdtangle_error)
    """
    tiktok_items = []
    trends_items = []
    ct_items = []
    tiktok_error = None
    trends_error = None
    ct_error = None
    web_needed = True  # WebSearch always supplements

    run_tiktok = True  # Always free
    run_trends = True  # Always free
    run_ct = sources == 'all' and (mock or config.get("CROWDTANGLE_TOKEN"))

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {}

        if run_tiktok:
            if progress:
                progress.start_tiktok()
            futures["tiktok"] = executor.submit(_search_tiktok, topic, depth, mock)

        if run_trends:
            if progress:
                progress.start_trends()
            futures["trends"] = executor.submit(_search_google_trends, topic, depth, mock)

        if run_ct:
            if progress:
                progress.start_crowdtangle()
            futures["crowdtangle"] = executor.submit(
                _search_crowdtangle, topic, config.get("CROWDTANGLE_TOKEN", ""),
                from_date, to_date, depth, mock
            )

        # Collect results
        if "tiktok" in futures:
            try:
                tiktok_items, tiktok_error = futures["tiktok"].result()
                if tiktok_error and progress:
                    progress.show_error(f"TikTok: {tiktok_error}")
            except Exception as e:
                tiktok_error = f"{type(e).__name__}: {e}"
                if progress:
                    progress.show_error(f"TikTok: {e}")
            if progress:
                progress.end_tiktok(len(tiktok_items))

        if "trends" in futures:
            try:
                trends_items, trends_error = futures["trends"].result()
                if trends_error and progress:
                    progress.show_error(f"Google Trends: {trends_error}")
            except Exception as e:
                trends_error = f"{type(e).__name__}: {e}"
                if progress:
                    progress.show_error(f"Google Trends: {e}")
            if progress:
                progress.end_trends(len(trends_items))

        if "crowdtangle" in futures:
            try:
                ct_items, ct_error = futures["crowdtangle"].result()
                if ct_error and progress:
                    progress.show_error(f"CrowdTangle: {ct_error}")
            except Exception as e:
                ct_error = f"{type(e).__name__}: {e}"
                if progress:
                    progress.show_error(f"CrowdTangle: {e}")
            if progress:
                progress.end_crowdtangle(len(ct_items))

    return tiktok_items, trends_items, ct_items, web_needed, tiktok_error, trends_error, ct_error


def main():
    parser = argparse.ArgumentParser(
        description="Research a topic from the last 30 days on social media"
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
        choices=["auto", "free", "crowdtangle"],
        default="auto",
        help="Source selection",
    )
    parser.add_argument("--quick", action="store_true", help="Faster research")
    parser.add_argument("--deep", action="store_true", help="Comprehensive research")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    if args.debug:
        os.environ["SOCIAL30DAYS_DEBUG"] = "1"
        from lib import http as http_module
        http_module.DEBUG = True

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
        print("Usage: python3 social30days.py <topic> [options]", file=sys.stderr)
        sys.exit(1)

    config = env.get_config()
    available = env.get_available_sources(config)

    if args.mock:
        sources = "free" if args.sources == "auto" else args.sources
    else:
        sources, error = env.validate_sources(args.sources, available)
        if error:
            print(f"Note: {error}", file=sys.stderr)

    from_date, to_date = dates.get_date_range(30)
    missing_keys = env.get_missing_keys(config)

    progress = ui.ProgressDisplay(args.topic, show_banner=True)

    if missing_keys != 'none':
        progress.show_promo(missing_keys)

    # Run research
    tiktok_items, trends_items, ct_items, web_needed, tiktok_error, trends_error, ct_error = run_research(
        args.topic, sources, config, from_date, to_date, depth, args.mock, progress,
    )

    # Processing
    progress.start_processing()

    # Normalize social items (CrowdTangle posts)
    normalized_social = normalize.normalize_social_items(ct_items, from_date, to_date)

    # Normalize trend items (TikTok + Google Trends)
    all_trend_raw = tiktok_items + trends_items
    normalized_trends = normalize.normalize_trend_items(all_trend_raw)

    # Date filter social items
    filtered_social = normalize.filter_by_date_range(normalized_social, from_date, to_date)

    # Score
    scored_social = score.score_social_items(filtered_social)
    scored_trends = score.score_trend_items(normalized_trends)

    # Sort
    sorted_social = score.sort_social_items(scored_social)
    sorted_trends = score.sort_trend_items(scored_trends)

    # Dedupe
    deduped_social = dedupe.dedupe_social(sorted_social)
    deduped_trends = dedupe.dedupe_trends(sorted_trends)

    progress.end_processing()

    # Create report
    report = schema.create_report(args.topic, from_date, to_date, sources)
    report.social = deduped_social
    report.trends = deduped_trends
    report.tiktok_count = len(tiktok_items)
    report.google_trends_count = len(trends_items)
    report.crowdtangle_count = len(ct_items)
    report.tiktok_error = tiktok_error
    report.google_trends_error = trends_error
    report.crowdtangle_error = ct_error

    report.context_snippet_md = render.render_context_snippet(report)
    render.write_outputs(report)

    progress.show_complete(len(tiktok_items), len(trends_items), len(ct_items))

    # Output
    output_result(report, args.emit, web_needed, args.topic, from_date, to_date, missing_keys)


def output_result(
    report: schema.SocialReport,
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
        instructions = social_websearch.get_websearch_instructions(topic, from_date, to_date)
        print(f"\n{'='*60}")
        print(instructions)
        print("="*60)


if __name__ == "__main__":
    main()
