# backend/tests/controllers/test_trades_controller.py

import pytest
from httpx import AsyncClient
import uuid
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.Models import Broker

pytestmark = pytest.mark.anyio

async def setup_broker(db_session: AsyncSession) -> str:
    """Helper to create a broker and return its ID."""
    broker = Broker(name=f"Test Broker {uuid.uuid4()}")
    db_session.add(broker)
    await db_session.commit()
    await db_session.refresh(broker)
    return str(broker.id)

async def setup_trading_account(client: AsyncClient, db_session: AsyncSession) -> str:
    """Helper per creare un General e un Trading Account e restituire l'ID di quest'ultimo."""
    await client.post("/api/v1/general-accounts/")
    broker_id = await setup_broker(db_session)
    response = await client.post(
        "/api/v1/trading-accounts/",
        json={
            "label": "Test Trading Account",
            "broker_id": broker_id,
            "initial_balance": 100000,
            "currency": "USD"
        }
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]

async def test_create_trade_fails_without_trading_account(async_client: AsyncClient):
    """Testa che la creazione di un trade fallisca se il trading account non esiste."""
    response = await async_client.post(
        "/api/v1/trades/",
        json={"trading_account_id": str(uuid.uuid4()), "symbol_snapshot": "EURUSD", "status": "closed", "direction": "LONG"}
    )
    assert response.status_code == 404

async def test_create_and_get_trade(async_client: AsyncClient, db_session: AsyncSession):
    """Testa la creazione e il recupero di un trade semplice."""
    trading_account_id = await setup_trading_account(async_client, db_session)

    trade_payload = {
        "trading_account_id": trading_account_id,
        "symbol_snapshot": "BTCUSD",
        "direction": "LONG",
        "status": "closed",
        "entry_price": 50000,
        "exit_price": 51000,
        "p_l": 1000
    }

    create_response = await async_client.post("/api/v1/trades/", json=trade_payload)
    assert create_response.status_code == 201
    created_data = create_response.json()
    trade_id = created_data["id"]

    assert created_data["symbol_snapshot"] == "BTCUSD"

    get_response = await async_client.get(f"/api/v1/trades/{trade_id}")
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["id"] == trade_id

    list_response = await async_client.get(f"/api/v1/trades/by-trading-account/{trading_account_id}")
    assert list_response.status_code == 200
    list_data = list_response.json()
    assert len(list_data) == 1

async def test_create_trade_with_related_entities_by_name(async_client: AsyncClient, db_session: AsyncSession):
    """
    Testa la creazione di un trade con entità correlate (tags, mistakes, playbooks)
    passando i loro nomi come stringhe, come farebbe il frontend.
    """
    trading_account_id = await setup_trading_account(async_client, db_session)

    trade_payload = {
        "trading_account_id": trading_account_id,
        "symbol_snapshot": "ETHUSD",
        "status": "closed",
        "direction": "SHORT",
        "tags": ["Good Entry", "News-Driven"],
        "mistakes": ["FOMO"],
        "playbooks": ["Opening Range Breakout"]
    }
    create_response = await async_client.post("/api/v1/trades/", json=trade_payload)
    assert create_response.status_code == 201
    created_trade = create_response.json()

    assert len(created_trade["tags"]) == 2
    returned_tags = {tag['name'] for tag in created_trade['tags']}
    assert returned_tags == {"Good Entry", "News-Driven"}

    assert len(created_trade["mistakes"]) == 1
    assert created_trade["mistakes"][0]["name"] == "FOMO"

    assert len(created_trade["playbooks"]) == 1
    assert created_trade["playbooks"][0]["name"] == "Opening Range Breakout"

    trade_payload_2 = {
        "trading_account_id": trading_account_id,
        "symbol_snapshot": "SOLUSD",
        "tags": ["Good Entry"],
        "status": "closed",
        "direction": "LONG"
    }
    create_response_2 = await async_client.post("/api/v1/trades/", json=trade_payload_2)
    assert create_response_2.status_code == 201
    created_trade_2 = create_response_2.json()
    assert len(created_trade_2["tags"]) == 1

    good_entry_tag_from_trade1 = next(t for t in created_trade['tags'] if t['name'] == 'Good Entry')
    good_entry_tag_from_trade2 = created_trade_2['tags'][0]

    assert good_entry_tag_from_trade2['id'] == good_entry_tag_from_trade1['id']


async def test_delete_trade(async_client: AsyncClient, db_session: AsyncSession):
    """Testa l'eliminazione di un trade."""
    trading_account_id = await setup_trading_account(async_client, db_session)
    trade_payload = {"trading_account_id": trading_account_id, "symbol_snapshot": "ADAUSD", "status": "closed", "direction": "LONG"}
    create_response = await async_client.post("/api/v1/trades/", json=trade_payload)
    assert create_response.status_code == 201
    trade_id = create_response.json()["id"]

    delete_response = await async_client.delete(f"/api/v1/trades/{trade_id}")
    assert delete_response.status_code == 204

    get_response = await async_client.get(f"/api/v1/trades/{trade_id}")
    assert get_response.status_code == 404

async def test_list_trades_with_date_filter(async_client: AsyncClient, db_session: AsyncSession):
    """Testa che il filtro per data sull'endpoint di elenco dei trade funzioni correttamente."""
    trading_account_id = await setup_trading_account(async_client, db_session)
    today = date.today()
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)

    # Crea tre trade in giorni diversi
    await async_client.post("/api/v1/trades/", json={"trading_account_id": trading_account_id, "symbol_snapshot": "YESTERDAY_TRADE", "entry_timestamp": yesterday.isoformat(), "status": "closed", "direction": "LONG"})
    await async_client.post("/api/v1/trades/", json={"trading_account_id": trading_account_id, "symbol_snapshot": "TODAY_TRADE", "entry_timestamp": today.isoformat(), "status": "closed", "direction": "LONG"})
    await async_client.post("/api/v1/trades/", json={"trading_account_id": trading_account_id, "symbol_snapshot": "TOMORROW_TRADE", "entry_timestamp": tomorrow.isoformat(), "status": "closed", "direction": "LONG"})

    # 1. Testa con il filtro per data (solo oggi)
    response_filtered = await async_client.get(
        f"/api/v1/trades/by-trading-account/{trading_account_id}",
        params={"start_date": today.isoformat(), "end_date": today.isoformat()}
    )
    assert response_filtered.status_code == 200
    filtered_data = response_filtered.json()
    assert len(filtered_data) == 1
    assert filtered_data[0]["symbol_snapshot"] == "TODAY_TRADE"

    # 2. Testa senza filtro per data (tutti i trade)
    response_unfiltered = await async_client.get(f"/api/v1/trades/by-trading-account/{trading_account_id}")
    assert response_unfiltered.status_code == 200
    unfiltered_data = response_unfiltered.json()
    assert len(unfiltered_data) == 3