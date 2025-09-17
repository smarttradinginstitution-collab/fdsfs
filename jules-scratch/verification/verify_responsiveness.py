from playwright.sync_api import sync_playwright, expect

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            # 1. Navigate to the app
            page.goto("http://localhost:5173/")

            # 2. Log in
            page.get_by_label("Email").fill("test@test.com")
            page.get_by_label("Password").fill("password")
            page.get_by_role("button", name="Accedi").click()

            # 3. Wait for dashboard to load by looking for a widget title
            # Increased timeout to give the dashboard time to fetch data.
            expect(page.get_by_role("heading", name="Vantage Score")).to_be_visible(timeout=15000)

            # 4. Set a mobile viewport
            page.set_viewport_size({"width": 375, "height": 812}) # iPhone X

            # 5. Take a screenshot
            screenshot_path = "jules-scratch/verification/responsiveness_check.png"
            page.screenshot(path=screenshot_path)
            print(f"Screenshot saved to {screenshot_path}")

        except Exception as e:
            print(f"An error occurred: {e}")
            # Save a screenshot on error to help debug
            page.screenshot(path="jules-scratch/verification/error_screenshot.png")
        finally:
            browser.close()

if __name__ == "__main__":
    run()
