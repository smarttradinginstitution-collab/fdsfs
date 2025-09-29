import pytest
from httpx import AsyncClient
from uuid import uuid4, UUID

pytestmark = pytest.mark.anyio

async def setup_playbook(client: AsyncClient) -> str:
    """
    Helper function to ensure a playbook exists for the test user.
    Returns the playbook_id.
    """
    # Ensure general account exists
    response = await client.get("/api/v1/general-accounts/me")
    if response.status_code != 200:
        await client.post("/api/v1/general-accounts/")

    # Create a playbook
    playbook_data = {
        "title": "Playbook for Rule Group Tests",
        "description": "A test playbook.",
        "private": False
    }
    response = await client.post("/api/v1/me/playbooks", json=playbook_data)
    assert response.status_code == 201, "Failed to create playbook for setup"
    return response.json()["id"]


async def test_create_and_list_rule_groups(async_client: AsyncClient):
    """
    Tests creating rule groups for a playbook and then listing them.
    """
    playbook_id = await setup_playbook(async_client)

    group1_data = {"name_group": "Group One", "playbook_id": playbook_id}
    group2_data = {"name_group": "Group Two", "playbook_id": playbook_id}

    # Create group 1
    create_resp1 = await async_client.post(
        f"/api/v1/playbooks/{playbook_id}/rule-groups/",
        json=group1_data
    )
    assert create_resp1.status_code == 201
    created_data1 = create_resp1.json()
    assert created_data1["name_group"] == group1_data["name_group"]
    assert created_data1["playbook_id"] == playbook_id
    assert "rules" in created_data1
    assert created_data1["rules"] == []

    # Create group 2
    create_resp2 = await async_client.post(
        f"/api/v1/playbooks/{playbook_id}/rule-groups/",
        json=group2_data
    )
    assert create_resp2.status_code == 201

    # List groups for the playbook
    list_resp = await async_client.get(f"/api/v1/playbooks/{playbook_id}/rule-groups/")
    assert list_resp.status_code == 200
    list_data = list_resp.json()
    assert len(list_data) >= 2

    names = {g["name_group"] for g in list_data}
    assert "Group One" in names
    assert "Group Two" in names


async def test_update_rule_group(async_client: AsyncClient):
    """
    Tests updating an existing rule group.
    """
    playbook_id = await setup_playbook(async_client)

    # Create a group
    create_resp = await async_client.post(
        f"/api/v1/playbooks/{playbook_id}/rule-groups/",
        json={"name_group": "Original Group Name", "playbook_id": playbook_id}
    )
    assert create_resp.status_code == 201
    group_id = create_resp.json()["id"]

    # Update the group
    update_data = {"name_group": "Updated Group Name"}
    update_resp = await async_client.put(
        f"/api/v1/rule-groups/{group_id}",
        json=update_data
    )
    assert update_resp.status_code == 200
    updated_data = update_resp.json()
    assert updated_data["name_group"] == update_data["name_group"]
    assert updated_data["id"] == group_id

    # Verify the update by fetching the playbook and checking the nested group
    get_playbook_resp = await async_client.get(f"/api/v1/playbooks/{playbook_id}")
    playbook_data = get_playbook_resp.json()
    group_found = False
    for group in playbook_data["rules_groups"]:
        if group["id"] == group_id:
            assert group["name_group"] == update_data["name_group"]
            group_found = True
    assert group_found, "Updated group not found in playbook's nested data."


async def test_delete_rule_group(async_client: AsyncClient):
    """
    Tests deleting a rule group.
    """
    playbook_id = await setup_playbook(async_client)

    # Create a group
    create_resp = await async_client.post(
        f"/api/v1/playbooks/{playbook_id}/rule-groups/",
        json={"name_group": "To Be Deleted", "playbook_id": playbook_id}
    )
    assert create_resp.status_code == 201
    group_id = create_resp.json()["id"]

    # Delete the group
    delete_resp = await async_client.delete(f"/api/v1/rule-groups/{group_id}")
    assert delete_resp.status_code == 200
    assert delete_resp.json()["ok"] is True

    # Verify it's gone from the playbook's list
    get_playbook_resp = await async_client.get(f"/api/v1/playbooks/{playbook_id}")
    playbook_data = get_playbook_resp.json()
    for group in playbook_data["rules_groups"]:
        assert group["id"] != group_id, "Deleted group still found in playbook."