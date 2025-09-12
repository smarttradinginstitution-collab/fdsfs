import re
from playwright.sync_api import sync_playwright, Page, expect

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    try:
        # Navigate and log in
        page.goto("http://localhost:5173/login")
        email_input = page.get_by_placeholder("iltuoindirizzo@email.com")
        password_input = page.get_by_placeholder("••••••••")
        expect(email_input).to_be_visible(timeout=10000)
        email_input.fill("cutio.venezia@aol.com")
        password_input.fill("Asdfg12345")
        page.get_by_role("button", name="Accedi").click()

        # Wait for navigation to the dashboard
        expect(page).to_have_url(re.compile(r"/$"), timeout=10000)

        # --- VERIFICATION ---
        # Locate the RR Distribution widget
        rr_widget_title = page.get_by_role("heading", name="RR Distribution")
        expect(rr_widget_title).to_be_visible(timeout=10000)

        rr_widget_container = rr_widget_title.locator("xpath=ancestor::div[contains(@class, 'widget-card')]")

        expect(rr_widget_container).to_be_visible()

        # Take a screenshot
        rr_widget_container.screenshot(path="jules-scratch/verification/rr_distribution_widget.png")
        print("Screenshot of RR Distribution widget captured successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")
        page.screenshot(path="jules-scratch/verification/error_screenshot.png")
    finally:
        browser.close()

with sync_playwright() as playwright:
    run(playwright)
