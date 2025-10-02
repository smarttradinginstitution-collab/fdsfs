import re
from playwright.sync_api import sync_playwright, expect

def run(playwright):
    # This is a hardcoded trade ID that is known to exist in the test database.
    trade_id = "a1b2c3d4-e5f6-7890-1234-567890abcdef"

    # CORRECTED URL: Using /report/ (singular) instead of /reports/
    url = f"http://localhost:5173/report/{trade_id}"

    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    try:
        print(f"Navigating to {url}...")
        # Use networkidle to wait for network requests to finish, which is more reliable
        page.goto(url, wait_until="networkidle")

        print("Waiting for trade data to load...")

        # Wait for the asset name in the header. This is a good sign the page is loading.
        asset_name_locator = page.locator(".asset-name")
        expect(asset_name_locator).to_have_text("XAUUSD", timeout=10000)

        # Wait for the Net P&L value to appear. This confirms data binding.
        # This locator is more specific and robust.
        net_pnl_locator = page.locator(".stat-item.large-value .stat-value")
        expect(net_pnl_locator).to_be_visible()
        # Check that it contains a currency symbol
        expect(net_pnl_locator).to_contain_text("$")

        print("Data loaded. Taking screenshot...")

        screenshot_path = "jules-scratch/verification/report-page-rework.png"
        page.screenshot(path=screenshot_path, full_page=True)

        print(f"Screenshot saved to {screenshot_path}")

    except Exception as e:
        print(f"An error occurred: {e}")
        page.screenshot(path="jules-scratch/verification/error_screenshot.png", full_page=True)
    finally:
        browser.close()

with sync_playwright() as playwright:
    run(playwright)