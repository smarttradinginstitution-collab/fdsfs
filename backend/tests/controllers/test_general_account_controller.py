# backend/tests/controllers/test_general_account_controller.py

import pytest
from httpx import AsyncClient
from uuid import uuid4

from app.Models.general_account import GeneralAccount

pytestmark = pytest.mark.anyio


async def test_create_general_account_with_default_data(async_client: AsyncClient):
    """
    Testa la creazione di un GeneralAccount per un utente e verifica che i
    gruppi di tag e i tag di default siano stati creati correttamente.
    """
    # 1. Crea il GeneralAccount
    response = await async_client.post("/api/v1/general-accounts/")
    assert response.status_code == 201  # Deve essere una nuova creazione
    data = response.json()
    assert "id" in data
    general_account_id = data["id"]

    # 2. Verifica che una seconda chiamata non crei un nuovo account (idempotenza)
    response_repeat = await async_client.post("/api/v1/general-accounts/")
    assert response_repeat.status_code in [200, 201]  # OK or CREATED
    data_repeat = response_repeat.json()
    assert data_repeat["id"] == general_account_id

    # 3. Recupera i dati completi dell'account per verificare i dati predefiniti
    response_full_data = await async_client.get(
        f"/api/v1/general-account-with-data/{general_account_id}"
    )
    assert response_full_data.status_code == 200
    account_data = response_full_data.json()

    # 4. Verifica i gruppi di tag e i tag
    assert "tags_groups" in account_data
    groups = account_data["tags_groups"]
    assert len(groups) == 4

    # Ordina i gruppi per posizione per un controllo deterministico
    groups.sort(key=lambda x: x["position"])

    # Gruppo 1: Setup
    assert groups[0]["name"] == "Setup"
    assert groups[0]["position"] == 1
    assert len(groups[0]["tags"]) == 4
    tag_names_setup = {tag["name"] for tag in groups[0]["tags"]}
    assert tag_names_setup == {"Breakout", "Reversal", "Continuation", "Fakeout"}

    # Gruppo 2: Market Context
    assert groups[1]["name"] == "Market Context"
    assert groups[1]["position"] == 2
    assert len(groups[1]["tags"]) == 4
    tag_names_context = {tag["name"] for tag in groups[1]["tags"]}
    assert tag_names_context == {
        "Trending Market",
        "Ranging Market",
        "High Volatility",
        "Low Volume",
    }

    # Gruppo 3: Execution
    assert groups[2]["name"] == "Execution"
    assert groups[2]["position"] == 3
    assert len(groups[2]["tags"]) == 4
    tag_names_execution = {tag["name"] for tag in groups[2]["tags"]}
    assert tag_names_execution == {
        "Scaled In",
        "Took Partials",
        "Moved to Breakeven",
        "All In / All Out",
    }

    # Gruppo 4: Timeframe
    assert groups[3]["name"] == "Timeframe"
    assert groups[3]["position"] == 4
    assert len(groups[3]["tags"]) == 5
    tag_names_timeframe = {tag["name"] for tag in groups[3]["tags"]}
    assert tag_names_timeframe == {"1m", "5m", "15m", "1h", "Daily"}


async def test_create_general_account_idempotency(async_client: AsyncClient):
    """
    Testa che la creazione di un GeneralAccount sia idempotente e non duplichi
    i dati predefiniti.
    """
    # Crea l'account la prima volta
    await async_client.post("/api/v1/general-accounts/")

    # Eseguilo di nuovo
    await async_client.post("/api/v1/general-accounts/")

    # Recupera i dati e verifica che non ci siano duplicati
    response = await async_client.get("/api/v1/general-accounts/me")
    account_id = response.json()["id"]

    response_full_data = await async_client.get(
        f"/api/v1/general-account-with-data/{account_id}"
    )
    account_data = response_full_data.json()

    assert len(account_data["tags_groups"]) == 4
    assert sum(len(g["tags"]) for g in account_data["tags_groups"]) == (4 + 4 + 4 + 5)

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