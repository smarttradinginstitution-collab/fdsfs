import re
from playwright.sync_api import sync_playwright, Page, expect

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080} # Set a large viewport for the test
    )
    page = context.new_page()

    try:
        # Navigate to the login page
        page.goto("http://localhost:5173/login")

        # Fill in the login form
        page.get_by_label("Email").fill("test@example.com")
        page.get_by_label("Password").fill("password")

        # Click the login button
        page.get_by_role("button", name="Login").click()

        # Wait for navigation to the dashboard
        expect(page).to_have_url(re.compile(r".*/dashboard$"))

        # Wait for the stats grid to be visible
        stats_grid = page.locator(".stats-grid")
        expect(stats_grid).to_be_visible()

        # Take a screenshot of the dashboard, focusing on the stats cards
        stats_grid.screenshot(path="jules-scratch/verification/verification.png")

        print("Screenshot saved to jules-scratch/verification/verification.png")

    except Exception as e:
        print(f"An error occurred: {e}")
        page.screenshot(path="jules-scratch/verification/error.png")

    finally:
        browser.close()

with sync_playwright() as playwright:
    run(playwright)
