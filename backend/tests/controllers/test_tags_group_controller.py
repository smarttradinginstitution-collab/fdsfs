import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.anyio


async def get_general_account_id(client: AsyncClient) -> str:
    """Helper to get or create a general account for the current test user."""
    response = await client.get("/api/v1/general-accounts/me/")
    if response.status_code == 200 and response.json() is not None:
        return response.json()["id"]

    response = await client.post("/api/v1/general-accounts/", json={"label": "Test Account"})
    assert response.status_code == 201
    return response.json()["id"]


async def test_create_and_get_tags_group(authenticated_client_factory):
    """Tests creating a tags group and then retrieving it."""
    async with authenticated_client_factory() as client:
        await get_general_account_id(client)

        group_data = {"name": "Test Group", "description": "A group for testing"}
        create_response = await client.post("/api/v1/tags-groups/", json=group_data)

        assert create_response.status_code == 201
        created_group = create_response.json()
        group_id = created_group["id"]

        assert created_group["name"] == group_data["name"]
        assert created_group["description"] == group_data["description"]

        get_response = await client.get(f"/api/v1/tags-groups/{group_id}/")
        assert get_response.status_code == 200
        retrieved_group = get_response.json()
        assert retrieved_group["id"] == group_id
        assert retrieved_group["name"] == group_data["name"]


async def test_list_tags_groups(authenticated_client_factory):
    """Tests listing all tags groups for the authenticated user."""
    async with authenticated_client_factory() as client:
        await get_general_account_id(client)

        await client.post("/api/v1/tags-groups/", json={"name": "Group A"})
        await client.post("/api/v1/tags-groups/", json={"name": "Group B"})

        list_response = await client.get("/api/v1/tags-groups/")
        assert list_response.status_code == 200
        groups = list_response.json()
        assert len(groups) >= 2
        group_names = {g["name"] for g in groups}
        assert "Group A" in group_names
        assert "Group B" in group_names


async def test_update_tags_group(authenticated_client_factory):
    """Tests updating an existing tags group."""
    async with authenticated_client_factory() as client:
        await get_general_account_id(client)

        create_response = await client.post("/api/v1/tags-groups/", json={"name": "Original Name"})
        assert create_response.status_code == 201
        group_id = create_response.json()["id"]

        update_data = {"name": "Updated Name", "color": "#FFFFFF"}
        update_response = await client.put(f"/api/v1/tags-groups/{group_id}/", json=update_data)
        assert update_response.status_code == 200
        updated_group = update_response.json()
        assert updated_group["name"] == update_data["name"]
        assert updated_group["color"] == update_data["color"]


async def test_delete_tags_group_and_cascade(authenticated_client_factory):
    """Tests deleting a tags group and ensures its associated tags are also deleted."""
    async with authenticated_client_factory() as client:
        await get_general_account_id(client)

        create_group_response = await client.post("/api/v1/tags-groups/", json={"name": "Group to Delete"})
        assert create_group_response.status_code == 201
        group_id = create_group_response.json()["id"]

        tag_data = {"name": "Tag to be deleted", "group_id": group_id}
        create_tag_response = await client.post("/api/v1/me/tags/", json=tag_data)
        assert create_tag_response.status_code == 201
        tag_id = create_tag_response.json()["id"]

        delete_response = await client.delete(f"/api/v1/tags-groups/{group_id}/")
        assert delete_response.status_code == 200
        assert delete_response.json()["ok"] is True

        get_group_response = await client.get(f"/api/v1/tags-groups/{group_id}/")
        assert get_group_response.status_code == 404

        get_tag_response = await client.get(f"/api/v1/tags/{tag_id}/")
        assert get_tag_response.status_code == 404


async def test_user_cannot_access_other_users_group(authenticated_client_factory):
    """Tests that a user cannot access, update, or delete another user's tags group."""
    group_id = None
    async with authenticated_client_factory() as client1:
        await get_general_account_id(client1)
        create_response = await client1.post("/api/v1/tags-groups/", json={"name": "User 1's Group"})
        assert create_response.status_code == 201
        group_id = create_response.json()["id"]

    assert group_id is not None, "Failed to create group with client1"

    async with authenticated_client_factory() as client2:
        await get_general_account_id(client2)

        get_response = await client2.get(f"/api/v1/tags-groups/{group_id}/")
        assert get_response.status_code == 404

        update_response = await client2.put(f"/api/v1/tags-groups/{group_id}/", json={"name": "Hacked"})
        assert update_response.status_code == 404

        delete_response = await client2.delete(f"/api/v1/tags-groups/{group_id}/")
        assert delete_response.status_code == 404