# backend/tests/controllers/test_news_impact_controller.py
import pytest
from httpx import AsyncClient
import uuid

pytestmark = pytest.mark.anyio


async def get_general_account_id(client: AsyncClient) -> str:
    """Helper to get or create a general account for the current test user."""
    response = await client.get("/api/v1/general-accounts/me/")
    if response.status_code == 200 and response.json() is not None:
        return response.json()["id"]
    response = await client.post("/api/v1/general-accounts/", json={"label": "Test Account"})
    assert response.status_code == 201
    return response.json()["id"]


async def create_news_impact_group(client: AsyncClient, name: str) -> str:
    """Helper to create a news impact group."""
    group_data = {"name": name}
    response = await client.post("/api/v1/me/news-impacts-groups", json=group_data)
    assert response.status_code == 201
    return response.json()["id"]


async def test_create_and_get_news_impact(authenticated_client_factory):
    """Tests creating a news impact within a group and then retrieving it."""
    async with authenticated_client_factory() as client:
        await get_general_account_id(client)
        group_id = await create_news_impact_group(client, "Test News Group")

        impact_data = {"name": "High Impact News", "group_id": group_id}
        create_response = await client.post("/api/v1/me/news-impacts", json=impact_data)

        assert create_response.status_code == 201
        created_impact = create_response.json()
        impact_id = created_impact["id"]

        assert created_impact["name"] == impact_data["name"]
        assert created_impact["group_id"] == group_id

        get_response = await client.get(f"/api/v1/me/news-impacts/{impact_id}")
        assert get_response.status_code == 200
        retrieved_impact = get_response.json()
        assert retrieved_impact["id"] == impact_id
        assert retrieved_impact["name"] == impact_data["name"]


async def test_list_my_news_impacts(authenticated_client_factory):
    """Tests listing all news impacts for the authenticated user."""
    async with authenticated_client_factory() as client:
        await get_general_account_id(client)
        group_id = await create_news_impact_group(client, "Listing Group")

        await client.post("/api/v1/me/news-impacts", json={"name": "Impact A", "group_id": group_id})
        await client.post("/api/v1/me/news-impacts", json={"name": "Impact B", "group_id": group_id})

        # Test with trailing slash
        list_response_slash = await client.get("/api/v1/me/news-impacts/")
        assert list_response_slash.status_code == 200
        impacts_slash = list_response_slash.json()
        assert len(impacts_slash) >= 2
        impact_names_slash = {i["name"] for i in impacts_slash}
        assert "Impact A" in impact_names_slash
        assert "Impact B" in impact_names_slash

        # Test without trailing slash
        list_response_no_slash = await client.get("/api/v1/me/news-impacts")
        assert list_response_no_slash.status_code == 200
        impacts_no_slash = list_response_no_slash.json()
        assert len(impacts_no_slash) >= 2
        impact_names_no_slash = {i["name"] for i in impacts_no_slash}
        assert "Impact A" in impact_names_no_slash
        assert "Impact B" in impact_names_no_slash


async def test_update_news_impact(authenticated_client_factory):
    """Tests updating an existing news impact."""
    async with authenticated_client_factory() as client:
        await get_general_account_id(client)
        group_id = await create_news_impact_group(client, "Update Group")

        create_response = await client.post("/api/v1/me/news-impacts", json={"name": "Original Impact", "group_id": group_id})
        assert create_response.status_code == 201
        impact_id = create_response.json()["id"]

        update_data = {"name": "Updated Impact Name"}
        update_response = await client.put(f"/api/v1/me/news-impacts/{impact_id}", json=update_data)
        assert update_response.status_code == 200
        updated_impact = update_response.json()
        assert updated_impact["name"] == update_data["name"]


async def test_delete_news_impact(authenticated_client_factory):
    """Tests deleting a news impact."""
    async with authenticated_client_factory() as client:
        await get_general_account_id(client)
        group_id = await create_news_impact_group(client, "Delete Group")

        create_response = await client.post("/api/v1/me/news-impacts", json={"name": "To Be Deleted", "group_id": group_id})
        assert create_response.status_code == 201
        impact_id = create_response.json()["id"]

        delete_response = await client.delete(f"/api/v1/me/news-impacts/{impact_id}")
        assert delete_response.status_code == 204

        get_response = await client.get(f"/api/v1/me/news-impacts/{impact_id}")
        assert get_response.status_code == 404

async def test_user_cannot_create_impact_in_other_users_group(authenticated_client_factory):
    """Tests that a user cannot create a news impact in another user's group."""
    group_id_user1 = None
    async with authenticated_client_factory() as client1:
        await get_general_account_id(client1)
        group_id_user1 = await create_news_impact_group(client1, "User 1's Group")

    assert group_id_user1 is not None, "Failed to create group with client1"

    async with authenticated_client_factory() as client2:
        await get_general_account_id(client2)

        impact_data = {"name": "Malicious Impact", "group_id": group_id_user1}
        create_response = await client2.post("/api/v1/me/news-impacts", json=impact_data)
        assert create_response.status_code == 404
