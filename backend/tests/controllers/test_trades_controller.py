# backend/tests/controllers/test_trades_controller.py

import pytest
from httpx import AsyncClient
import uuid

pytestmark = pytest.mark.anyio

async def setup_trading_account(client: AsyncClient) -> str:
    """Helper per creare un General e un Trading Account e restituire l'ID di quest'ultimo."""
    await client.post("/api/v1/general-accounts/")
    response = await client.post("/api/v1/trading-accounts/", json={"label": "Test Trading Account"})
    return response.json()["id"]

async def test_create_trade_fails_without_trading_account(async_client: AsyncClient):
    """Testa che la creazione di un trade fallisca se il trading account non esiste."""
    response = await async_client.post(
        "/api/v1/trades/",
        json={"trading_account_id": str(uuid.uuid4()), "symbol": "EURUSD"}
    )
    assert response.status_code == 404

async def test_create_and_get_trade(async_client: AsyncClient):
    """Testa la creazione e il recupero di un trade semplice."""
    trading_account_id = await setup_trading_account(async_client)

    trade_payload = {
        "trading_account_id": trading_account_id,
        "symbol": "BTCUSD",
        "direction": "Long",
        "entry_price": 50000,
        "exit_price": 51000,
        "p_l": 1000
    }

    create_response = await async_client.post("/api/v1/trades/", json=trade_payload)
    assert create_response.status_code == 201
    created_data = create_response.json()
    trade_id = created_data["id"]

    assert created_data["symbol"] == "BTCUSD"

    get_response = await async_client.get(f"/api/v1/trades/{trade_id}")
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["id"] == trade_id

    list_response = await async_client.get(f"/api/v1/trades/by-trading-account/{trading_account_id}")
    assert list_response.status_code == 200
    list_data = list_response.json()
    assert len(list_data) == 1

async def test_create_trade_with_related_entities_by_name(async_client: AsyncClient):
    """
    Testa la creazione di un trade con entità correlate (tags, mistakes, playbooks)
    passando i loro nomi come stringhe, come farebbe il frontend.
    """
    trading_account_id = await setup_trading_account(async_client)

    trade_payload = {
        "trading_account_id": trading_account_id,
        "symbol": "ETHUSD",
        "tags": ["Good Entry", "News-Driven"],
        "mistakes": ["FOMO"],
        "playbooks": ["Opening Range Breakout"]
    }
    create_response = await async_client.post("/api/v1/trades/", json=trade_payload)
    assert create_response.status_code == 201
    created_trade = create_response.json()
    trade_id = created_trade["id"]

    # Verifica che le entità siano state create e associate
    assert len(created_trade["tags"]) == 2
    returned_tags = {tag['name'] for tag in created_trade['tags']}
    assert returned_tags == {"Good Entry", "News-Driven"}

    assert len(created_trade["mistakes"]) == 1
    assert created_trade["mistakes"][0]["name"] == "FOMO"

    assert len(created_trade["playbooks"]) == 1
    assert created_trade["playbooks"][0]["title"] == "Opening Range Breakout"

    # Verifica che una richiesta successiva con gli stessi nomi non crei duplicati
    trade_payload_2 = {
        "trading_account_id": trading_account_id,
        "symbol": "SOLUSD",
        "tags": ["Good Entry"],
    }
    create_response_2 = await async_client.post("/api/v1/trades/", json=trade_payload_2)
    assert create_response_2.status_code == 201
    created_trade_2 = create_response_2.json()
    assert len(created_trade_2["tags"]) == 1

    # L'ID del tag "Good Entry" dovrebbe essere lo stesso del primo trade,
    # verificando che l'upsert non abbia creato un duplicato.
    good_entry_tag_from_trade1 = next(t for t in created_trade['tags'] if t['name'] == 'Good Entry')
    good_entry_tag_from_trade2 = created_trade_2['tags'][0]

    assert good_entry_tag_from_trade2['id'] == good_entry_tag_from_trade1['id']


async def test_delete_trade(async_client: AsyncClient):
    """Testa l'eliminazione di un trade."""
    trading_account_id = await setup_trading_account(async_client)
    trade_payload = {"trading_account_id": trading_account_id, "symbol": "ADAUSD"}
    create_response = await async_client.post("/api/v1/trades/", json=trade_payload)
    trade_id = create_response.json()["id"]

    delete_response = await async_client.delete(f"/api/v1/trades/{trade_id}")
    assert delete_response.status_code == 204

    get_response = await async_client.get(f"/api/v1/trades/{trade_id}")
    assert get_response.status_code == 404