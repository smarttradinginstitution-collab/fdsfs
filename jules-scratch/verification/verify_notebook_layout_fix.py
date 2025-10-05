import re
from playwright.sync_api import sync_playwright, Page, expect

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    try:
        # 1. Log in
        page.goto("http://localhost:5173/login")
        page.get_by_label("Email").fill("cutio.venezia@aol.com")
        page.get_by_label("Password").fill("Asdfg12345")
        page.get_by_role("button", name="Log in").click()

        # Wait for navigation to the dashboard after login
        expect(page).to_have_url(re.compile(".*/dashboard.*"), timeout=15000)

        # 2. Navigate to the Notebook page
        page.get_by_role("link", name="Notebook").click()
        expect(page).to_have_url(re.compile(".*notebook.*"), timeout=10000)

        # 3. Verify the three-column layout is visible
        # Wait for a key element in each column to ensure they have rendered
        expect(page.get_by_text("Add Folder")).to_be_visible(timeout=10000) # From FolderList
        expect(page.get_by_text("Log Day")).to_be_visible(timeout=10000) # From NoteList
        expect(page.get_by_text("Select a note to view or edit it.")).to_be_visible(timeout=10000) # From Editor placeholder

        # Take a screenshot
        page.screenshot(path="/app/jules-scratch/verification/notebook_layout_fixed.png")
        print("Screenshot taken successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")
        page.screenshot(path="/app/jules-scratch/verification/error.png")

    finally:
        browser.close()

with sync_playwright() as playwright:
    run(playwright)