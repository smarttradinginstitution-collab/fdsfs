from playwright.sync_api import sync_playwright, expect

def run_verification(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    try:
        # 1. Login
        page.goto("http://localhost:5173/login")
        page.get_by_placeholder("iltuoindirizzo@email.com").fill("test@test.com")
        page.get_by_placeholder("••••••••").fill("password")
        page.get_by_role("button", name="Accedi").click()

        # Wait for navigation to the dashboard after login
        expect(page).to_have_url("http://localhost:5173/dashboard", timeout=10000)
        print("Login successful.")

        # 2. Navigate to Playbooks page
        # Use a direct link to avoid potential race conditions with the sidebar loading
        page.goto("http://localhost:5173/playbooks")
        expect(page).to_have_url("http://localhost:5173/playbooks")
        print("Navigated to Playbooks page.")

        # 3. Click on the first playbook card to go to details
        # Wait for the playbook list to be visible before interacting with it
        playbook_list = page.locator(".playbook-list")
        expect(playbook_list).to_be_visible()

        # Click the first link within the list
        playbook_list.get_by_role("link").first.click()

        # Wait for navigation to a playbook detail page
        expect(page).to_have_url(lambda url: "/playbooks/" in url)
        print("Navigated to Playbook detail page.")

        # 4. Click on the "Executed Trades" tab
        executed_trades_tab = page.get_by_role("link", name="Executed Trades")
        executed_trades_tab.click()
        print("Clicked 'Executed Trades' tab.")

        # 5. Assert that the trades table is visible
        trades_table = page.locator("table.trades-table")
        expect(trades_table).to_be_visible(timeout=10000) # Increased timeout for data loading
        print("Trades table is visible, verification successful.")

        # 6. Take a screenshot for visual confirmation
        page.screenshot(path="jules-scratch/verification/executed-trades.png")
        print("Screenshot saved to jules-scratch/verification/executed-trades.png")

    except Exception as e:
        print(f"An error occurred during verification: {e}")
        page.screenshot(path="jules-scratch/verification/error.png")
        print("Error screenshot saved.")
    finally:
        browser.close()

with sync_playwright() as playwright:
    run_verification(playwright)