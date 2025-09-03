import asyncio
from playwright.async_api import async_playwright, Page, expect

async def main():
    """
    Questo script verifica la responsività della dashboard a diverse dimensioni.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        print("Navigazione alla dashboard...")
        await page.goto("http://localhost:5173/")

        # Attendi che un elemento chiave (la griglia delle statistiche) sia visibile
        await expect(page.locator(".stats-grid")).to_be_visible(timeout=10000)
        print("Dashboard caricata.")

        # --- Screenshot Desktop ---
        print("Cattura screenshot Desktop (1280x720)...")
        await page.set_viewport_size({"width": 1280, "height": 720})
        # Aggiungo un piccolo ritardo per assicurare il rendering completo
        await page.wait_for_timeout(1000)
        await page.screenshot(path="jules-scratch/verification/screenshot_desktop.png")

        # --- Screenshot Tablet ---
        print("Cattura screenshot Tablet (768x1024)...")
        await page.set_viewport_size({"width": 768, "height": 1024})
        await page.wait_for_timeout(1000)
        await page.screenshot(path="jules-scratch/verification/screenshot_tablet.png")

        # --- Screenshot Mobile ---
        print("Cattura screenshot Mobile (375x667)...")
        await page.set_viewport_size({"width": 375, "height": 667})
        await page.wait_for_timeout(1000)
        await page.screenshot(path="jules-scratch/verification/screenshot_mobile.png")

        await browser.close()
        print("Verifica completata. Screenshot salvati.")

if __name__ == "__main__":
    asyncio.run(main())
