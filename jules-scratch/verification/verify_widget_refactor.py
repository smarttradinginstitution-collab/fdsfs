from playwright.sync_api import sync_playwright, expect

def handle_response(response):
    print(f"<<< {response.status} {response.url}")

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.on("response", handle_response)
        try:
            print("Navigating to login page...")
            page.goto("http://localhost:5173/login", timeout=90000)
            print("Waiting for page to load...")
            page.wait_for_load_state('networkidle', timeout=90000)
            print("Filling in login form...")
            page.locator('input[placeholder="iltuoindirizzo@email.com"]').fill("test@example.com", timeout=90000)
            page.locator('input[placeholder="••••••••"]').fill("password", timeout=90000)
            page.get_by_role("button", name="Accedi").click()
            print("Waiting for dashboard to load...")
            page.wait_for_url("http://localhost:5173/", timeout=90000)
            print("Dashboard loaded.")
            print("Finding VantageScoreWidget...")
            widget = page.locator(".widget-card", has_text="Vantage Score")
            print("Taking screenshot...")
            widget.screenshot(path="jules-scratch/verification/verification.png")
            print("Screenshot saved.")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    run()
