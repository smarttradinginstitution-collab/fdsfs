import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from decimal import Decimal
from datetime import datetime, timezone
from uuid import uuid4

# Importa l'app FastAPI e le dipendenze da mockare
from app.main import app
from app.Models.trade import Trade
from app.Repositories.trade_repository import TradeRepository
from app.Infrastructure.db import get_db
from app.Router.auth import get_current_claims

# Mock del trade che verrà restituito dal repository
# Questo timestamp è alle 23:30 UTC del 26 Ottobre 2023.
# In 'Europe/Rome' (UTC+2), è già il 27 Ottobre.
utc_entry_time = datetime(2023, 10, 26, 23, 30, 0, tzinfo=timezone.utc)
mock_user_id = uuid4()
mock_trade_orm = Trade(
    id=uuid4(),
    user_id=mock_user_id,
    p_l=Decimal("150.00"),
    entry_timestamp=utc_entry_time,
    exit_timestamp=utc_entry_time,
    created_at=utc_entry_time,
    setup="Test"
)

# Funzione per simulare la risposta del repository
async def mock_list_with_filters(*args, **kwargs):
    return [(mock_trade_orm, [])]

# Fixture per il client di test
@pytest.fixture
def test_client():
    """
    Crea un client di test per l'app FastAPI, sovrascrivendo le dipendenze
    del database e dell'autenticazione per isolare il test.
    """
    # Funzione di override per la dipendenza del database
    async def override_get_db():
        # Non abbiamo bisogno di una vera sessione DB, il repository è mockato
        yield None

    # Funzione di override per la dipendenza di autenticazione
    async def override_get_current_claims():
        # Ritorna un payload di claims fittizio per superare il controllo dei ruoli
        return {"sub": str(mock_user_id), "roles": ["member"]}

    # Applica gli override delle dipendenze
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_claims] = override_get_current_claims

    # Mocka il metodo del repository a livello di classe prima di creare il client
    # Questo assicura che qualsiasi istanza di TradeRepository usi il nostro mock
    original_list_with_filters = TradeRepository.list_with_filters
    TradeRepository.list_with_filters = AsyncMock(side_effect=mock_list_with_filters)

    with TestClient(app) as client:
        yield client

    # Ripristina lo stato originale dopo il test
    app.dependency_overrides.clear()
    TradeRepository.list_with_filters = original_list_with_filters


def test_get_processed_stats_with_timezone(test_client):
    """
    Test di integrazione per l'endpoint /api/v1/trades/processed-stats
    Verifica che il raggruppamento giornaliero avvenga correttamente secondo il fuso orario.
    """
    user_timezone = "Europe/Rome"
    expected_local_date = "2023-10-27"

    # Aggiunto il prefisso /api/v1 all'URL
    response = test_client.get(
        f"/api/v1/trades/processed-stats?user_id={mock_user_id}&user_timezone={user_timezone}"
    )

    assert response.status_code == 200, f"Test fallito con status {response.status_code} e body: {response.text}"
    data = response.json()

    # Verifica che la risposta contenga la sezione 'daily_data'
    assert "daily_data" in data

    # Verifica che ci sia una chiave per la data locale corretta (27/10)
    assert expected_local_date in data["daily_data"]

    # Verifica che non ci sia una chiave per la data UTC (26/10)
    assert "2023-10-26" not in data["daily_data"]

    # Verifica che i dati aggregati per quel giorno siano corretti
    day_stats = data["daily_data"][expected_local_date]
    assert day_stats["total_pnl"] == float(mock_trade_orm.p_l)
    assert day_stats["trade_count"] == 1
    assert day_stats["winning_trades"] == 1
