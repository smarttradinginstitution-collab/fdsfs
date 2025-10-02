from playwright.sync_api import Page, expect

def test_trades_table_rework(page: Page):
    """
    This test verifies that the reworked trades table is displayed correctly.
    It logs in, navigates to the trades page, and captures a screenshot.
    """
    # 1. Arrange: Go to the login page.
    page.goto("http://localhost:5173/login")

    # 2. Act: Log in.
    # Using common development credentials.
    page.get_by_label("Email").fill("admin@test.com")
    page.get_by_label("Password").fill("password")
    page.get_by_role("button", name="Login").click()

    # 3. Act: Navigate to the trades page.
    # The app should redirect to the dashboard after login, then we go to trades.
    expect(page).to_have_url("http://localhost:5173/", timeout=10000)
    page.goto("http://localhost:5173/trades")

    # 4. Assert: Check for the new table structure.
    # We'll look for the "Bulk Actions" button and the table header.
    expect(page.get_by_role("button", name="Bulk Actions")).to_be_visible()
    expect(page.get_by_role("heading", name="Trade Log")).to_be_visible()

    # Wait for the table to be populated
    # We can wait for a specific cell's text to appear
    expect(page.locator("table >> tbody >> tr").first).to_be_visible(timeout=15000)


    # 5. Screenshot: Capture the final result for visual verification.
    page.screenshot(path="jules-scratch/verification/trades-table.png")