from playwright.sync_api import sync_playwright, Page, expect

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    try:
        # Navigate to login page
        page.goto("http://localhost:4173/login")

        # Fill in credentials and login
        page.get_by_label("Email").fill("cutio.venezia@aol.com")
        page.get_by_label("Password").fill("Asdfg12345")
        page.get_by_role("button", name="Accedi").click()

        # Wait for dashboard to load
        expect(page.get_by_role("heading", name="Dashboard")).to_be_visible()

        # Locate the Vantage Score widget
        widget_locator = page.locator(".complex-widgets-grid > div", has=page.get_by_role("heading", name="Zella Score", exact=True))

        # Take a screenshot of the widget
        widget_locator.screenshot(path="jules-scratch/verification/vantage_score_widget.png")

        # Click the header to open the popover
        header_locator = widget_locator.locator(".widget-header")
        header_locator.click()

        # Wait for the popover to be visible
        popover_locator = page.locator(".info-overlay-text")
        expect(popover_locator).to_be_visible()

        # Take a screenshot with the popover open
        widget_locator.screenshot(path="jules-scratch/verification/vantage_score_widget_popover.png")

    finally:
        # Clean up
        context.close()
        browser.close()

with sync_playwright() as playwright:
    run(playwright)
