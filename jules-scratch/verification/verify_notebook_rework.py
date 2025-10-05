import re
from playwright.sync_api import sync_playwright, Page, expect

def login(page: Page):
    """Logs the user into the application."""
    page.goto("http://localhost:5175/login")
    page.get_by_placeholder("Enter your email").fill("cutio.venezia@aol.com")
    page.get_by_placeholder("Enter your password").fill("Asdfg12345")
    page.get_by_role("button", name="Login").click()
    # Wait for navigation to the dashboard after login
    expect(page).to_have_url(re.compile(r".*/dashboard$"))

def test_notebook_first_column_rework(page: Page):
    """
    This test verifies the stylistic rework of the first column of the Notebooks page.
    It checks the new layout, the 'Add Folder' functionality, and the 'Log Day' button.
    """
    # 1. Arrange: Login and navigate to the Notebooks page.
    login(page)
    page.get_by_role("link", name="Notebook").click()
    expect(page).to_have_url(re.compile(r".*/notebook$"))

    # 2. Assert: Check initial layout of the first column.
    # Expect the "Notebook" title to be visible.
    expect(page.get_by_role("heading", name="Notebook")).to_be_visible()
    # Expect the "Add folder" and "Log day" buttons to be visible.
    expect(page.get_by_role("button", name="Add folder")).to_be_visible()
    expect(page.get_by_role("button", name="Log day")).to_be_visible()
    # Expect the search input to be present.
    expect(page.get_by_placeholder("Search notes...")).to_be_visible()

    # 3. Act: Test the "Add Folder" functionality.
    page.get_by_role("button", name="Add folder").click()

    # Assert: Modal should be visible
    add_folder_modal = page.get_by_role("dialog")
    expect(add_folder_modal).to_be_visible()
    expect(add_folder_modal.get_by_role("heading", name="Add New Folder")).to_be_visible()

    # 4. Act: Fill in the form and create the folder.
    folder_name = "My Test Folder"
    add_folder_modal.get_by_label("Folder Name").fill(folder_name)
    # Click the third color option (a nice green)
    add_folder_modal.get_by_role("radio").nth(2).click()
    add_folder_modal.get_by_role("button", name="Save").click()

    # 5. Assert: Verify the new folder is in the list.
    folder_list = page.get_by_role("list")
    new_folder_item = folder_list.get_by_text(folder_name)
    expect(new_folder_item).to_be_visible()
    # Check for the note count badge
    expect(new_folder_item.locator("..").get_by_text("0")).to_be_visible()

    # 6. Screenshot: Capture the final state for visual verification.
    page.screenshot(path="jules-scratch/verification/notebook_rework_verification.png")

# Main execution block
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    test_notebook_first_column_rework(page)
    browser.close()