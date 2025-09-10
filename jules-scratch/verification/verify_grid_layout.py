import time
from playwright.sync_api import sync_playwright, Page, expect

def verify_grid_layout(page: Page):
    """
    Navigates to the dashboard and takes a screenshot of the
    charts grid to verify the 3-column layout.
    """
    page.goto("http://localhost:5173/", timeout=60000)

    # Wait for the loading to finish.
    loading_spinner = page.locator(".charts-grid .loading-container")
    expect(loading_spinner).to_have_count(0, timeout=30000)

    # Now that loading is done, the chart grid should be visible.
    charts_grid = page.locator(".charts-grid")
    expect(charts_grid).to_be_visible()

    # Add a small delay to ensure canvas animation is complete
    time.sleep(1)

    charts_grid.screenshot(path="jules-scratch/verification/grid_layout.png")
    print("Screenshot saved to jules-scratch/verification/grid_layout.png")

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Use a large viewport to trigger the 3-column media query
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        verify_grid_layout(page)
        browser.close()

if __name__ == "__main__":
    main()
