import json
from playwright.sync_api import sync_playwright, expect

def run_verification(playwright):
    """
    This script verifies the new layout of the KPI dashboard.
    It bypasses the auth guard by setting dummy data in localStorage.
    """
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    # Define the base URL and the target page
    base_url = "http://localhost:5176"
    trades_page_url = f"{base_url}/trades"

    # 1. Go to the base page first to set localStorage
    page.goto(base_url)

    # 2. Set localStorage items to bypass the navigation guard
    page.evaluate("""() => {
        localStorage.setItem('token', 'dummy-auth-token');
        localStorage.setItem('selectedTradingAccount', JSON.stringify({ id: '323aacbc-b72c-4129-a403-bb45d81e09b1' }));
    }""")

    # 3. Navigate to the trades page
    page.goto(trades_page_url)

    # 4. Wait for the dashboard to be visible, indicating the data has loaded
    # We target the main dashboard container.
    dashboard_locator = page.locator(".kpi-dashboard")
    expect(dashboard_locator).to_be_visible(timeout=15000) # Increased timeout for data fetching

    # 5. Take a screenshot of the entire dashboard to verify all card layouts
    screenshot_path = "jules-scratch/verification/kpi-dashboard-layout.png"
    page.screenshot(path=screenshot_path)

    print(f"Screenshot saved to {screenshot_path}")

    # Clean up
    context.close()
    browser.close()

if __name__ == "__main__":
    with sync_playwright() as playwright:
        run_verification(playwright)