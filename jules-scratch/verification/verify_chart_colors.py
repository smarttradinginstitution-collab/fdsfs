import time
from playwright.sync_api import sync_playwright, Page, expect

def verify_chart_colors(page: Page):
    """
    Navigates to the dashboard, waits for the chart to load,
    and takes a screenshot to verify the colors are correct.
    """
    # 1. Navigate to the app. Assuming dashboard is at the root.
    # Using a longer timeout to be safe.
    page.goto("http://localhost:5173/", timeout=60000)

    # 2. Wait for the chart to load.
    # The loading spinner is shown while isLoadingChart is true.
    # We can wait for the widget title to be visible, which appears
    # after the loading is complete.
    chart_widget_title = page.get_by_text("Daily Net Cumulative P&L")

    # Wait up to 30 seconds for the title to be visible.
    # This accounts for the 1.5s mock API delay and any other loading time.
    expect(chart_widget_title).to_be_visible(timeout=30000)

    # 3. Locate the chart container and take a screenshot.
    charts_grid = page.locator(".charts-grid")
    expect(charts_grid).to_be_visible()

    # Add a small delay to ensure canvas animation is complete
    time.sleep(1)

    charts_grid.screenshot(path="jules-scratch/verification/verification.png")
    print("Screenshot saved to jules-scratch/verification/verification.png")

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        verify_chart_colors(page)
        browser.close()

if __name__ == "__main__":
    main()
