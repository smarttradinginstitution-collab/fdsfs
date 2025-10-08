import pytest
from httpx import AsyncClient
from uuid import UUID, uuid4

pytestmark = pytest.mark.anyio


# Helper functions to set up necessary data for tests
async def setup_general_account(client: AsyncClient) -> str:
    """Ensures a general account exists for the test user and returns its ID."""
    response = await client.get("/api/v1/general-accounts/me")
    if response.status_code == 200 and response.json():
        return response.json()[0]["id"]
    response = await client.post("/api/v1/general-accounts/", json={"label": "Test Account"})
    assert response.status_code == 201, "Failed to create general account"
    return response.json()["id"]

async def create_folder(client: AsyncClient, general_account_id: str) -> str:
    """Creates a notebook folder and returns its ID."""
    folder_data = {"name": f"Test Folder {uuid4()}", "general_account_id": general_account_id}
    # The endpoint is /api/v1/notebook/folders
    response = await client.post("/api/v1/notebook/folders", json=folder_data)
    assert response.status_code == 201, f"Failed to create folder: {response.text}"
    return response.json()["id"]

async def create_note(client: AsyncClient, folder_id: str) -> str:
    """Creates a note and returns its ID."""
    note_data = {"title": f"Test Note {uuid4()}", "folder_id": folder_id}
    response = await client.post("/api/v1/notebook/notes", json=note_data)
    assert response.status_code == 201, f"Failed to create note: {response.text}"
    return response.json()["id"]


# --- Test Cases ---

async def test_create_and_get_note_template(async_client: AsyncClient):
    """Tests creating a note template and then retrieving it by its ID."""
    general_account_id = await setup_general_account(async_client)
    template_data = {
        "title": "My First Template",
        "text": "This is the content of the template.",
        "general_account_id": general_account_id,
    }

    # Create
    create_response = await async_client.post("/api/v1/note-templates", json=template_data)
    assert create_response.status_code == 201
    created_data = create_response.json()
    template_id = created_data["id"]

    assert created_data["title"] == template_data["title"]
    assert created_data["text"] == template_data["text"]
    assert "id" in created_data
    assert "created_at" in created_data

    # Get
    get_response = await async_client.get(f"/api/v1/note-templates/{template_id}")
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["id"] == template_id
    assert get_data["title"] == template_data["title"]


async def test_list_my_note_templates(async_client: AsyncClient):
    """Tests listing all note templates for the authenticated user."""
    general_account_id = await setup_general_account(async_client)
    await async_client.post("/api/v1/note-templates", json={"title": "Template A", "general_account_id": general_account_id})
    await async_client.post("/api/v1/note-templates", json={"title": "Template B", "general_account_id": general_account_id})

    # List
    list_response = await async_client.get("/api/v1/note-templates")
    assert list_response.status_code == 200
    list_data = list_response.json()
    assert len(list_data) >= 2
    titles = {t["title"] for t in list_data}
    assert "Template A" in titles
    assert "Template B" in titles


async def test_update_note_template(async_client: AsyncClient):
    """Tests updating an existing note template."""
    general_account_id = await setup_general_account(async_client)
    create_response = await async_client.post(
        "/api/v1/note-templates",
        json={"title": "Original Title", "text": "Original text", "general_account_id": general_account_id},
    )
    assert create_response.status_code == 201
    template_id = create_response.json()["id"]

    # Update
    update_data = {"title": "Updated Title", "text": "Updated text"}
    update_response = await async_client.put(
        f"/api/v1/note-templates/{template_id}", json=update_data
    )
    assert update_response.status_code == 200
    updated_data = update_response.json()
    assert updated_data["title"] == update_data["title"]
    assert updated_data["text"] == update_data["text"]

    # Verify
    get_response = await async_client.get(f"/api/v1/note-templates/{template_id}")
    assert get_response.status_code == 200
    assert get_response.json()["title"] == update_data["title"]


async def test_delete_note_template(async_client: AsyncClient):
    """Tests deleting a note template."""
    general_account_id = await setup_general_account(async_client)
    create_response = await async_client.post(
        "/api/v1/note-templates",
        json={"title": "To Be Deleted", "general_account_id": general_account_id},
    )
    assert create_response.status_code == 201
    template_id = create_response.json()["id"]

    # Delete
    delete_response = await async_client.delete(f"/api/v1/note-templates/{template_id}")
    assert delete_response.status_code == 204

    # Verify
    get_response = await async_client.get(f"/api/v1/note-templates/{template_id}")
    assert get_response.status_code == 404


async def test_add_and_remove_template_from_note(async_client: AsyncClient):
    """Tests associating and disassociating a template from a note."""
    general_account_id = await setup_general_account(async_client)
    folder_id = await create_folder(async_client, general_account_id)
    note_id = await create_note(async_client, folder_id)

    # Create a template
    template_res = await async_client.post(
        "/api/v1/note-templates",
        json={"title": "Association Test Template", "general_account_id": general_account_id},
    )
    assert template_res.status_code == 201
    template_id = template_res.json()["id"]

    # Add template to note
    add_res = await async_client.post(f"/api/v1/notes/{note_id}/templates/{template_id}")
    assert add_res.status_code == 200
    note_data = add_res.json()
    assert len(note_data["templates"]) == 1
    assert note_data["templates"][0]["id"] == template_id

    # Verify the association is present when fetching the note directly
    get_note_res = await async_client.get(f"/api/v1/notebook/notes/{note_id}")
    assert get_note_res.status_code == 200
    assert len(get_note_res.json()["templates"]) == 1

    # Remove template from note
    remove_res = await async_client.delete(f"/api/v1/notes/{note_id}/templates/{template_id}")
    assert remove_res.status_code == 200
    note_data_after_removal = remove_res.json()
    assert len(note_data_after_removal["templates"]) == 0

    # Verify the association is gone
    get_note_res_after = await async_client.get(f"/api/v1/notebook/notes/{note_id}")
    assert get_note_res_after.status_code == 200
    assert len(get_note_res_after.json()["templates"]) == 0