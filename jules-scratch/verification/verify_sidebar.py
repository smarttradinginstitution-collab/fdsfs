import time
from playwright.sync_api import sync_playwright, Page, expect

def verify_sidebar_toggle(page: Page):
    """
    This test verifies that the sidebar toggle functionality works correctly
    on a mobile viewport.
    """
    # 1. Arrange: Go to the application's homepage and set mobile viewport.
    page.goto("http://localhost:5174/")

    # Wait for the app to load, a simple sleep is fine for this verification
    time.sleep(3)

    # 2. Act & Assert: Initial state
    # The hamburger button is inside the header
    hamburger_button = page.locator(".hamburger-menu")
    sidebar = page.locator("aside.sidebar")

    # On mobile, the sidebar should be hidden by default.
    # We check its transform property. translateX(-100%) is tricky to assert directly,
    # so we'll check that it's not visible in the main viewport area.
    # A robust way is to check the computed transform matrix.
    # A more pragmatic way for this test is to just take a screenshot and visually verify.
    page.screenshot(path="jules-scratch/verification/01_initial_state.png")
    print("Screenshot 1: Initial state captured.")

    # Let's check if the button is visible, which it should be on mobile
    expect(hamburger_button).to_be_visible()

    # 3. Act: Click the hamburger button to open the sidebar
    hamburger_button.click()
    # Wait for the transition to complete
    page.wait_for_timeout(500)

    # 4. Assert: Sidebar should be visible
    # The 'is-mobile-open' class should be applied to the sidebar
    expect(sidebar).to_have_class(r"sidebar is-mobile-open")
    page.screenshot(path="jules-scratch/verification/02_sidebar_opened.png")
    print("Screenshot 2: Opened state captured.")

    # 5. Act: Click the hamburger button again to close the sidebar
    hamburger_button.click()
    page.wait_for_timeout(500)

    # 6. Assert: Sidebar should be hidden again
    expect(sidebar).not_to_have_class(r"sidebar is-mobile-open")
    page.screenshot(path="jules-scratch/verification/03_sidebar_closed.png")
    print("Screenshot 3: Final closed state captured.")


# --- Boilerplate to run the test ---
def main():
    with sync_playwright() as p:
        # IMPORTANT: You must install playwright browsers first: `playwright install`
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        # Set a mobile viewport
        page.set_viewport_size({"width": 375, "height": 812}) # iPhone X

        try:
            verify_sidebar_toggle(page)
            print("\nVerification script completed successfully!")
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            page.screenshot(path="jules-scratch/verification/error.png")
        finally:
            browser.close()

if __name__ == "__main__":
    main()
