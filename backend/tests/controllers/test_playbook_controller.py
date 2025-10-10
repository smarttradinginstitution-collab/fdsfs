import pytest
from httpx import AsyncClient
from uuid import uuid4

pytestmark = pytest.mark.anyio

async def setup_general_account(client: AsyncClient) -> str:
    """
    Helper function to ensure a general account exists for the test user.
    Returns the general_account_id.
    """
    # Check if account exists first to avoid errors on subsequent calls within the same test
    response = await client.get("/api/v1/general-accounts/me")
    if response.status_code == 200:
        return response.json()["id"]

    # If not, create it
    response = await client.post("/api/v1/general-accounts/")
    assert response.status_code == 201, "Failed to create general account for setup"
    return response.json()["id"]


async def test_create_and_get_playbook(async_client: AsyncClient):
    """
    Tests creating a playbook and then retrieving it by its ID.
    """
    await setup_general_account(async_client)

    playbook_data = {
        "title": "My Test Playbook",
        "description": "This is a test description.",
        "private": True
    }

    # Create playbook
    create_response = await async_client.post(
        "/api/v1/me/playbooks",
        json=playbook_data
    )
    assert create_response.status_code == 201
    created_data = create_response.json()
    playbook_id = created_data["id"]

    assert created_data["title"] == playbook_data["title"]
    assert created_data["description"] == playbook_data["description"]
    assert created_data["private"] == playbook_data["private"]
    assert "general_account_id" in created_data
    assert "rules_groups" in created_data
    assert created_data["rules_groups"] == []

    # Get the playbook by ID
    get_response = await async_client.get(f"/api/v1/playbooks/{playbook_id}")
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["id"] == playbook_id
    assert get_data["title"] == playbook_data["title"]
    assert get_data["description"] == playbook_data["description"]


async def test_list_my_playbooks(async_client: AsyncClient):
    """
    Tests listing all playbooks for the authenticated user.
    """
    await setup_general_account(async_client)

    # Create a couple of playbooks
    await async_client.post("/api/v1/me/playbooks", json={"title": "Playbook One", "description": "Desc 1"})
    await async_client.post("/api/v1/me/playbooks", json={"title": "Playbook Two", "description": "Desc 2"})

    # List playbooks
    list_response = await async_client.get("/api/v1/me/playbooks")
    assert list_response.status_code == 200
    list_data = list_response.json()

    # The number of playbooks might be more than 2 if other tests ran before
    assert len(list_data) >= 2
    titles = {p["title"] for p in list_data}
    assert "Playbook One" in titles
    assert "Playbook Two" in titles


async def test_update_playbook(async_client: AsyncClient):
    """
    Tests updating an existing playbook.
    """
    await setup_general_account(async_client)

    # Create a playbook
    create_response = await async_client.post(
        "/api/v1/me/playbooks",
        json={"title": "Original Title", "description": "Original Desc", "private": False}
    )
    assert create_response.status_code == 201
    playbook_id = create_response.json()["id"]

    # Update the playbook
    update_data = {
        "title": "Updated Title",
        "description": "Updated Desc",
        "private": True
    }
    update_response = await async_client.put(
        f"/api/v1/playbooks/{playbook_id}",
        json=update_data
    )
    assert update_response.status_code == 200
    updated_response_data = update_response.json()
    assert updated_response_data["title"] == update_data["title"]
    assert updated_response_data["description"] == update_data["description"]
    assert updated_response_data["private"] == update_data["private"]

    # Verify the update
    get_response = await async_client.get(f"/api/v1/playbooks/{playbook_id}")
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["title"] == update_data["title"]
    assert get_data["description"] == update_data["description"]
    assert get_data["private"] == update_data["private"]


async def test_delete_playbook(async_client: AsyncClient):
    """
    Tests deleting a playbook.
    """
    await setup_general_account(async_client)

    # Create a playbook
    create_response = await async_client.post(
        "/api/v1/me/playbooks",
        json={"title": "To Be Deleted", "description": "This will be deleted."}
    )
    assert create_response.status_code == 201
    playbook_id = create_response.json()["id"]

    # Delete the playbook
    delete_response = await async_client.delete(f"/api/v1/playbooks/{playbook_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["ok"] is True

    # Verify it's gone
    get_response = await async_client.get(f"/api/v1/playbooks/{playbook_id}")
    assert get_response.status_code == 404


async def test_create_playbook_with_duplicate_title(async_client: AsyncClient):
    """
    Tests that creating a playbook with a duplicate title for the same user fails.
    """
    await setup_general_account(async_client)
    playbook_data = {"title": "Duplicate Title Playbook", "description": "First one."}

    # Create the first playbook
    response1 = await async_client.post("/api/v1/me/playbooks", json=playbook_data)
    assert response1.status_code == 201, "First playbook creation failed"

    # Attempt to create a second playbook with the same title
    response2 = await async_client.post("/api/v1/me/playbooks", json=playbook_data)
    assert response2.status_code == 409
    assert "already exists" in response2.json()["detail"]


async def test_update_playbook_to_duplicate_title(async_client: AsyncClient):
    """
    Tests that updating a playbook to a title that already exists for another playbook fails.
    """
    await setup_general_account(async_client)

    # Create two playbooks
    playbook1_data = {"title": "Playbook A", "description": "I am A."}
    playbook2_data = {"title": "Playbook B", "description": "I am B."}
    response1 = await async_client.post("/api/v1/me/playbooks", json=playbook1_data)
    response2 = await async_client.post("/api/v1/me/playbooks", json=playbook2_data)
    assert response1.status_code == 201
    assert response2.status_code == 201
    playbook2_id = response2.json()["id"]

    # Attempt to update Playbook B to have the same title as Playbook A
    update_data = {"title": "Playbook A"}
    update_response = await async_client.put(f"/api/v1/playbooks/{playbook2_id}", json=update_data)
    assert update_response.status_code == 409
    assert "already exists" in update_response.json()["detail"]


async def test_update_playbook_with_same_title(async_client: AsyncClient):
    """
    Tests that updating a playbook's other fields without changing its title succeeds.
    """
    await setup_general_account(async_client)
    playbook_data = {"title": "Consistent Title", "description": "Original Description"}
    create_response = await async_client.post("/api/v1/me/playbooks", json=playbook_data)
    assert create_response.status_code == 201
    playbook_id = create_response.json()["id"]

    # Update description but keep the title the same
    update_data = {"title": "Consistent Title", "description": "Updated Description"}
    update_response = await async_client.put(f"/api/v1/playbooks/{playbook_id}", json=update_data)
    assert update_response.status_code == 200
    assert update_response.json()["description"] == "Updated Description"