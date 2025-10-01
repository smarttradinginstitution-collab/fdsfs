import re
from playwright.sync_api import sync_playwright, Page, expect

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    try:
        # 1. Arrange: Log in to the application
        page.goto("http://localhost:5173/login")
        page.get_by_placeholder("iltuoindirizzo@email.com").fill("test@example.com")
        page.get_by_placeholder("Password").fill("Password123!")
        page.get_by_role("button", name="Accedi").click()

        # Wait for successful login by checking for the dashboard URL
        expect(page).to_have_url(re.compile(r".*/dashboard$"), timeout=10000)

        # 2. Act: Navigate to the playbook detail page
        page.goto("http://localhost:5173/playbooks/1")

        # 3. Assert: Check that the main container for the new table view is visible
        rules_table_container = page.locator(".rules-table-container")
        expect(rules_table_container).to_be_visible()

        # 4. Assert: Check for the global header
        header = rules_table_container.locator(".table-header")
        expect(header).to_be_visible()
        expect(header).to_contain_text("Follow Rate")
        expect(header).to_contain_text("Net Profit / Loss")

        # 5. Assert: Check for at least one group heading
        entry_criteria_heading = page.get_by_role("heading", name="Entry Criteria")
        expect(entry_criteria_heading).to_be_visible()

        # 6. Screenshot: Capture the final result for visual verification
        page.screenshot(path="jules-scratch/verification/playbook-rules-rework.png")
        print("Verification script completed successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")
        page.screenshot(path="jules-scratch/verification/error.png")
    finally:
        browser.close()

with sync_playwright() as playwright:
    run(playwright)