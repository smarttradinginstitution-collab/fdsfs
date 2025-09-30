import re
from playwright.sync_api import sync_playwright, Page, expect

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    try:
        # Navigate to the login page
        page.goto("http://localhost:5173/login")

        # Fill in the login form and submit
        page.get_by_placeholder("Enter your email").fill("test@example.com")
        page.get_by_placeholder("Enter your password").fill("Password123!")
        page.get_by_role("button", name="Login").click()

        # Wait for navigation to the dashboard
        expect(page).to_have_url(re.compile(r".*/dashboard$"))

        # Wait for an element that indicates the dashboard data has loaded initially
        # I'll use the "Recent Trades" table as a marker
        expect(page.get_by_text("Recent Trades")).to_be_visible(timeout=10000)

        # Now, reload the page
        page.reload()

        # After reload, wait again for the "Recent Trades" table to be visible.
        # This will confirm that the data fetching logic works on refresh.
        expect(page.get_by_text("Recent Trades")).to_be_visible(timeout=10000)

        # Take a screenshot for visual confirmation
        page.screenshot(path="jules-scratch/verification/verification.png")

        print("Verification script completed successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")
        # Take a screenshot even on failure for debugging
        page.screenshot(path="jules-scratch/verification/error.png")
    finally:
        browser.close()

with sync_playwright() as playwright:
    run(playwright)