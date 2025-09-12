import re
from playwright.sync_api import sync_playwright, Page, expect

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    try:
        # Navigate directly to the login page
        page.goto("http://localhost:5173/login")

        # --- LOGIN STEPS ---
        email_input = page.get_by_placeholder("iltuoindirizzo@email.com")
        password_input = page.get_by_placeholder("••••••••")

        expect(email_input).to_be_visible(timeout=10000)

        email_input.fill("cutio.venezia@aol.com")
        password_input.fill("Asdfg12345")

        page.get_by_role("button", name="Accedi").click()

        # --- CHECK LOGIN RESULT ---
        try:
            # Wait for navigation to the dashboard with a 5-second timeout
            expect(page).to_have_url(re.compile(r"/$"), timeout=5000)
            print("Login successful. Proceeding to verification.")
        except Exception:
            # If navigation fails, check for a visible error message
            error_message_locator = page.locator('.error-message')
            if error_message_locator.is_visible():
                error_text = error_message_locator.inner_text()
                raise Exception(f"Login failed. UI Error: '{error_text}'")
            else:
                raise Exception("Login failed. The page did not redirect, and no error message was found.")

        # --- VERIFICATION STEPS ---
        expect(page.locator(".widget-card").first).to_be_visible(timeout=10000)

        pnl_widget_title = page.get_by_role("heading", name="Daily net cumulative P&L")
        pnl_widget_container = pnl_widget_title.locator("xpath=ancestor::div[contains(@class, 'widget-card')]")

        expect(pnl_widget_container).to_be_visible()

        pnl_widget_container.screenshot(path="jules-scratch/verification/widget_refactor.png")
        print("Screenshot captured successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")
        page.screenshot(path="jules-scratch/verification/error_screenshot.png")
    finally:
        browser.close()

with sync_playwright() as playwright:
    run(playwright)
