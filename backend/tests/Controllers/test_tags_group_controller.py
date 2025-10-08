import pytest
from httpx import AsyncClient

# Mark all tests in this file as asyncio
pytestmark = pytest.mark.asyncio


async def test_create_tags_group_conflict(async_client: AsyncClient):
    """
    Tests that creating a tags group with a duplicate name for the same
    account fails with a 409 Conflict error.
    """
    # First, create a general account for the user, as it's required.
    general_account_response = await async_client.post(
        "/api/v1/general-accounts/", json={"label": "Test General Account"}
    )
    assert general_account_response.status_code == 201, "Failed to create general account"

    # Define the tags group data
    tags_group_data = {
        "name": "Test Group",
        "description": "A group for testing",
        "color": "#FF0000",
        "position": 1,
    }

    # 1. First attempt: Create the tags group, which should succeed
    response = await async_client.post("/api/v1/tags-groups/", json=tags_group_data)
    assert response.status_code == 201, f"Expected 201 Created, got {response.status_code}: {response.text}"
    created_group = response.json()
    assert created_group["name"] == tags_group_data["name"]

    # 2. Second attempt: Try to create a group with the same name
    response = await async_client.post("/api/v1/tags-groups/", json=tags_group_data)

    # Assert that the request fails with a 409 Conflict
    assert response.status_code == 409, f"Expected 409 Conflict, got {response.status_code}: {response.text}"

    # Assert the error message is correct
    error_detail = response.json()
    assert error_detail["detail"] == "Un gruppo di tag con questo nome esiste già."