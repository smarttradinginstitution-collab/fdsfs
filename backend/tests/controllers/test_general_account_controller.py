# backend/tests/controllers/test_general_account_controller.py

import pytest
from httpx import AsyncClient
from uuid import uuid4

from app.Models.general_account import GeneralAccount

pytestmark = pytest.mark.anyio

async def test_create_general_account(async_client: AsyncClient):
    """
    Testa la creazione di un GeneralAccount per un utente.
    """
    response = await async_client.post("/api/v1/general-accounts/")
    assert response.status_code == 201
    data = response.json()
    assert "id" in data

    general_account_id = data["id"]

    # La seconda chiamata deve restituire lo stesso account
    response_repeat = await async_client.post("/api/v1/general-accounts/")
    assert response_repeat.status_code == 201
    data_repeat = response_repeat.json()
    assert data_repeat["id"] == general_account_id

async def test_get_my_general_account(async_client: AsyncClient):
    """
    Testa il recupero del GeneralAccount dell'utente.
    """
    create_response = await async_client.post("/api/v1/general-accounts/")
    assert create_response.status_code == 201
    created_data = create_response.json()

    get_response = await async_client.get("/api/v1/general-accounts/me")
    assert get_response.status_code == 200
    get_data = get_response.json()

    assert get_data["id"] == created_data["id"]
    assert get_data["label"] == created_data["label"]

async def test_get_my_general_account_not_found(async_client: AsyncClient):
    """
    Testa 404 se l'account non esiste.
    """
    # La fixture `async_client` usa un db pulito per ogni test, quindi non c'è account all'inizio.
    response = await async_client.get("/api/v1/general-accounts/me")
    assert response.status_code == 404


async def test_get_general_account_with_all_data(
    user_client: AsyncClient, general_account_with_data: GeneralAccount
):
    """
    Testa il recupero di un GeneralAccount con tutti i dati correlati,
    inclusi trading accounts e trades.
    """
    response = await user_client.get(
        f"/api/v1/general-account-with-data/{general_account_with_data.id}"
    )
    assert response.status_code == 200
    data = response.json()

    # Verifica i dati di base del GeneralAccount
    assert data["id"] == str(general_account_with_data.id)
    assert data["label"] == general_account_with_data.label

    # Verifica le relazioni dirette del GeneralAccount
    assert len(data["mistakes"]) == 1
    assert data["mistakes"][0]["name"] == "Test Mistake"
    assert len(data["news_impacts"]) == 1
    assert data["news_impacts"][0]["name"] == "Test News"
    assert len(data["psychology_states"]) == 1
    assert data["psychology_states"][0]["name"] == "Test State"
    assert len(data["tags_groups"]) == 1
    assert data["tags_groups"][0]["name"] == "Test Group"

    # Verifica la presenza dei Trading Accounts
    assert "trading_accounts" in data
    assert len(data["trading_accounts"]) == 1
    trading_account = data["trading_accounts"][0]
    assert trading_account["label"] == "Test Trading Account"
    assert trading_account["broker"]["name"].startswith("Test Broker Inc.")

    # Verifica la presenza dei Trades nel Trading Account
    assert "trades" in trading_account
    assert len(trading_account["trades"]) == 1
    trade = trading_account["trades"][0]
    assert trade["p_l"] == 150.75
    assert trade["direction"] == "LONG"

    # Verifica l'Asset associato al Trade
    assert "asset" in trade
    assert trade["asset"]["symbol"] == "ES"
    assert trade["asset"]["asset_class"]["name"] == "Futures"

    # Verifica le relazioni M2M del Trade
    assert len(trade["mistakes"]) == 1
    assert trade["mistakes"][0]["name"] == "Test Mistake"
    assert len(trade["tags"]) == 1
    assert trade["tags"][0]["name"] == "Tag 1"
    assert "playbook" in trade
    assert trade["playbook"] is not None
    assert trade["playbook"]["title"] == "Test Playbook"


async def test_get_general_account_with_all_data_forbidden(
    admin_client: AsyncClient, general_account_with_data: GeneralAccount
):
    """
    Testa che un utente non possa accedere ai dati di un altro utente.
    `general_account_with_data` è creato per `regular_user`, ma la chiamata
    viene fatta con `admin_client`, che non è il proprietario.
    """
    response = await admin_client.get(
        f"/api/v1/general-account-with-data/{general_account_with_data.id}"
    )
    # Anche un admin non può vedere i dati di un altro utente, a meno che non sia specificato
    assert response.status_code == 403