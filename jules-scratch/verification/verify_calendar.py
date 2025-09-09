import re
from playwright.sync_api import sync_playwright, Page, expect

def run_verification(page: Page):
    """
    This script logs in, navigates to the dashboard, and takes a screenshot
    of the calendar to verify that the date initialization is correct.
    """
    # 1. Go to the app's root URL.
    page.goto("http://localhost:5173/")
    page.wait_for_load_state("networkidle")

    # 2. Check if we need to log in.
    if "/login" in page.url:
        print("Redirected to login page. Performing login...")
        # Use placeholder text to locate the fields as the labels are not
        # programmatically linked to the inputs.
        page.get_by_placeholder("iltuoindirizzo@email.com").fill("cutio.venezia@aol.com")
        page.get_by_placeholder("••••••••").fill("Asdfg12345")
        page.get_by_role("button", name="Accedi").click()
    else:
        print("Already logged in. Proceeding to dashboard verification.")

    # 3. Assert: Wait for the dashboard to load and verify the calendar is visible.
    print("Waiting for calendar card to be visible...")
    calendar_card = page.locator(".calendar-card")
    expect(calendar_card).to_be_visible(timeout=15000)

    print("Waiting for calendar cells to be populated...")
    first_day_cell = page.locator(".day-cell:not(.placeholder)").first
    expect(first_day_cell).to_be_visible()
    print("Calendar is visible and populated.")

    # 4. Screenshot: Capture the final result for visual verification.
    print("Taking screenshot...")
    page.screenshot(path="jules-scratch/verification/calendar_verification.png")
    print("Screenshot saved to jules-scratch/verification/calendar_verification.png")

# Boilerplate to run the verification
if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        run_verification(page)
        browser.close()
