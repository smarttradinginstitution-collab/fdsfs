import pytest
from httpx import AsyncClient
import uuid

# Mark all tests in this file as asyncio
pytestmark = pytest.mark.asyncio


async def test_create_tag_conflict(async_client: AsyncClient):
    """
    Tests that creating a tag with a duplicate name within the same group
    fails with a 409 Conflict error.
    """
    # 1. Create a general account
    ga_response = await async_client.post(
        "/api/v1/general-accounts/", json={"label": "Test General Account for Tags"}
    )
    assert ga_response.status_code == 201, "Failed to create general account"

    # 2. Create a tags group
    group_data = {"name": "Test Tag Group", "description": "A group for tag tests"}
    group_response = await async_client.post("/api/v1/tags-groups/", json=group_data)
    assert group_response.status_code == 201, "Failed to create tags group"
    group_id = group_response.json()["id"]

    # 3. Define the tag data
    tag_data = {
        "name": "Duplicate Tag",
        "color": "#123456",
        "group_id": group_id,
    }

    # 4. First attempt: Create the tag, which should succeed
    response1 = await async_client.post("/api/v1/me/tags", json=tag_data)
    assert response1.status_code == 201, f"Expected 201, got {response1.status_code}: {response1.text}"
    created_tag = response1.json()
    assert created_tag["name"] == tag_data["name"]

    # 5. Second attempt: Try to create a tag with the same name in the same group
    response2 = await async_client.post("/api/v1/me/tags", json=tag_data)

    # Assert that the request fails with a 409 Conflict
    assert response2.status_code == 409, f"Expected 409, got {response2.status_code}: {response2.text}"

    # Assert the error message is correct
    error_detail = response2.json()
    assert error_detail["detail"] == "Un tag con questo nome esiste già in questo gruppo."