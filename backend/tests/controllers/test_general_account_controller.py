# backend/tests/controllers/test_general_account_controller.py

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.anyio

async def test_create_general_account(async_client: AsyncClient):
    """
    Testa la creazione di un GeneralAccount per un utente.
    """
    response = await async_client.post("/api/v1/general-accounts/")
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["label"] == "test@example.com"

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