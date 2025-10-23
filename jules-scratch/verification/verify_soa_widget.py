from playwright.sync_api import sync_playwright, expect

def run(playwright):
    browser = playwright.chromium.launch()
    page = browser.new_page()
    page.goto("http://localhost:5173/")

    # --- Login Sequence ---
    page.get_by_label("Email").fill("test@example.com")
    page.get_by_label("Password").fill("password")
    page.get_by_role("button", name="Login").click()

    # --- Verification Sequence ---
    soa_widget_title = page.get_by_text("Sintesi Predittiva SOA")
    expect(soa_widget_title).to_be_visible(timeout=30000)

    widget_container = page.locator("div.base-widget", has_text="Sintesi Predittiva SOA")
    expect(widget_container).to_be_visible()

    page.screenshot(path="jules-scratch/verification/soa_widget.png")
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
