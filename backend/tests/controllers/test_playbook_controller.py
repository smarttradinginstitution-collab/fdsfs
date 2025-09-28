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

    playbook_title = "My Test Playbook"

    # Create playbook
    create_response = await async_client.post(
        "/api/v1/me/playbooks",
        json={"title": playbook_title}
    )
    assert create_response.status_code == 201
    created_data = create_response.json()
    playbook_id = created_data["id"]

    assert created_data["title"] == playbook_title
    assert "general_account_id" in created_data

    # Get the playbook by ID
    get_response = await async_client.get(f"/api/v1/playbooks/{playbook_id}")
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["id"] == playbook_id
    assert get_data["title"] == playbook_title


async def test_list_my_playbooks(async_client: AsyncClient):
    """
    Tests listing all playbooks for the authenticated user.
    """
    await setup_general_account(async_client)

    # Create a couple of playbooks
    await async_client.post("/api/v1/me/playbooks", json={"title": "Playbook One"})
    await async_client.post("/api/v1/me/playbooks", json={"title": "Playbook Two"})

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
    create_response = await async_client.post("/api/v1/me/playbooks", json={"title": "Original Title"})
    assert create_response.status_code == 201
    playbook_id = create_response.json()["id"]

    # Update the playbook
    updated_title = "Updated Title"
    update_response = await async_client.put(
        f"/api/v1/playbooks/{playbook_id}",
        json={"title": updated_title}
    )
    assert update_response.status_code == 200
    updated_data = update_response.json()
    assert updated_data["title"] == updated_title

    # Verify the update
    get_response = await async_client.get(f"/api/v1/playbooks/{playbook_id}")
    assert get_response.status_code == 200
    assert get_response.json()["title"] == updated_title


async def test_delete_playbook(async_client: AsyncClient):
    """
    Tests deleting a playbook.
    """
    await setup_general_account(async_client)

    # Create a playbook
    create_response = await async_client.post("/api/v1/me/playbooks", json={"title": "To Be Deleted"})
    assert create_response.status_code == 201
    playbook_id = create_response.json()["id"]

    # Delete the playbook
    delete_response = await async_client.delete(f"/api/v1/playbooks/{playbook_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["ok"] is True

    # Verify it's gone
    get_response = await async_client.get(f"/api/v1/playbooks/{playbook_id}")
    assert get_response.status_code == 404