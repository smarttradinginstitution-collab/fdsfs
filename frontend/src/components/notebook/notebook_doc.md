# Notebook Feature: Architectural Overview

This document provides a comprehensive, full-stack overview of the Notebook feature, detailing its architecture from the frontend components down to the database models.

## 1. High-Level Architecture

The Notebook feature is built on a modern, decoupled, full-stack architecture:

-   **Frontend:** A Vue.js 3 Single Page Application (SPA) using Vite. It employs Pinia for state management and TailwindCSS with semantic tokens for styling.
-   **Backend:** A FastAPI application that serves a RESTful API. It follows a layered architecture (Controller -> Service -> Repository).
-   **Database:** A PostgreSQL database with the schema managed by SQLAlchemy ORM models.
-   **Communication:** The frontend communicates with the backend via a REST API, with data contracts defined by Pydantic schemas.

The feature is designed around a three-column layout: **Folders**, **Notes**, and a **Note Editor**.

---

## 2. Frontend Analysis

### 2.1. Main View (`NotebookView.vue`)

-   **Purpose:** Acts as the main container and orchestrator for the entire notebook page.
-   **Structure:**
    -   Sets up the main three-column `grid` layout.
    -   Includes a top-level search bar.
    -   Renders the three core child components: `FolderList`, `NoteList`, and `NoteEditor`.
-   **Logic:**
    -   On mount (`onMounted` hook), it calls the `notebookStore.fetchFolders()` action to initialize the folder list.
    -   The `NoteEditor` is conditionally rendered only when a note is selected in the store (`store.selectedNote`).
    -   The search query from the search bar is passed as a `prop` to the `NoteList` component for filtering.

### 2.2. Child Components

#### `FolderList.vue`

-   **Purpose:** Displays the list of system-generated and user-created folders.
-   **Data Source:** Reactively renders folders from `store.systemFolders` and `store.userFolders` getters.
-   **Key Interactions:**
    -   **Add Folder:** Opens an `AddFolderModal` which, on submission, calls the `store.createFolder()` action.
    -   **Select Folder:** On click, it calls `store.selectFolder(folderId)`, triggering the note list to update.
    -   **Styling:** Differentiates between system and user folders and highlights the currently selected folder based on `store.selectedFolderId`.

#### `NoteList.vue`

-   **Purpose:** Displays the list of notes for the currently selected folder and handles note creation.
-   **Data Source:** Reactively renders notes from the `store.notes` array. It uses a `computed` property to filter these notes based on the `searchQuery` prop.
-   **Key Interactions:**
    -   **Select Note:** On click, calls `store.selectNote(noteId)`, which causes the `NoteEditor` to display the note's content.
    -   **Delete Note:** Calls `store.deleteNote(noteId)` after user confirmation.
    -   **Dynamic Header:** The header of this component is highly dynamic and changes based on the `system_folder_identifier` of the selected folder:
        -   **Trade Notes:** Shows a "New Note" button that opens a modal to create a trade-linked note.
        -   **Daily Journal:** Shows a "Log Day" date picker that calls `store.logDay()` to create a note for a specific date.
        -   **Session Recap:** Shows a "Log Session" date range picker to create a summary note for a period.
        -   **User Folders:** Also uses the "Log Day" functionality.

#### `NoteEditor.vue`

-   **Purpose:** Displays the content of the selected note and allows for editing.
-   **Editor:** Uses the **Tiptap** rich text editor (`useEditor` from `@tiptap/vue-3`).
-   **Key Features:**
    -   **Auto-Save:** The editor's content and the note's title are watched for changes. A debounced function calls `store.updateNote()` automatically after a period of inactivity, providing a seamless auto-save experience.
    -   **Metadata Display:** Shows the note's creation and update timestamps.
    -   **Conditional Financial Data:** This is a critical feature. It checks the context of the selected note and displays relevant financial metrics fetched by the store:
        -   If the note is in "Trade Notes" and linked to a trade, it displays **Gross P&L, Commissions, and Net ROI**.
        -   If the note is in "Daily Journal", it displays the **Net P&L** for that specific day.

