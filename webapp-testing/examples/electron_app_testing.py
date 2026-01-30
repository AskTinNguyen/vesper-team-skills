"""
Basic Electron App Testing via CDP

Connects to a running Electron app using Playwright's connect_over_cdp(),
discovers UI elements, takes a screenshot, and verifies window.electronAPI.

Prerequisites:
  - Electron running with --remote-debugging-port=9222
  - CDP_ENDPOINT env var set (e.g., via cdp_connect.py)

Usage:
  python scripts/cdp_connect.py -- python examples/electron_app_testing.py
"""

import os
from playwright.sync_api import sync_playwright

CDP_ENDPOINT = os.environ.get("CDP_ENDPOINT", "http://localhost:9222")


def main():
    with sync_playwright() as p:
        # Connect to existing Electron instance — do NOT launch a new browser
        browser = p.chromium.connect_over_cdp(CDP_ENDPOINT)

        # Get the existing Electron page (don't create a new one)
        context = browser.contexts[0]
        page = context.pages[0]

        print(f"Connected to: {page.title()}")
        print(f"URL: {page.url}")

        # Wait for the app to be fully loaded
        page.wait_for_load_state("networkidle")

        # Take a screenshot
        screenshot_path = "/tmp/electron_app.png"
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"Screenshot saved: {screenshot_path}")

        # Discover UI elements
        buttons = page.locator("button").all()
        print(f"\nButtons ({len(buttons)}):")
        for btn in buttons[:10]:  # Limit output
            text = btn.inner_text().strip()
            visible = btn.is_visible()
            if text:
                print(f"  - '{text}' (visible={visible})")

        inputs = page.locator("input").all()
        print(f"\nInputs ({len(inputs)}):")
        for inp in inputs[:10]:
            name = inp.get_attribute("name") or inp.get_attribute("id") or "unnamed"
            input_type = inp.get_attribute("type") or "text"
            print(f"  - {name} (type={input_type})")

        links = page.locator("a").all()
        print(f"\nLinks ({len(links)}):")
        for link in links[:10]:
            text = link.inner_text().strip()
            href = link.get_attribute("href") or ""
            if text:
                print(f"  - '{text}' → {href}")

        # Verify electronAPI is available (Electron preload bridge)
        has_api = page.evaluate("typeof window.electronAPI !== 'undefined'")
        print(f"\nwindow.electronAPI available: {has_api}")

        if has_api:
            api_keys = page.evaluate("Object.keys(window.electronAPI)")
            print(f"electronAPI methods: {api_keys[:20]}")

        # IMPORTANT: Do NOT call browser.close() — it kills the Electron app!
        print("\nDone. (Electron app left running)")


if __name__ == "__main__":
    main()
