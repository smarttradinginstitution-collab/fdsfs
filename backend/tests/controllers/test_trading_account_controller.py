# backend/tests/controllers/test_trading_account_controller.py

import pytest
from httpx import AsyncClient
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.Models import Broker

pytestmark = pytest.mark.anyio

async def setup_broker(db_session: AsyncSession) -> uuid.UUID:
    """Helper function to create a broker for tests."""
    broker = Broker(name=f"Test Broker {uuid.uuid4()}")
    db_session.add(broker)
    await db_session.commit()
    await db_session.refresh(broker)
    return broker.id

async def test_create_trading_account_fails_without_general_account(async_client: AsyncClient, db_session: AsyncSession):
    """
    Testa che la creazione di un TradingAccount fallisca se non esiste un GeneralAccount.
    """
    broker_id = await setup_broker(db_session)
    response = await async_client.post(
        "/api/v1/trading-accounts/",
        json={
            "label": "My First Trading Account",
            "broker_id": str(broker_id),
            "initial_balance": 100000,
            "currency": "USD"
        }
    )
    assert response.status_code == 403

async def test_create_and_get_trading_account(async_client: AsyncClient, db_session: AsyncSession):
    """
    Testa la creazione e il recupero di un TradingAccount.
    """
    # 1. Crea un GeneralAccount
    ga_response = await async_client.post("/api/v1/general-accounts/")
    assert ga_response.status_code == 201

    # 1.5 Create a Broker to associate with the Trading Account
    broker_id = await setup_broker(db_session)

    # 2. Crea un TradingAccount
    label = "My Test Account"
    ta_response = await async_client.post(
        "/api/v1/trading-accounts/",
        json={
            "label": label,
            "broker_id": str(broker_id),
            "initial_balance": 100000,
            "currency": "USD"
        }
    )
    assert ta_response.status_code == 201
    data = ta_response.json()
    assert data["label"] == label
    assert data["broker_id"] == str(broker_id)

    trading_account_id = data["id"]

    # 3. Recupera il TradingAccount tramite GET /
    list_response = await async_client.get("/api/v1/trading-accounts/")
    assert list_response.status_code == 200
    list_data = list_response.json()
    assert isinstance(list_data, list)
    assert len(list_data) == 1
    assert list_data[0]["id"] == trading_account_id
    assert list_data[0]["label"] == label

    # 4. Recupera il TradingAccount tramite GET /{id}
    get_response = await async_client.get(f"/api/v1/trading-accounts/{trading_account_id}")
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["id"] == trading_account_id
    assert get_data["label"] == label

async def test_get_trading_account_not_found(async_client: AsyncClient):
    """
    Testa che il recupero di un trading account inesistente restituisca 404.
    """
    random_id = uuid.uuid4()
    response = await async_client.get(f"/api/v1/trading-accounts/{random_id}")
    assert response.status_code == 404