### 2.3. State Management (`notebookStore.js`)

-   **Purpose:** The single source of truth for the entire Notebook feature on the frontend.
-   **State:** Manages `folders`, `notes`, `selectedFolderId`, `selectedNoteId`, loading/error states, and `financialData`.
-   **Getters:** Provides computed properties like `selectedFolder`, `selectedNote`, and separates folders into `systemFolders` and `userFolders`. It also creates the virtual "All Notes" folder entirely in the frontend.
-   **Actions (API Communication):**
    -   Handles all CRUD operations for notes and folders by making calls to the backend API via a centralized `apiClient`.
    -   Contains the business logic for the various note creation workflows (`logDay`, `createTradeNote`, `createSessionRecapNote`).
    -   Implements the crucial `fetchFinancialDataForSelectedNote` action, which intelligently calls different backend endpoints based on the selected note's context.
    -   The `updateNote` action is intentionally "silent" (doesn't set a global loading state) to support the smooth auto-save feature in the editor.

---

## 3. Backend Analysis

### 3.1. API Layer (`notebook_router.py`)

-   **Purpose:** Defines all the REST API endpoints for the notebook feature under the `/api/v1/notebook` prefix.
-   **Structure:** Maps HTTP methods (GET, POST, PUT, DELETE) for `/folders` and `/notes` resources to the corresponding methods in the `NotebookController`.
-   **Example Endpoints:**
    -   `GET /folders`: Lists all folders for a user.
    -   `GET /folders/{folder_id}/notes`: Lists all notes within a specific folder.
    -   `GET /notes/all`: Lists all notes for a user, regardless of folder.
    -   `PUT /notes/{note_id}`: Updates a specific note.

### 3.2. Controller Layer (`notebook_controller.py`)

-   **Purpose:** Acts as a thin layer that connects the API routes to the business logic.
-   **Logic:**
    -   It uses FastAPI's dependency injection to get the `current_user` and an instance of the `NotebookService`.
    -   It **delegates all business logic** to the `NotebookService`, passing along the user's ID and the request data (Pydantic schemas).
    -   It does not contain any business logic itself.

### 3.3. Service Layer (`notebook_service.py`)

-   **Purpose:** The core of the backend logic. It orchestrates all operations related to notebooks.
-   **Key Responsibilities:**
    -   **Authorization:** Ensures a user can only access their own data by first fetching their `general_account_id` and using it for all subsequent database queries.
    -   **System Folder Management:** Contains the logic to automatically create the three system folders ("Trade Notes", "Daily Journal", "Session Recap") for a user if they don't exist. It also prevents the deletion of these folders.
    -   **Business Rule Enforcement:** Validates data based on business rules, such as preventing the creation of folders with duplicate names or notes linked to the same trade.
    -   **Repository Orchestration:** Uses the `NotebookFolderRepository` and `NoteRepository` to perform the actual database operations.

### 3.4. Data Schemas (`Schemas/notebook.py`)

-   **Purpose:** Defines the data contracts for the API using Pydantic models.
-   **Key Schemas:**
    -   `NoteCreate`, `NoteUpdate`, `NoteRead`: Define the structure for creating, updating, and returning notes. `NoteRead` can optionally include the full related `Trade` object.
    -   `NotebookFolderCreate`, `NotebookFolderUpdate`, `NotebookFolderRead`: Define folder structures.
    -   `NotebookFolderReadWithCount`: An optimized schema for folder lists that includes the `note_count` without embedding the full array of notes, preventing performance issues.

### 3.5. Database Models

#### `Models/note.py`

-   **Table:** `notes`
-   **Key Columns:** `id`, `folder_id`, `trade_id` (nullable), `note_date` (nullable), `title`, `content` (JSONB).
-   **Relationships:**
    -   **Many-to-One with `notebook_folders`:** A note belongs to exactly one folder. If the folder is deleted, its notes are also deleted (`ondelete="CASCADE"`).
    -   **One-to-One with `trades`:** A note can be linked to one trade. If the trade is deleted, the `trade_id` is set to `NULL`, but the note remains (`ondelete="SET NULL"`).

#### `Models/notebook_folder.py`

-   **Table:** `notebook_folders`
-   **Key Columns:** `id`, `general_account_id`, `name`, `color`, `folder_type` (Enum), `system_folder_identifier` (Enum), `is_system_folder` (boolean).
-   **Relationships:**
    -   **Many-to-One with `general_accounts`:** A folder belongs to one user account.
    -   **One-to-Many with `notes`:** A folder can have many notes. If the folder is deleted, all its notes are deleted (`cascade="all, delete-orphan"`).

---

## 4. Key End-to-End Workflows

### Workflow 1: Initial Page Load

1.  **FE:** `NotebookView.vue` mounts and calls `store.fetchFolders()`.
2.  **FE:** The store sets `isLoadingFolders` to `true` and sends a request: `GET /api/v1/notebook/folders`.
3.  **BE:** The request hits `NotebookController.list_my_folders`.
4.  **BE:** The controller calls `NotebookService.get_all_folders`.
5.  **BE:** The service gets the user's `general_account_id`, ensures system folders exist (creating them if necessary), and calls `NotebookFolderRepository.list_by_general_account_id`.
6.  **DB:** The repository queries the `notebook_folders` table, joining with `notes` to get a `note_count`.
7.  **BE -> FE:** The data is returned as a list of `NotebookFolderReadWithCount` schemas.
8.  **FE:** The store is populated with the folders, `isLoadingFolders` is set to `false`, and the `FolderList.vue` component renders the folders. A default folder is automatically selected.

### Workflow 2: Note Editing and Auto-Saving

1.  **FE:** User clicks a note in `NoteList.vue`, calling `store.selectNote(noteId)`.
2.  **FE:** `NoteEditor.vue` becomes visible and is populated with the selected note's data. The Tiptap editor is initialized.
3.  **FE:** User types in the title `input` or the Tiptap editor.
4.  **FE:** `watch` functions in `NoteEditor.vue` detect the changes.
5.  **FE:** A debounced `saveNote` function is triggered after 1.5 seconds of inactivity.
6.  **FE:** The `saveNote` function calls `store.updateNote()`, passing the note ID and the new title/content.
7.  **FE:** The store sends a **"silent"** request (no global loading spinner): `PUT /api/v1/notebook/notes/{note_id}`.
8.  **BE:** The request hits `NotebookController.update_note`.
9.  **BE:** The controller calls `NotebookService.update_note`, which validates ownership.
10. **BE:** The service calls `NoteRepository.update` to save the changes to the database.
11. **BE -> FE:** The updated note is returned.
12. **FE:** The store optimistically updates the local note object in the `notes` array, ensuring the UI is in sync without a full refetch.

### Workflow 3: Displaying Financial Data for a Trade Note

1.  **FE:** User selects a note that belongs to the "Trade Notes" folder.
2.  **FE:** `store.selectNote(noteId)` is called.
3.  **FE:** This action immediately calls `store.fetchFinancialDataForSelectedNote()`.
4.  **FE:** Inside this action, it detects that the note's folder is "Trade Notes" and that `note.trade_id` exists.
5.  **FE:** The store sends a request: `GET /api/v1/trades/{note.trade_id}/financial_summary`.
6.  **BE:** This request is handled by the `TradesController`, which uses the `MetricsCalculator` service to compute the trade's P&L, ROI, etc.
7.  **BE -> FE:** The financial data is returned.
8.  **FE:** The `financialData` object in the `notebookStore` is populated.
9.  **FE:** `NoteEditor.vue`, which is watching `store.financialData`, reactively updates to display the Gross P&L, Commissions, and Net ROI in the metadata section.