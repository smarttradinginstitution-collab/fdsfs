# backend/tests/controllers/test_general_account_controller.py

from fastapi.testclient import TestClient

def test_create_general_account(test_client_sync: TestClient):
    """
    Testa la creazione di un GeneralAccount per un utente.
    La prima volta dovrebbe avere successo (201 Created).
    La seconda volta dovrebbe restituire l'account esistente (200 OK, anche se il controller restituisce 201).
    """
    # Prima chiamata: creazione
    response = test_client_sync.post("/api/v1/general-accounts/")
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["label"] == "test@example.com"

    general_account_id = data["id"]

    # Seconda chiamata: deve restituire lo stesso account
    response_repeat = test_client_sync.post("/api/v1/general-accounts/")
    assert response_repeat.status_code == 201 # Il service è idempotente
    data_repeat = response_repeat.json()
    assert data_repeat["id"] == general_account_id

def test_get_my_general_account(test_client_sync: TestClient):
    """
    Testa il recupero del GeneralAccount dell'utente.
    Prima lo crea, poi lo recupera.
    """
    # 1. Crea l'account
    create_response = test_client_sync.post("/api/v1/general-accounts/")
    assert create_response.status_code == 201
    created_data = create_response.json()

    # 2. Recupera l'account
    get_response = test_client_sync.get("/api/v1/general-accounts/me")
    assert get_response.status_code == 200
    get_data = get_response.json()

    assert get_data["id"] == created_data["id"]
    assert get_data["label"] == created_data["label"]

def test_get_my_general_account_not_found(test_client_sync: TestClient):
    """
    Testa che venga restituito 404 se si cerca di recuperare un account non esistente.
    """
    # In questa sessione di test, l'utente non ha ancora un account
    # Nota: questo test deve essere eseguito con un db pulito.
    # La fixture `test_client_sync` garantisce una sessione pulita per ogni test.
    response = test_client_sync.get("/api/v1/general-accounts/me")
    assert response.status_code == 404