# backend/tests/integration/test_import_flow.py
import pytest
import io
from uuid import uuid4

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.main import app
from app.Models.trade import Trade
from app.Models.auth_user import AuthUser
from app.Router.auth import get_current_claims
from app.Infrastructure.db import get_db

# Dati di esempio per i test
VALID_CSV_CONTENT = """Trade #,Tipo,Data/Ora,Segnale,Prezzo USD,Dimensione posizione (quantità),Dimensione posizione (valore),P&L Netto USD,P&L Netto %,Massimale USD,Massimale %,Drawdown USD,Drawdown %,P&L cumulativo USD,P&L cumulativo %
1,Entrata long,01.01.2023 10:00:00,SignalA,150.00,10,1500.00,50.00,3.33,60.00,4.00,-10.00,-0.67,50.00,3.33
1,Uscita long,01.01.2023 11:00:00,SignalA,155.00,10,1550.00,50.00,3.33,60.00,4.00,-10.00,-0.67,50.00,3.33
2,Entrata short,02.01.2023 14:00:00,SignalB,200.00,5,1000.00,-25.00,-2.50,5.00,0.50,-30.00,-3.00,25.00,1.25
2,Uscita short,02.01.2023 15:00:00,SignalB,195.00,5,975.00,-25.00,-2.50,5.00,0.50,-30.00,-3.00,25.00,1.25
"""

@pytest.mark.anyio
async def test_import_csv_flow(async_client: AsyncClient, db_session: AsyncSession):
    """
    Testa l'intero flusso di importazione CSV:
    1. Importa un file valido e verifica la creazione dei trade.
    2. Importa lo stesso file di nuovo e verifica che i duplicati vengano ignorati.
    """
    mock_user_id = uuid4()

    # Override delle dipendenze per usare il db di test e un utente mockato
    async def override_get_db():
        yield db_session

    async def override_get_current_claims():
        return {"sub": str(mock_user_id), "roles": ["member"]}

    app.dependency_overrides[get_current_claims] = override_get_current_claims
    app.dependency_overrides[get_db] = override_get_db

    # Crea un utente nel DB di test per soddisfare il foreign key constraint
    test_user = AuthUser(id=mock_user_id, email=f"testuser_{mock_user_id}@test.com", is_sso_user=False, is_anonymous=False)
    db_session.add(test_user)
    await db_session.commit()


    # --- 1. Prima importazione (creazione) ---
    files = {"file": ("test_import_NQ1!_data.csv", io.BytesIO(VALID_CSV_CONTENT.encode("utf-8")), "text/csv")}
    response = await async_client.post(
        f"/api/v1/trades/import-csv?user_id={mock_user_id}",
        files=files
    )

    # Verifica la risposta
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["summary"]["new_trades_imported"] == 2
    assert json_response["summary"]["duplicate_trades_skipped"] == 0
    assert json_response["summary"]["errors_found"] == 0

    # Verifica il database
    stmt = select(Trade).where(Trade.user_id == mock_user_id)
    result = await db_session.execute(stmt)
    trades_in_db = result.scalars().all()
    assert len(trades_in_db) == 2
    external_ids_in_db = {t.external_id for t in trades_in_db}
    assert external_ids_in_db == {"1", "2"}

    # --- 2. Seconda importazione (duplicati) ---
    files = {"file": ("test_import_NQ1!_data.csv", io.BytesIO(VALID_CSV_CONTENT.encode("utf-8")), "text/csv")}
    response_duplicate = await async_client.post(
        f"/api/v1/trades/import-csv?user_id={mock_user_id}",
        files=files
    )

    # Verifica la risposta
    assert response_duplicate.status_code == 200
    json_response_dup = response_duplicate.json()
    assert json_response_dup["summary"]["new_trades_imported"] == 0
    assert json_response_dup["summary"]["duplicate_trades_skipped"] == 2
    assert json_response_dup["summary"]["errors_found"] == 0

    # Verifica che il database non sia cambiato
    result_after_dup = await db_session.execute(stmt)
    trades_in_db_after_dup = result_after_dup.scalars().all()
    assert len(trades_in_db_after_dup) == 2

    # Cleanup
    app.dependency_overrides.clear()
