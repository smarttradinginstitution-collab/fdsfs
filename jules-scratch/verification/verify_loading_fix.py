from playwright.sync_api import sync_playwright, Page, expect

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    # Go to login page
    page.goto("http://localhost:5173/login")

    # Perform login
    page.get_by_label("Email").fill("user2@example.com")
    page.get_by_label("Password").fill("string")
    page.get_by_role("button", name="Accedi").click()

    # Wait for navigation to the select account page
    expect(page.get_by_role("heading", name="Seleziona un Account di Trading")).to_be_visible()

    # Click the first account in the list to proceed
    page.locator(".account-item").first.click()

    # Now, wait for navigation to the main app page (trades view)
    # The table should be visible
    expect(page.get_by_role("table")).to_be_visible()

    # Click the first trade in the table to go to the detail page
    # We target the first row in the table body
    first_trade_row = page.locator("tbody tr").first
    first_trade_row.click()

    # Wait for the report detail view to load completely
    # We expect the main container to be visible, which replaces the loading message.
    # This is the core of the verification: if the loading logic is correct,
    # this container will appear without the "Trade not found" flicker.
    report_container = page.locator(".report-container")
    expect(report_container).to_be_visible(timeout=10000) # Increased timeout for slow data loading

    # Take a screenshot to visually verify the fix
    page.screenshot(path="jules-scratch/verification/verification.png")

    # Clean up
    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)