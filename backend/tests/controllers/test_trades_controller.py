# backend/tests/controllers/test_trades_controller.py

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.Models.tag import Tag
import uuid

def setup_trading_account(client: TestClient) -> str:
    """Helper per creare un General e un Trading Account e restituire l'ID di quest'ultimo."""
    client.post("/api/v1/general-accounts/")
    response = client.post("/api/v1/trading-accounts/", json={"label": "Test Trading Account"})
    return response.json()["id"]

def test_create_trade_fails_without_trading_account(test_client_sync: TestClient):
    """Testa che la creazione di un trade fallisca se il trading account non esiste."""
    response = test_client_sync.post(
        "/api/v1/trades/",
        json={"trading_account_id": str(uuid.uuid4()), "symbol": "EURUSD"}
    )
    assert response.status_code == 404

def test_create_and_get_trade(test_client_sync: TestClient):
    """Testa la creazione e il recupero di un trade semplice."""
    trading_account_id = setup_trading_account(test_client_sync)

    trade_payload = {
        "trading_account_id": trading_account_id,
        "symbol": "BTCUSD",
        "direction": "Long",
        "entry_price": 50000,
        "exit_price": 51000,
        "p_l": 1000
    }

    # Crea il trade
    create_response = test_client_sync.post("/api/v1/trades/", json=trade_payload)
    assert create_response.status_code == 201
    created_data = create_response.json()
    trade_id = created_data["id"]

    assert created_data["symbol"] == "BTCUSD"
    assert created_data["p_l"] == 1000

    # Recupera il trade
    get_response = test_client_sync.get(f"/api/v1/trades/{trade_id}")
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["id"] == trade_id
    assert get_data["symbol"] == "BTCUSD"

    # Recupera la lista dei trade per l'account
    list_response = test_client_sync.get(f"/api/v1/trades/by-trading-account/{trading_account_id}")
    assert list_response.status_code == 200
    list_data = list_response.json()
    assert len(list_data) == 1
    assert list_data[0]["id"] == trade_id

def test_trade_with_m2m_relations(test_client_sync: TestClient, db_session_sync: Session):
    """Testa la creazione e l'aggiornamento di un trade con relazioni M2M (tags)."""
    trading_account_id = setup_trading_account(test_client_sync)

    # Ottieni il general_account_id per creare i tag
    ga_response = test_client_sync.get("/api/v1/general-accounts/me")
    general_account_id = ga_response.json()["id"]

    # Crea dei tag per l'utente
    tag1 = Tag(name="FOMO", general_account_id=general_account_id)
    tag2 = Tag(name="Good Entry", general_account_id=general_account_id)
    db_session_sync.add_all([tag1, tag2])
    db_session_sync.commit()

    # 1. Crea un trade con un tag
    trade_payload = {
        "trading_account_id": trading_account_id,
        "symbol": "ETHUSD",
        "tag_ids": [str(tag1.id)]
    }
    create_response = test_client_sync.post("/api/v1/trades/", json=trade_payload)
    assert create_response.status_code == 201
    created_data = create_response.json()
    trade_id = created_data["id"]

    assert len(created_data["tags"]) == 1
    assert created_data["tags"][0]["name"] == "FOMO"

    # 2. Aggiorna il trade per avere entrambi i tag
    update_payload = {"tag_ids": [str(tag1.id), str(tag2.id)]}
    update_response = test_client_sync.put(f"/api/v1/trades/{trade_id}", json=update_payload)
    assert update_response.status_code == 200
    updated_data = update_response.json()
    assert len(updated_data["tags"]) == 2

    # 3. Aggiorna il trade per rimuovere tutti i tag
    update_payload_empty = {"tag_ids": []}
    update_empty_response = test_client_sync.put(f"/api/v1/trades/{trade_id}", json=update_payload_empty)
    assert update_empty_response.status_code == 200
    updated_empty_data = update_empty_response.json()
    assert len(updated_empty_data["tags"]) == 0

def test_delete_trade(test_client_sync: TestClient):
    """Testa l'eliminazione di un trade."""
    trading_account_id = setup_trading_account(test_client_sync)
    trade_payload = {"trading_account_id": trading_account_id, "symbol": "ADAUSD"}
    create_response = test_client_sync.post("/api/v1/trades/", json=trade_payload)
    trade_id = create_response.json()["id"]

    # Elimina il trade
    delete_response = test_client_sync.delete(f"/api/v1/trades/{trade_id}")
    assert delete_response.status_code == 204

    # Verifica che non sia più recuperabile
    get_response = test_client_sync.get(f"/api/v1/trades/{trade_id}")
    assert get_response.status_code == 404