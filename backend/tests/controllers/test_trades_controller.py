# backend/tests/controllers/test_trades_controller.py

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.Models.tag import Tag
from app.Models.playbook import Playbook
from app.Models.mistake import Mistake
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

async def test_trade_with_m2m_relations(async_client: AsyncClient, db_session: AsyncSession):
    """Testa la creazione e l'aggiornamento di un trade con relazioni M2M (tags)."""
    trading_account_id = await setup_trading_account(async_client)

    ga_response = await async_client.get("/api/v1/general-accounts/me")
    general_account_id = uuid.UUID(ga_response.json()["id"])

    tag1 = Tag(name="FOMO", general_account_id=general_account_id)
    tag2 = Tag(name="Good Entry", general_account_id=general_account_id)
    db_session.add_all([tag1, tag2])
    await db_session.commit()

    trade_payload = {
        "trading_account_id": trading_account_id,
        "symbol": "ETHUSD",
        "tag_ids": [str(tag1.id)]
    }
    create_response = await async_client.post("/api/v1/trades/", json=trade_payload)
    assert create_response.status_code == 201
    trade_id = create_response.json()["id"]

    # Adesso verifichiamo che il trade sia stato salvato correttamente
    get_response = await async_client.get(f"/api/v1/trades/{trade_id}")
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert len(get_data["tags"]) == 1
    assert get_data["tags"][0]["name"] == "FOMO"

    update_payload = {"tag_ids": [str(tag1.id), str(tag2.id)]}
    update_response = await async_client.put(f"/api/v1/trades/{trade_id}", json=update_payload)
    assert update_response.status_code == 200

    # Verifichiamo di nuovo dopo l'aggiornamento
    get_response_after_update = await async_client.get(f"/api/v1/trades/{trade_id}")
    assert get_response_after_update.status_code == 200
    updated_data = get_response_after_update.json()
    assert len(updated_data["tags"]) == 2

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

async def test_trade_with_playbooks_and_mistakes(async_client: AsyncClient, db_session: AsyncSession):
    """Testa la creazione e l'aggiornamento di un trade con playbooks e mistakes."""
    trading_account_id = await setup_trading_account(async_client)
    ga_response = await async_client.get("/api/v1/general-accounts/me")
    general_account_id = uuid.UUID(ga_response.json()["id"])

    # Creazione di entità correlate
    playbook1 = Playbook(title="Opening Range Breakout", general_account_id=general_account_id)
    mistake1 = Mistake(name="Over-leveraged", general_account_id=general_account_id)
    db_session.add_all([playbook1, mistake1])
    await db_session.commit()

    # Creazione del trade
    trade_payload = {
        "trading_account_id": trading_account_id,
        "symbol": "SPY",
        "playbook_ids": [str(playbook1.id)],
        "mistake_ids": [str(mistake1.id)],
    }
    create_response = await async_client.post("/api/v1/trades/", json=trade_payload)
    assert create_response.status_code == 201
    trade_id = create_response.json()["id"]

    # Verifica delle relazioni leggendo il trade
    get_response = await async_client.get(f"/api/v1/trades/{trade_id}")
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert len(get_data["playbooks"]) == 1
    assert get_data["playbooks"][0]["title"] == "Opening Range Breakout"
    assert len(get_data["mistakes"]) == 1
    assert get_data["mistakes"][0]["name"] == "Over-leveraged"

    # Aggiornamento del trade per rimuovere le associazioni
    update_payload = {"playbook_ids": [], "mistake_ids": []}
    await async_client.put(f"/api/v1/trades/{trade_id}", json=update_payload)

    # Verifichiamo di nuovo dopo l'aggiornamento
    get_response_after_update = await async_client.get(f"/api/v1/trades/{trade_id}")
    assert get_response_after_update.status_code == 200
    updated_data = get_response_after_update.json()
    assert len(updated_data["playbooks"]) == 0
    assert len(updated_data["mistakes"]) == 0