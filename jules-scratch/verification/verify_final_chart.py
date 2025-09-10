import time
from playwright.sync_api import sync_playwright, Page, expect

def verify_chart(page: Page):
    """
    Navigates to the dashboard, waits for the chart to load,
    and takes a screenshot.
    """
    page.goto("http://localhost:5173/", timeout=60000)

    # Wait for the loading to finish by waiting for the .charts-grid to not
    # contain a loading spinner. A better way is to wait for the chart
    # itself to be visible.
    loading_spinner = page.locator(".charts-grid .loading-container")
    expect(loading_spinner).to_have_count(0, timeout=30000)

    # Now that loading is done, the chart should be visible.
    chart_widget = page.locator(".charts-grid .chart-widget")
    expect(chart_widget).to_be_visible()

    # Add a small delay to ensure canvas animation is complete
    time.sleep(1)

    chart_widget.screenshot(path="jules-scratch/verification/final_chart.png")
    print("Screenshot saved to jules-scratch/verification/final_chart.png")

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        verify_chart(page)
        browser.close()

if __name__ == "__main__":
    main()
