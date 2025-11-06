import re
from playwright.sync_api import sync_playwright, expect, Error as PlaywrightError

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    debug_file_path = "jules-scratch/verification/debug_output.txt"

    try:
        page.goto("http://localhost:5173/login")
        expect(page.get_by_role("heading", name="Bentornato")).to_be_visible()
        page.get_by_label("Email").fill("cutio.venezia@aol.com")
        page.get_by_label("Password").fill("Asdfg12345")
        page.get_by_role("button", name="Accedi").click()

        expect(page).to_have_url(re.compile(r"(/dashboard|/select-account)"), timeout=10000)

    except PlaywrightError as e:
        with open(debug_file_path, "w") as f:
            f.write("Login navigation failed. Checking for error messages on the page...\\n")

            error_locator = page.locator(".error-message")
            mfa_locator = page.get_by_label("Codice di Verifica")

            try:
                if error_locator.is_visible(timeout=1000):
                    error_text = error_locator.inner_text()
                    f.write(f"Error message found on page: '{error_text}'\\n")
                elif mfa_locator.is_visible(timeout=1000):
                    f.write("MFA prompt is visible. Login is likely waiting for an OTP code.\\n")
                else:
                    f.write("Could not find a specific error message or MFA prompt.\\n")
                    page.screenshot(path="jules-scratch/verification/debug_screenshot.png")
            except PlaywrightError:
                f.write("An error occurred while trying to find the debug info on the page.\\n")

        raise e

    # This part will not be reached if the login fails
    if "/select-account" in page.url:
        page.locator(".card-body").first.click()
        expect(page).to_have_url(re.compile(r"/dashboard"), timeout=10000)

    page.goto("http://localhost:5173/trades")
    expect(page.get_by_role("heading", name="Tutti i trade")).to_be_visible()
    page.get_by_role("button", name="Aggiungi Trade").click()

    modal_locator = page.locator(".modal-content")
    expect(modal_locator).to_be_visible()
    expect(modal_locator.get_by_placeholder("Seleziona i tag")).to_be_visible()
    page.screenshot(path="jules-scratch/verification/new-trade-form.png")

    browser.close()

with sync_playwright() as playwright:
    run(playwright)
