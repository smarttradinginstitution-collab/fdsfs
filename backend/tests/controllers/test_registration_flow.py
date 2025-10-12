# backend/tests/controllers/test_registration_flow.py

import pytest
from httpx import AsyncClient
from uuid import uuid4

pytestmark = pytest.mark.anyio

async def test_full_registration_and_default_data_creation(async_client: AsyncClient):
    """
    Tests the full user registration flow and verifies the creation of a
    general_account with all default tags and tag groups.
    """
    # This test uses the 'async_client' which is already authenticated
    # for a new, unique user in each test run, thanks to the conftest setup.
    # Therefore, we can proceed directly to creating the general account.

    # 1. Create the GeneralAccount, which should trigger default data creation
    response_create = await async_client.post("/api/v1/general-accounts/")
    assert response_create.status_code == 201
    account_data = response_create.json()
    general_account_id = account_data["id"]

    # 2. Fetch the account with all its nested data
    response_get = await async_client.get(
        f"/api/v1/general-account-with-data/{general_account_id}"
    )
    assert response_get.status_code == 200
    account_with_data = response_get.json()

    # 3. Verify the structure of the default data
    assert "tags_groups" in account_with_data
    groups = account_with_data["tags_groups"]
    assert len(groups) == 4, "Should create exactly 4 tag groups"

    expected_structure = {
        "Setup": {
            "description": "The chart pattern or technical setup that initiated the trade.",
            "position": 1,
            "tags": ["Breakout", "Reversal", "Continuation", "Fakeout"],
        },
        "Market Context": {
            "description": "The overall market conditions at the time of the trade.",
            "position": 2,
            "tags": ["Trending Market", "Ranging Market", "High Volatility", "Low Volume"],
        },
        "Execution": {
            "description": "How you actively managed the entry, position, and exit.",
            "position": 3,
            "tags": ["Scaled In", "Took Partials", "Moved to Breakeven", "All In / All Out"],
        },
        "Timeframe": {
            "description": "The primary timeframe used for the trade analysis.",
            "position": 4,
            "tags": ["1m", "5m", "15m", "1h", "Daily"],
        },
    }

    # Sort groups by position to ensure deterministic order for comparison
    groups.sort(key=lambda x: x['position'])

    for i, group in enumerate(groups):
        expected_group_name = list(expected_structure.keys())[i]
        expected_group_data = expected_structure[expected_group_name]

        assert group["name"] == expected_group_name
        assert group["description"] == expected_group_data["description"]
        assert group["position"] == expected_group_data["position"]
        assert group["color"] == "#888888"

        actual_tags = sorted([tag["name"] for tag in group["tags"]])
        expected_tags = sorted(expected_group_data["tags"])
        assert actual_tags == expected_tags, f"Tags for group '{expected_group_name}' do not match"

        for tag in group["tags"]:
            assert tag["color"] == "#888888"