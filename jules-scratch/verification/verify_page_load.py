from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        try:
            print("Navigating to http://localhost:5173/trades...")
            # The router should redirect to /login since we are not authenticated
            page.goto("http://localhost:5173/trades", timeout=10000)
            print("Navigation successful. Taking screenshot...")
            page.screenshot(path="jules-scratch/verification/page-load-test.png")
            print("Screenshot taken successfully.")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    run()