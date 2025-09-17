from playwright.sync_api import sync_playwright, expect, TimeoutError

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            # 1. Navigate to the app with a longer timeout
            print("Navigating to the page...")
            page.goto("http://localhost:5173/", timeout=90000, wait_until='networkidle')
            print("Page navigation complete.")

            # 2. Log in
            print("Attempting to log in...")
            page.get_by_label("Email").fill("test@test.com")
            page.get_by_label("Password").fill("password")
            page.get_by_role("button", name="Accedi").click()
            print("Login submitted.")

            # 3. Wait for dashboard to load by looking for a stable element
            print("Waiting for dashboard to load...")
            expect(page.get_by_role("heading", name="Dashboard")).to_be_visible(timeout=30000)
            print("Dashboard loaded.")

            # 4. Set a mobile viewport
            print("Setting viewport to mobile size...")
            page.set_viewport_size({"width": 375, "height": 812}) # iPhone X
            # Add a small wait for the layout to reflow
            page.wait_for_timeout(1000)
            print("Viewport set.")

            # 5. Take a screenshot
            screenshot_path = "jules-scratch/verification/final_verification.png"
            print(f"Taking screenshot to {screenshot_path}...")
            page.screenshot(path=screenshot_path)
            print("Screenshot saved.")

        except TimeoutError as e:
            print(f"A timeout error occurred: {e}")
            page.screenshot(path="jules-scratch/verification/final_error_screenshot.png")
            print("Error screenshot saved.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            page.screenshot(path="jules-scratch/verification/final_error_screenshot.png")
            print("Error screenshot saved.")
        finally:
            print("Closing browser.")
            browser.close()

if __name__ == "__main__":
    run()
