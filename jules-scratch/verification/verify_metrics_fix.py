import re
from playwright.sync_api import Page, expect
import time

def test_metrics_are_loaded(page: Page):
    """
    Test that after fixing the backend, the dashboard metrics load
    with real data and not zeros or N/A.
    """
    print("Starting verification script...")

    # 1. Arrange: Go to the login page and log in
    print("Navigating to login page...")
    page.goto("http://localhost:5173/login")
    print("Filling in credentials...")
    page.get_by_label("Email").fill("test@example.com")
    page.get_by_label("Password").fill("password")
    print("Clicking login button...")
    page.get_by_role("button", name="Log In").click()

    # 2. Act: Navigate to the dashboard and wait for it to load
    print("Waiting for dashboard to be visible...")
    # Use a specific, reliable element to wait for
    expect(page.get_by_text("Dashboard Overview")).to_be_visible(timeout=20000)
    print("Dashboard is visible. Waiting for network to be idle...")
    # Wait for all network requests to finish, which indicates data has loaded
    page.wait_for_load_state('networkidle', timeout=30000)
    print("Network is idle.")

    # Let's add a small extra delay just in case of slow rendering
    time.sleep(3)

    # Find the "Net P&L" widget. We will check its value.
    print("Looking for 'Net P&L' widget...")
    net_pnl_widget = page.locator(".stat-card-metric", has_text="Net P&L").first()
    expect(net_pnl_widget).to_be_visible()
    print("Found 'Net P&L' widget.")

    # Check that the value is not the default loading state "$0.00"
    pnl_text = net_pnl_widget.inner_text()
    print(f"Net P&L widget text: '{pnl_text}'")
    if pnl_text.strip() == "$0.00":
        print("Warning: Net P&L is $0.00. This might be correct or a loading issue. Waiting a bit more.")
        time.sleep(5) # Wait longer if we see the default value
        pnl_text = net_pnl_widget.inner_text()
        print(f"Net P&L widget text after extra wait: '{pnl_text}'")

    expect(net_pnl_widget).not_to_have_text("$0.00", timeout=5000)
    print("Assertion passed: Net P&L is not the default $0.00.")

    # Find the "Win Rate" widget
    print("Looking for 'Win Rate' widget...")
    win_rate_widget = page.locator(".stat-card-metric", has_text="Win Rate").first()
    expect(win_rate_widget).to_be_visible()
    print("Found 'Win Rate' widget.")

    win_rate_text = win_rate_widget.inner_text()
    print(f"Win Rate widget text: '{win_rate_text}'")
    expect(win_rate_widget).not_to_have_text("N/A", timeout=5000)
    print("Assertion passed: Win Rate is not the default 'N/A'.")

    # 3. Screenshot: Capture the state of the dashboard
    screenshot_path = "jules-scratch/verification/verification.png"
    print(f"Taking screenshot and saving to {screenshot_path}...")
    page.screenshot(path=screenshot_path)
    print("Screenshot saved successfully.")
    print("Verification script finished.")
