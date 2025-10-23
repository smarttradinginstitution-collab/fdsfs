from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    # Log in
    page.goto("http://localhost:5173/login")
    page.get_by_label("Email").fill("cutio.venezia@admin.com")
    page.get_by_label("Password").fill("string")
    page.get_by_role("button", name="Accedi").click()
    page.wait_for_url("http://localhost:5173/select-account")
    page.get_by_role("button", name="Entra").click()
    page.wait_for_url("http://localhost:5173/dashboard")

    # Go to the playbook edit page
    page.goto("http://localhost:5173/playbooks/a1dc628c-dd8a-435e-b424-574fe6c0a33b/edit")

    # Click the "Next" button to go to the rules step
    page.get_by_role("button", name="Next").click()

    # Wait for the rule groups to be visible
    page.wait_for_selector("text=Trading Playbook Rules")

    # Take a screenshot
    page.screenshot(path="jules-scratch/verification/verification.png")

    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
