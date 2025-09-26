import re
from playwright.sync_api import sync_playwright, expect

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()

    # Use an init script to set localStorage before any page scripts run
    context.add_init_script("""
        localStorage.setItem('token', 'fake-token');
        localStorage.setItem('user', JSON.stringify({id: 'user-123'}));
        localStorage.setItem('generalAccount', JSON.stringify({id: 'ga-456'}));
        localStorage.setItem('selectedTradingAccount', JSON.stringify({id: 'acc-1', label: 'Account Principale'}));
    """)

    page = context.new_page()
    page.set_viewport_size({"width": 1920, "height": 1080})
    page.set_default_timeout(15000)

    # --- Stateful Mock for API Responses ---
    accounts = [
        {"id": "acc-1", "label": "Account Principale"},
        {"id": "acc-2", "label": "Account di Prova"}
    ]

    try:
        # Mock API endpoints
        def handle_trading_accounts(route):
            nonlocal accounts
            if route.request.method == 'POST':
                new_account_data = route.request.post_data_json
                new_account = {"id": f"acc-{len(accounts) + 1}", "label": new_account_data.get("label")}
                accounts.append(new_account)
                route.fulfill(status=201, json=new_account)
            else: # GET
                route.fulfill(status=200, json=accounts)

        page.route("**/api/v1/trading-accounts/**", handle_trading_accounts)
        page.route("**/api/v1/trades/**", lambda route: route.fulfill(status=200, json=[]))
        page.route("**/api/v1/playbooks/**", lambda route: route.fulfill(status=200, json=[]))

        # --- Test Execution ---
        # ** THE FIX **: Wait for parallel network responses correctly.
        # Set up listeners for the responses we expect to be triggered on page load.
        accounts_response_waiter = page.expect_response("**/api/v1/trading-accounts/**")
        trades_response_waiter = page.expect_response("**/api/v1/trades/by-trading-account/acc-1")

        # Navigate to the page, which triggers the network calls.
        page.goto("http://localhost:5173/")

        # Wait for both responses to be received.
        accounts_response_waiter.value
        trades_response_waiter.value

        # 1. Verify initial state
        select_element = page.locator(".account-selector select")
        expect(select_element).to_have_value("acc-1")

        # 2. Test Account Creation
        create_button = page.get_by_test_id("create-account-btn")
        expect(create_button).to_be_visible()
        create_button.click()

        modal = page.locator(".base-modal")
        expect(modal).to_be_visible()

        modal.get_by_placeholder("Es. Conto Secondario").fill("Nuovo Conto Test")

        with page.expect_response("**/api/v1/trading-accounts/**") as response_info:
            modal.get_by_role("button", name="Crea Account").click()

        assert response_info.value.request.method == 'POST'

        expect(modal).not_to_be_visible()
        expect(select_element).to_have_value("acc-3")

        # 3. Test Account Selection (Reactivity)
        with page.expect_request("**/api/v1/trades/by-trading-account/acc-2"):
            select_element.select_option(value="acc-2")

        expect(select_element).to_have_value("acc-2")

        # 4. Take screenshot
        page.screenshot(path="jules-scratch/verification/dashboard-features.png")
        print("Dashboard features verification successful. Screenshot saved.")

    except Exception as e:
        print(f"Error during dashboard features verification: {e}")
        page.screenshot(path="jules-scratch/verification/dashboard-features-error.png")

    finally:
        browser.close()

with sync_playwright() as playwright:
    run(playwright)