from playwright.sync_api import sync_playwright, expect
import time

def run_verification():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            # 1. Navigate to the login page
            page.goto("http://localhost:5173/login", timeout=10000)

            # Debug: Print page content
            time.sleep(2) # Give page a moment to render anything
            content = page.content()
            print("--- PAGE CONTENT ---")
            print(content)
            print("--------------------")

            # 2. Log in
            page.get_by_label("Email").fill("cutio.venezia@aol.com")
            page.get_by_label("Password").fill("Asdfg12345")
            page.get_by_role("button", name="Login").click()

            # 3. Navigate to the connections page
            # Use a robust locator to wait for the page to load
            expect(page.get_by_role("heading", name="Dashboard")).to_be_visible(timeout=10000)
            page.get_by_role("link", name="Connections").click()

            # 4. Find a connection and delete it
            expect(page.get_by_role("heading", name="Connessioni Broker")).to_be_visible()

            # Find the first row in the table
            first_row = page.locator("tbody tr").first
            expect(first_row).to_be_visible()

            # Get the name of the broker from the first row to verify deletion later
            broker_name_cell = first_row.locator("td").first
            broker_name = broker_name_cell.inner_text()
            print(f"Attempting to delete connection for: {broker_name}")

            # Click the delete button in that row
            delete_button = first_row.get_by_role("button", name="Delete connection")
            delete_button.click()

            # 5. Interact with the confirmation modal
            modal = page.locator(".modal-content") # Assuming modal has this class, might need adjustment
            if not modal.is_visible():
                modal = page.get_by_role("dialog") # Fallback to role

            expect(modal.get_by_role("heading", name="Delete Connection")).to_be_visible()

            # Type "delete" to confirm
            modal.get_by_label('To confirm, please type "delete" below:').fill("delete")

            # Click the final confirm button
            modal.get_by_role("button", name="Confirm").click()

            # 6. Assertions
            # Check for success toast
            success_toast = page.get_by_text("✅ Connessione cancellata con successo")
            expect(success_toast).to_be_visible()

            # Check that the connection is removed from the table
            # This is tricky, so we'll just check that the text of the deleted broker is no longer there.
            expect(page.get_by_text(broker_name)).not_to_be_visible()

            print("Verification successful: Connection deleted and success toast shown.")

            # 7. Screenshot
            page.screenshot(path="jules-scratch/verification/delete-connection-success.png")
            print("Screenshot captured.")

        except Exception as e:
            print(f"An error occurred during verification: {e}")
            page.screenshot(path="jules-scratch/verification/verification-error.png")
            raise

        finally:
            browser.close()

if __name__ == "__main__":
    run_verification()
