import re
import json
from playwright.sync_api import sync_playwright, Page, expect

def verify_connections_load(page: Page):
    """
    This script verifies that the Broker Connections page loads correctly,
    bypassing login by setting dummy auth data in localStorage.
    """
    try:
        # 1. Arrange: Go to the base URL to have a page context
        page.goto("http://localhost:5175/")

        # 2. Act: Inject auth data into localStorage to simulate a logged-in user
        user_id = "3f7dbd4e-f0f0-42a4-8fe4-4ddec85d5a7e"
        user_data = {
            "id": user_id,
            "profile": { "has_snaptrade_user_secret": True }
        }

        page.evaluate("""(data) => {
            localStorage.setItem('token', 'dummy-test-token');
            localStorage.setItem('user', JSON.stringify(data));
        }""", user_data)

        # 3. Act: Navigate to the connections page
        page.goto("http://localhost:5175/connections")

        # 4. Assert: Check if the navigation was successful
        expect(page).to_have_url("http://localhost:5175/connections", timeout=5000)

        # 5. Assert: Wait for the table and its content to be visible
        connections_table = page.get_by_role("table")
        expect(connections_table).to_be_visible(timeout=10000)
        expect(connections_table.get_by_text("Interactive Brokers")).to_be_visible()
        expect(connections_table.get_by_text("Alpaca Paper")).to_be_visible()

        # 6. Success Screenshot
        page.screenshot(path="jules-scratch/verification/verification.png")

    except Exception as e:
        # On failure, take a debug screenshot to see what the page looks like
        page.screenshot(path="jules-scratch/verification/verification-error.png")
        raise e

# Boilerplate to run the verification
if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        verify_connections_load(page)
        browser.close()
