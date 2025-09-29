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


async def test_create_and_get_mistake(async_client: AsyncClient):
    """
    Tests creating a mistake and then retrieving it by its ID.
    """
    await setup_general_account(async_client)

    mistake_name = "My Test Mistake"
    mistake_description = "A detailed description of the mistake."

    # Create mistake
    create_response = await async_client.post(
        "/api/v1/me/mistakes",
        json={"name": mistake_name, "description": mistake_description}
    )
    assert create_response.status_code == 201
    created_data = create_response.json()
    mistake_id = created_data["id"]

    assert created_data["name"] == mistake_name
    assert created_data["description"] == mistake_description
    assert "general_account_id" in created_data

    # Get the mistake by ID
    get_response = await async_client.get(f"/api/v1/mistakes/{mistake_id}")
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["id"] == mistake_id
    assert get_data["name"] == mistake_name


async def test_list_my_mistakes(async_client: AsyncClient):
    """
    Tests listing all mistakes for the authenticated user.
    """
    await setup_general_account(async_client)

    # Create a couple of mistakes
    await async_client.post("/api/v1/me/mistakes", json={"name": "Mistake One", "description": "Desc 1"})
    await async_client.post("/api/v1/me/mistakes", json={"name": "Mistake Two", "description": "Desc 2"})

    # List mistakes
    list_response = await async_client.get("/api/v1/me/mistakes")
    assert list_response.status_code == 200
    list_data = list_response.json()

    # The number of mistakes might be more than 2 if other tests ran before
    assert len(list_data) >= 2
    names = {m["name"] for m in list_data}
    assert "Mistake One" in names
    assert "Mistake Two" in names


async def test_update_mistake(async_client: AsyncClient):
    """
    Tests updating an existing mistake.
    """
    await setup_general_account(async_client)

    # Create a mistake
    create_response = await async_client.post(
        "/api/v1/me/mistakes",
        json={"name": "Original Name", "description": "Original Description"}
    )
    assert create_response.status_code == 201
    mistake_id = create_response.json()["id"]

    # Update the mistake
    updated_name = "Updated Name"
    updated_description = "Updated Description"
    update_response = await async_client.put(
        f"/api/v1/mistakes/{mistake_id}",
        json={"name": updated_name, "description": updated_description}
    )
    assert update_response.status_code == 200
    updated_data = update_response.json()
    assert updated_data["name"] == updated_name
    assert updated_data["description"] == updated_description

    # Verify the update
    get_response = await async_client.get(f"/api/v1/mistakes/{mistake_id}")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == updated_name
    assert get_response.json()["description"] == updated_description


async def test_delete_mistake(async_client: AsyncClient):
    """
    Tests deleting a mistake.
    """
    await setup_general_account(async_client)

    # Create a mistake
    create_response = await async_client.post("/api/v1/me/mistakes", json={"name": "To Be Deleted"})
    assert create_response.status_code == 201
    mistake_id = create_response.json()["id"]

    # Delete the mistake
    delete_response = await async_client.delete(f"/api/v1/mistakes/{mistake_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["ok"] is True

    # Verify it's gone
    get_response = await async_client.get(f"/api/v1/mistakes/{mistake_id}")
    assert get_response.status_code == 404