
import asyncio
import uuid
from playwright.async_api import async_playwright, expect

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Event to signal interception
        folders_request_intercepted = asyncio.Event()

        # Mock API calls
        await page.route("**/api/v1/auth/login", lambda route: route.fulfill(
            status=200,
            json={"access_token": "fake_token", "user": {"id": "123"}}
        ))
        await page.route("**/api/v1/general-accounts/me", lambda route: route.fulfill(
            status=200,
            json={"id": "ga1"}
        ))
        await page.route("**/api/v1/trading-accounts/", lambda route: route.fulfill(
            status=200,
            json=[{"id": "ta1", "label": "Test Account", "is_selected": True}]
        ))

        # Mock the trade detail call
        trade_id = str(uuid.uuid4())
        await page.route(f"**/api/v1/trades/{trade_id}", lambda route: route.fulfill(
            status=200,
            json={"id": trade_id, "symbol_snapshot": "TEST", "entry_timestamp": "2023-10-29T10:00:00Z"}
        ))
        await page.route(f"**/api/v1/trades/{trade_id}/images", lambda route: route.fulfill(status=200, json=[]))

        # Mock the note call to return 404, simulating no note exists yet
        await page.route(f"**/api/v1/notebook/notes/by_trade/{trade_id}", lambda route: route.fulfill(
            status=404,
            json={"detail": "Note not found"}
        ))

        # Intercept the folders call
        async def handle_folders_route(route):
            print("Intercepted notebook folders request.")
            await route.fulfill(
                status=200,
                json=[{"id": "folder1", "name": "Trade Notes", "system_folder_identifier": "TRADE_NOTES"}]
            )
            folders_request_intercepted.set()

        await page.route("**/api/v1/notebook/folders", handle_folders_route)

        # 1. Login & Navigate
        await page.goto("http://localhost:5173/login")
        await page.get_by_label("Email").fill("test@example.com")
        await page.get_by_label("Password").fill("password")
        await page.get_by_role("button", name="Accedi").click()
        await expect(page.get_by_text("Test Account")).to_be_visible()
        await page.get_by_text("Test Account").click()
        await expect(page.locator('.stat-label:has-text("Net P&L")')).to_be_visible(timeout=10000)

        # 2. Go to the report page and verify folders are fetched
        await page.goto(f"http://localhost:5173/report/{trade_id}")

        # Wait for the interception to happen
        await folders_request_intercepted.wait()
        print("Folders request fulfilled.")

        # 3. Verify the "Create Note" button is visible
        await expect(page.get_by_role("button", name="Create Note for this Trade")).to_be_visible(timeout=10000)

        await page.screenshot(path="jules-scratch/verification/report_view_create_note.png")
        print("Report view screenshot taken, 'Create Note' button is visible.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
