from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    # Set a dummy token to simulate being logged in
    page.goto("http://localhost:5173/")
    page.evaluate("() => { localStorage.setItem('token', 'dummy-token-for-testing'); }")
    page.goto("http://localhost:5173/") # Reload to apply auth state

    # --- Desktop Screenshot ---
    page.set_viewport_size({"width": 1280, "height": 800})
    page.wait_for_selector('.stats-grid', timeout=10000) # Wait for stats to be visible
    page.screenshot(path="jules-scratch/verification/desktop_view.png")

    # --- Tablet Screenshot ---
    page.set_viewport_size({"width": 768, "height": 1024})
    page.wait_for_selector('.stats-grid', timeout=10000)
    page.screenshot(path="jules-scratch/verification/tablet_view.png")

    # --- Mobile Screenshot ---
    page.set_viewport_size({"width": 375, "height": 667})
    page.wait_for_selector('.stats-grid', timeout=10000)
    page.screenshot(path="jules-scratch/verification/mobile_view.png")

    # --- XL Desktop Screenshot ---
    page.set_viewport_size({"width": 1920, "height": 1080})
    page.wait_for_selector('.stats-grid', timeout=10000)
    page.screenshot(path="jules-scratch/verification/xl_view.png")

    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
