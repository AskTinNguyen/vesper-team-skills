"""
Electron IPC Testing via CDP

Demonstrates how to test Electron IPC communication through the
window.electronAPI bridge using Playwright's connect_over_cdp().

Covers:
  - Listing available electronAPI methods
  - Calling async IPC methods
  - UI interactions that trigger IPC
  - Console message capture for debugging

Prerequisites:
  - Electron running with --remote-debugging-port=9222
  - CDP_ENDPOINT env var set (e.g., via cdp_connect.py)

Usage:
  python scripts/cdp_connect.py -- python examples/electron_ipc_testing.py
"""

import os
from playwright.sync_api import sync_playwright

CDP_ENDPOINT = os.environ.get("CDP_ENDPOINT", "http://localhost:9222")


def main():
    with sync_playwright() as p:
        # Connect to existing Electron instance
        browser = p.chromium.connect_over_cdp(CDP_ENDPOINT)
        context = browser.contexts[0]
        page = context.pages[0]

        print(f"Connected to: {page.title()}")
        page.wait_for_load_state("networkidle")

        # --- 1. Discover electronAPI methods ---
        has_api = page.evaluate("typeof window.electronAPI !== 'undefined'")
        if not has_api:
            print("ERROR: window.electronAPI not found.")
            print("Ensure the Electron preload script exposes electronAPI.")
            return

        api_keys = page.evaluate("Object.keys(window.electronAPI)")
        print(f"\nelectronAPI methods ({len(api_keys)}):")
        for key in sorted(api_keys):
            kind = page.evaluate(f"typeof window.electronAPI['{key}']")
            print(f"  - {key} ({kind})")

        # --- 2. Call an async IPC method ---
        # Example: calling a read-only method like getConfig
        # Adjust the method name to match your app's electronAPI
        print("\n--- IPC Call Example ---")
        try:
            # Wrap in try/catch to handle missing methods gracefully
            result = page.evaluate("""async () => {
                // Try common read-only methods; adjust for your app
                if (typeof window.electronAPI.getConfig === 'function') {
                    return { method: 'getConfig', result: await window.electronAPI.getConfig() };
                }
                if (typeof window.electronAPI.getVersion === 'function') {
                    return { method: 'getVersion', result: await window.electronAPI.getVersion() };
                }
                return { method: null, result: 'No known read-only method found' };
            }""")
            print(f"  Called: {result['method']}")
            print(f"  Result: {result['result']}")
        except Exception as e:
            print(f"  IPC call failed: {e}")

        # --- 3. Console message capture ---
        print("\n--- Console Capture ---")
        console_messages = []

        def on_console(msg):
            console_messages.append({"type": msg.type, "text": msg.text})

        page.on("console", on_console)

        # Trigger some UI interaction that might produce console output
        # For example, clicking a button (adjust selector for your app)
        buttons = page.locator("button").all()
        if buttons:
            first_visible = None
            for btn in buttons:
                if btn.is_visible():
                    first_visible = btn
                    break

            if first_visible:
                btn_text = first_visible.inner_text().strip()
                print(f"  Clicking button: '{btn_text}'")
                first_visible.click()
                # Wait briefly for any async effects
                page.wait_for_timeout(1000)
            else:
                print("  No visible buttons to click")
        else:
            print("  No buttons found on page")

        # Report captured console messages
        if console_messages:
            print(f"\n  Captured {len(console_messages)} console message(s):")
            for msg in console_messages[:20]:
                print(f"    [{msg['type']}] {msg['text'][:200]}")
        else:
            print("  No console messages captured")

        page.remove_listener("console", on_console)

        # --- 4. UI interaction triggering IPC ---
        print("\n--- UI → IPC Flow ---")
        # Take a before screenshot
        page.screenshot(path="/tmp/electron_ipc_before.png")
        print("  Before screenshot: /tmp/electron_ipc_before.png")

        # Example: Find and interact with an input field, then check state
        inputs = page.locator("input[type='text'], input:not([type])").all()
        if inputs:
            first_input = inputs[0]
            if first_input.is_visible():
                input_name = (
                    first_input.get_attribute("name")
                    or first_input.get_attribute("placeholder")
                    or "unnamed"
                )
                print(f"  Typing into input: '{input_name}'")
                first_input.fill("test-value")
                page.wait_for_timeout(500)

        # Take an after screenshot
        page.screenshot(path="/tmp/electron_ipc_after.png")
        print("  After screenshot: /tmp/electron_ipc_after.png")

        # IMPORTANT: Do NOT call browser.close() — it kills the Electron app!
        print("\nDone. (Electron app left running)")


if __name__ == "__main__":
    main()
