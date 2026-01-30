#!/usr/bin/env python3
"""
Connect to a running Electron app via Chrome DevTools Protocol (CDP).

This script discovers the main Electron renderer page, sets environment
variables (CDP_ENDPOINT, CDP_PORT), and optionally runs a child command.

Usage:
    # Show help
    python scripts/cdp_connect.py --help

    # Validate CDP is reachable and list targets
    python scripts/cdp_connect.py --validate-only

    # Run a test script with CDP_ENDPOINT set
    python scripts/cdp_connect.py -- python your_test.py

    # Custom port and timeout
    python scripts/cdp_connect.py --port 9223 --timeout 15 -- python your_test.py
"""

import subprocess
import json
import time
import sys
import os
import argparse
import urllib.request
import urllib.error


def poll_cdp(port, timeout):
    """Wait for CDP to be reachable and return the targets list."""
    url = f"http://localhost:{port}/json"
    start = time.time()
    last_error = None
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(url, timeout=2) as resp:
                return json.loads(resp.read().decode())
        except (urllib.error.URLError, ConnectionRefusedError, OSError) as e:
            last_error = e
            time.sleep(0.5)
    raise RuntimeError(
        f"CDP not reachable on port {port} after {timeout}s: {last_error}"
    )


def find_main_page(targets):
    """Find the main Electron renderer page, filtering out DevTools."""
    for t in targets:
        if t.get("type") != "page":
            continue
        title = t.get("title", "")
        url = t.get("url", "")
        if "DevTools" in title or "devtools://" in url:
            continue
        return t
    return None


def print_targets(targets):
    """Print all CDP targets in a readable format."""
    for t in targets:
        kind = t.get("type", "unknown")
        title = t.get("title", "Untitled")
        url = t.get("url", "N/A")
        print(f"  [{kind}] {title}")
        print(f"          URL: {url}")


def main():
    parser = argparse.ArgumentParser(
        description="Connect to Electron via CDP and run a command"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=9222,
        help="CDP remote debugging port (default: 9222)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Seconds to wait for CDP availability (default: 10)",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Check CDP is reachable, list targets, then exit",
    )
    parser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help="Command to run with CDP_ENDPOINT set",
    )

    args = parser.parse_args()

    # Remove '--' separator if present
    command = args.command
    if command and command[0] == "--":
        command = command[1:]

    # --- Poll for CDP ---
    print(f"Connecting to CDP on port {args.port}...")
    try:
        targets = poll_cdp(args.port, args.timeout)
    except RuntimeError as e:
        print(f"Error: {e}")
        print()
        print("Make sure Electron is running with --remote-debugging-port=9222")
        print("Example: electron . --remote-debugging-port=9222")
        sys.exit(1)

    print(f"Found {len(targets)} CDP target(s):")
    print_targets(targets)
    print()

    # --- Find main page ---
    page = find_main_page(targets)
    if page:
        ws_url = page.get("webSocketDebuggerUrl", "")
        print(f"Main page: {page.get('title', 'Untitled')}")
        print(f"  WebSocket: {ws_url}")
    else:
        print("Warning: No main Electron page found (all targets may be DevTools)")
        ws_url = ""

    # --- Validate-only mode ---
    if args.validate_only:
        print()
        if page:
            print("CDP is reachable and main page found. Ready for testing.")
        else:
            print("CDP is reachable but no main page detected.")
        sys.exit(0 if page else 1)

    # --- Run child command ---
    if not command:
        print()
        print("No command specified. Set these in your environment to use manually:")
        print(f"  export CDP_ENDPOINT=http://localhost:{args.port}")
        print(f"  export CDP_PORT={args.port}")
        sys.exit(0)

    endpoint = f"http://localhost:{args.port}"
    env = os.environ.copy()
    env["CDP_ENDPOINT"] = endpoint
    env["CDP_PORT"] = str(args.port)

    print()
    print(f"Running: {' '.join(command)}")
    print(f"  CDP_ENDPOINT={endpoint}")
    print(f"  CDP_PORT={args.port}")
    print()

    result = subprocess.run(command, env=env)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
