import pytest
from httpx import AsyncClient
from uuid import uuid4

pytestmark = pytest.mark.anyio

async def setup_rule_group(client: AsyncClient) -> tuple[str, str]:
    """
    Helper function to ensure a playbook and a rule group exist.
    Returns a tuple of (playbook_id, group_id).
    """
    # Ensure general account exists
    response = await client.get("/api/v1/general-accounts/me")
    if response.status_code != 200:
        await client.post("/api/v1/general-accounts/")

    # Create a playbook
    playbook_data = {
        "title": "Playbook for Rule Tests",
        "description": "A test playbook for rules.",
        "private": False
    }
    pb_response = await client.post("/api/v1/me/playbooks", json=playbook_data)
    assert pb_response.status_code == 201
    playbook_id = pb_response.json()["id"]

    # Create a rule group
    group_data = {"name_group": "Group for Rule Tests", "playbook_id": playbook_id}
    group_response = await client.post(
        f"/api/v1/playbooks/{playbook_id}/rule-groups/",
        json=group_data
    )
    assert group_response.status_code == 201
    group_id = group_response.json()["id"]

    return playbook_id, group_id


async def test_create_and_list_rules(async_client: AsyncClient):
    """
    Tests creating rules for a group and then listing them.
    """
    playbook_id, group_id = await setup_rule_group(async_client)

    rule1_data = {"rule": "This is rule number 1.", "rules_groups_playbook_id": group_id}
    rule2_data = {"rule": "This is rule number 2.", "rules_groups_playbook_id": group_id}

    # Create rule 1
    create_resp1 = await async_client.post(
        f"/api/v1/rule-groups/{group_id}/rules/",
        json=rule1_data
    )
    assert create_resp1.status_code == 201
    created_data1 = create_resp1.json()
    assert created_data1["rule"] == rule1_data["rule"]
    assert created_data1["rules_groups_playbook_id"] == group_id

    # Create rule 2
    create_resp2 = await async_client.post(
        f"/api/v1/rule-groups/{group_id}/rules/",
        json=rule2_data
    )
    assert create_resp2.status_code == 201

    # List rules for the group
    list_resp = await async_client.get(f"/api/v1/rule-groups/{group_id}/rules/")
    assert list_resp.status_code == 200
    list_data = list_resp.json()
    assert len(list_data) >= 2

    rules_content = {r["rule"] for r in list_data}
    assert "This is rule number 1." in rules_content
    assert "This is rule number 2." in rules_content


async def test_update_rule(async_client: AsyncClient):
    """
    Tests updating an existing rule.
    """
    playbook_id, group_id = await setup_rule_group(async_client)

    # Create a rule
    create_resp = await async_client.post(
        f"/api/v1/rule-groups/{group_id}/rules/",
        json={"rule": "Original rule content.", "rules_groups_playbook_id": group_id}
    )
    assert create_resp.status_code == 201
    rule_id = create_resp.json()["id"]

    # Update the rule
    update_data = {"rule": "Updated rule content."}
    update_resp = await async_client.put(
        f"/api/v1/rules/{rule_id}",
        json=update_data
    )
    assert update_resp.status_code == 200
    updated_data = update_resp.json()
    assert updated_data["rule"] == update_data["rule"]
    assert updated_data["id"] == rule_id

    # Verify the update by fetching the playbook and checking nested data
    get_playbook_resp = await async_client.get(f"/api/v1/playbooks/{playbook_id}")
    playbook_data = get_playbook_resp.json()
    rule_found = False
    for group in playbook_data["rules_groups"]:
        if group["id"] == group_id:
            for rule in group["rules"]:
                if rule["id"] == rule_id:
                    assert rule["rule"] == update_data["rule"]
                    rule_found = True
    assert rule_found, "Updated rule not found in nested data."


async def test_delete_rule(async_client: AsyncClient):
    """
    Tests deleting a rule.
    """
    playbook_id, group_id = await setup_rule_group(async_client)

    # Create a rule
    create_resp = await async_client.post(
        f"/api/v1/rule-groups/{group_id}/rules/",
        json={"rule": "This rule will be deleted.", "rules_groups_playbook_id": group_id}
    )
    assert create_resp.status_code == 201
    rule_id = create_resp.json()["id"]

    # Delete the rule
    delete_resp = await async_client.delete(f"/api/v1/rules/{rule_id}")
    assert delete_resp.status_code == 200
    assert delete_resp.json()["ok"] is True

    # Verify it's gone
    get_playbook_resp = await async_client.get(f"/api/v1/playbooks/{playbook_id}")
    playbook_data = get_playbook_resp.json()
    for group in playbook_data["rules_groups"]:
        if group["id"] == group_id:
            for rule in group["rules"]:
                assert rule["id"] != rule_id, "Deleted rule still found in nested data."