# backend/tests/controllers/test_general_account_controller.py

import pytest
from httpx import AsyncClient
from uuid import uuid4

from app.Models.general_account import GeneralAccount

pytestmark = pytest.mark.anyio

async def test_create_general_account_and_idempotency(async_client: AsyncClient):
    """
    Testa la creazione di un GeneralAccount, la creazione dei dati di default
    e l'idempotenza della chiamata.
    """
    # 1. Prima chiamata: Crea il GeneralAccount e i dati di default
    response1 = await async_client.post("/api/v1/general-accounts/")
    assert response1.status_code == 201
    account1_data = response1.json()
    general_account_id = account1_data["id"]

    # Verifica che i dati siano stati creati
    assert "tags_groups" in account1_data
    groups = account1_data["tags_groups"]
    assert len(groups) == 4
    assert sum(len(g["tags"]) for g in groups) == 18

    # 2. Seconda chiamata: Dovrebbe restituire l'account esistente con status 200
    response2 = await async_client.post("/api/v1/general-accounts/")
    assert response2.status_code == 200
    account2_data = response2.json()
    assert account2_data["id"] == general_account_id

    # Verifica che non siano stati creati dati duplicati
    assert "tags_groups" in account2_data
    groups2 = account2_data["tags_groups"]
    assert len(groups2) == 4
    assert sum(len(g["tags"]) for g in groups2) == 18

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
    Testa il recupero di un GeneralAccount con tutti i dati correlati.
    """
    response = await user_client.get(
        f"/api/v1/general-account-with-data/{general_account_with_data.id}"
    )
    assert response.status_code == 200
    data = response.json()

    # Verifica i dati di base
    assert data["id"] == str(general_account_with_data.id)
    assert data["label"] == general_account_with_data.label

    # Verifica le relazioni nidificate
    assert len(data["mistakes"]) == 1
    assert data["mistakes"][0]["name"] == "Test Mistake"

    assert len(data["news_impacts"]) == 1
    assert data["news_impacts"][0]["name"] == "Test News"

    assert len(data["psychology_states"]) == 1
    assert data["psychology_states"][0]["name"] == "Test State"

    assert len(data["tags_groups"]) == 1
    group = data["tags_groups"][0]
    assert group["name"] == "Test Group"

    assert len(group["tags"]) == 2
    tag_names = {tag["name"] for tag in group["tags"]}
    assert tag_names == {"Tag 1", "Tag 2"}


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