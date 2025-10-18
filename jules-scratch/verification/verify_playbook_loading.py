
import asyncio
from playwright.async_api import async_playwright, expect

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Mock API calls
        await page.route("**/api/v1/auth/login", lambda route: route.fulfill(
            status=200,
            json={
                "access_token": "fake_token",
                "user": {"id": "123", "email": "test@example.com"}
            }
        ))
        await page.route("**/api/v1/general-accounts/me", lambda route: route.fulfill(
            status=200,
            json={"id": "ga1", "user_id": "123"}
        ))
        await page.route("**/api/v1/trading-accounts/", lambda route: route.fulfill(
            status=200,
            json=[{"id": "ta1", "label": "Test Account", "is_selected": True}]
        ))
        await page.route("**/api/v1/trades/performance/metrics/**", lambda route: route.fulfill(status=200, json={"stats": {}}))
        await page.route("**/api/v1/trades/calendar/data/**", lambda route: route.fulfill(status=200, json=[]))
        await page.route("**/api/v1/trades/processed-stats/**", lambda route: route.fulfill(status=200, json={}))
        await page.route("**/api/v1/trades/equity-curve/**", lambda route: route.fulfill(status=200, json={"labels": [], "data": []}))
        await page.route("**/api/v1/trades/vantage-score/**", lambda route: route.fulfill(status=200, json={}))

        # 1. Login
        await page.goto("http://localhost:5173/login")
        await expect(page.get_by_role("button", name="Accedi")).to_be_visible()
        await page.get_by_label("Email").fill("test@example.com")
        await page.get_by_label("Password").fill("password")
        await page.get_by_role("button", name="Accedi").click()

        # Navigate through account selection to the dashboard
        await expect(page.get_by_text("Test Account")).to_be_visible()
        await page.get_by_text("Test Account").click()
        await expect(page.locator('.stat-label:has-text("Net P&L")')).to_be_visible(timeout=10000)

        # 2. Verify Playbook Lazy Loading on Add Trade page
        await page.get_by_role("button", name="Nuovo Trade").click()
        await expect(page).to_have_url("http://localhost:5173/add-trade")

        # We expect the call to /api/v1/playbooks/ to happen AFTER clicking "Manual Entry"
        async with page.expect_request("**/api/v1/playbooks/") as request_info:
            await page.get_by_text("Manual Entry").click()

        request = await request_info.value
        assert request.method == 'GET', "The request to fetch playbooks was not a GET request."
        print("Successfully intercepted the GET request to /api/v1/playbooks/")

        # Fulfill the request now
        await request.fulfill(status=200, json=[{"id": "pb1", "title": "My Playbook"}])

        # Check if the playbook is visible in the form
        await expect(page.locator('option:has-text("My Playbook")')).to_be_visible()
        await page.screenshot(path="jules-scratch/verification/add_trade_playbook_loaded.png")
        print("Add Trade screenshot taken.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
