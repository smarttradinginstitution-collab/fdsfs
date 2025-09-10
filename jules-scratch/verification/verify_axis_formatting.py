import time
from playwright.sync_api import sync_playwright, Page, expect

def verify_axis_formatting(page: Page):
    """
    Navigates to the dashboard and takes a screenshot of the
    P&L chart to verify the axis formatting.
    """
    page.goto("http://localhost:5173/", timeout=60000)

    # Wait for the loading to finish.
    loading_spinner = page.locator(".charts-grid .loading-container")
    expect(loading_spinner).to_have_count(0, timeout=30000)

    # Now that loading is done, the chart should be visible.
    chart_widget = page.locator(".chart-widget", has_text="Daily Net Cumulative P&L")
    expect(chart_widget).to_be_visible()

    # Add a small delay to ensure canvas animation is complete
    time.sleep(1)

    chart_widget.screenshot(path="jules-scratch/verification/axis_formatting.png")
    print("Screenshot saved to jules-scratch/verification/axis_formatting.png")

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 720})
        verify_axis_formatting(page)
        browser.close()

if __name__ == "__main__":
    main()
