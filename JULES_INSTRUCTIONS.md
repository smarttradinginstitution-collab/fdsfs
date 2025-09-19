Hello! It seems my messages aren't getting through correctly. I've placed the final instructions in this file for you.

Here is a complete and detailed guide for everything you need to do to get the new SnapTrade feature running with the code I've written.

### Prerequisites

Please ensure you have `node` and `npm` installed for the frontend, and `python` and `pip` for the backend, as specified in the project's README.

### Step 1: Database Changes (Supabase)

I have created a new SQL migration file that needs to be run on your Supabase database.

1.  **Find the SQL file:** The file is located at `backend/db/sql/004_snaptrade_tables.sql`.
2.  **Execute the script:**
    *   Go to your Supabase project dashboard.
    *   In the left-hand menu, navigate to "SQL Editor".
    *   Click on "+ New query".
    *   Copy the entire contents of the `004_snaptrade_tables.sql` file and paste it into the editor.
    *   Click "RUN".

This will create the two new tables, `profiles` and `brokerage_connections`, with the necessary columns, foreign keys, and Row Level Security (RLS) policies.

### Step 2: Backend Environment Configuration

I encountered security policies that prevented me from modifying configuration files directly. You will need to make two small manual additions.

1.  **Add SnapTrade Credentials:**
    *   Open the file `backend/.env`.
    *   Add the following two lines to the end of the file:
        ```env
        SNAPTRADE_CLIENT_ID=MARCO-DONA-TEST-PJXKV
        SNAPTRADE_CONSUMER_KEY=BenZ6fKqXPnaCLsOJVxOEudjWGE2r6m9wcubY5abPqTFIk1xMX
        ```

2.  **Add Python Dependencies:**
    *   **SnapTrade SDK:** I was unable to modify `backend/requirements.txt`. Please open it and add the following line to the end:
        ```
        snaptrade-python-sdk
        ```
    *   **Test Dependency:** To run the backend tests, another dependency is required. Please also add this line to `backend/requirements.txt`:
        ```
        aiosqlite
        ```
    *   **Install Dependencies:** Once the file is modified, run this command in your terminal from the project's root directory:
        ```bash
        pip install -r backend/requirements.txt
        ```

### Step 3: Startup and Verification

Once the previous steps are completed, the system is ready.

1.  **Start the Backend:**
    *   Run this command from the project's root directory:
        ```bash
        uvicorn app.main:app --reload --app-dir backend
        ```

2.  **Start the Frontend:**
    *   Open a **new terminal**.
    *   Run these commands:
        ```bash
        cd frontend
        npm install
        npm run dev
        ```

3.  **Functional Verification:**
    *   Open your browser to the address provided by Vite (usually `http://localhost:5173`).
    *   Log in with a test user.
    *   Navigate to the new "Connections" page in the sidebar.
    *   You should see the first step for SnapTrade registration. Click the "Crea Profilo SnapTrade" button.
    *   The UI should show a loading state and then a success notification.
    *   After success, the page should update to show the connection management section, ready for future development.
    *   You can verify in your Supabase database (in the `profiles` table) that a `snaptrade_user_secret` has been saved for that user.

If you follow these steps, everything should work as expected. Let me know if you run into any issues!
