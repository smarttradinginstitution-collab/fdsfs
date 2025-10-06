import re
from playwright.sync_api import sync_playwright, Page, expect
import os

def verify_request_logs_page(page: Page):
    """
    This script verifies the request logs page for an admin user.
    1. Logs in as an admin.
    2. Navigates to the request logs page via the sidebar.
    3. Verifies the page content and takes a screenshot.
    """
    # 1. Navigate to the login page and log in.
    # Using placeholder credentials from environment variables if available,
    # otherwise, this step will likely fail.
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@example.com")
    admin_password = os.environ.get("ADMIN_PASSWORD", "password")

    page.goto("http://localhost:5173/login")

    # Fill in credentials using the correct Italian placeholders
    page.get_by_placeholder("iltuoindirizzo@email.com").fill(admin_email)
    page.get_by_placeholder("••••••••").fill(admin_password)

    # Click login button with the correct Italian text
    page.get_by_role("button", name="Accedi").click()

    # After login, the user might be redirected. We wait for a key element
    # on the dashboard to ensure login was successful.
    expect(page.get_by_role("heading", name="Dashboard")).to_be_visible(timeout=20000)

    # 2. Navigate to the request logs page.
    # The link is in the sidebar and should be visible to admins.
    monitoring_link = page.get_by_role("link", name="Monitoring")
    expect(monitoring_link).to_be_visible()
    monitoring_link.click()

    # 3. Verify the page content.
    # Check for the main heading of the request logs page.
    expect(page.get_by_role("heading", name="Monitoraggio Richieste API")).to_be_visible()

    # Check that the table is present.
    expect(page.get_by_role("table")).to_be_visible()

    # Check for the 'Svuota Log' (Clear Logs) button.
    expect(page.get_by_role("button", name=re.compile("Svuota Log", re.IGNORECASE))).to_be_visible()

    # 4. Take a screenshot for visual verification.
    page.screenshot(path="jules-scratch/verification/request-logs-page.png")

# Main execution block
if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            verify_request_logs_page(page)
            print("Verification script completed successfully.")
        except Exception as e:
            print(f"Verification script failed: {e}")
        finally:
            browser.close()