# backend/tests/controllers/test_import_controller.py
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from sqlalchemy import select

from app.Models.trade import Trade
from app.Models.broker import Broker

# Mark all tests in this module as asyncio
pytestmark = pytest.mark.asyncio

async def setup_broker(db_session: AsyncSession) -> str:
    """Helper to create a broker and return its ID."""
    broker = Broker(name=f"Test Broker {uuid.uuid4()}")
    db_session.add(broker)
    await db_session.commit()
    await db_session.refresh(broker)
    return str(broker.id)

async def setup_trading_account(client: AsyncClient, db_session: AsyncSession) -> str:
    """Helper per creare un General e un Trading Account e restituire l'ID di quest'ultimo."""
    await client.post("/api/v1/general-accounts/")
    broker_id = await setup_broker(db_session)
    response = await client.post(
        "/api/v1/trading-accounts/",
        json={
            "label": "Test Trading Account",
            "broker_id": broker_id,
            "initial_balance": 100000,
            "currency": "USD"
        }
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]

@pytest.fixture
def valid_csv_content():
    return """
symbol,_priceFormat,_priceFormatType,_tickSize,buyFillId,sellFillId,qty,buyPrice,sellPrice,pnl,boughtTimestamp,soldTimestamp,duration
NQZ5,-2,0,0.25,1,2,1,24861.0,24878.0,$340.00,09/22/2025 15:50:36,09/22/2025 15:54:58,4min 21sec
    """.strip().encode('utf-8')

async def test_import_tradovate_success(async_client: AsyncClient, db_session: AsyncSession, valid_csv_content, mocker):
    """
    Testa che il controller per l'import di Tradovate crei correttamente la ImportRun
    e accodi il task Celery.
    """
    mocker.patch("app.Controllers.import_controller.upload_import_file", return_value="mock/path/performance.csv")
    mock_delay = mocker.patch("app.Controllers.import_controller.process_import_task.delay")

    trading_account_id = await setup_trading_account(async_client, db_session)

    files = {'file': ('performance.csv', valid_csv_content, 'text/csv')}

    response = await async_client.post(
        f"/api/v1/import/tradovate/{trading_account_id}",
        files=files
    )

    # CORREZIONE: Lo status corretto è 202 Accepted
    assert response.status_code == 202
    import_run_data = response.json()
    assert import_run_data['status'] == 'queued'
    assert import_run_data['trading_account_id'] == str(trading_account_id)
    assert "performance.csv" in import_run_data['file_name']

    mock_delay.assert_called_once()
    args, _ = mock_delay.call_args
    assert args[0] == import_run_data['id']
    assert args[1] == "mock/path/performance.csv"
    assert args[2] == "tradovate"

async def test_import_tradovate_fails_with_invalid_file(async_client: AsyncClient, db_session: AsyncSession):
    """
    Testa che l'import fallisca se viene caricato un file non CSV.
    """
    trading_account_id = await setup_trading_account(async_client, db_session)
    files = {'file': ('report.txt', b'some,content', 'text/plain')}

    response = await async_client.post(
        f"/api/v1/import/tradovate/{trading_account_id}",
        files=files
    )

    assert response.status_code == 400
    assert "formato CSV" in response.json()['detail']

@pytest.fixture
def valid_mt5_html_content():
    """A fixture for a valid MT5 HTML report content."""
    return b"""
    <!DOCTYPE html>
    <html>
    <body>
        <table>
            <tr><th colspan="14"><div><b>Posizioni</b></div></th></tr>
            <tr align="center">
                <td><b>Ora</b></td><td><b>Posizione</b></td><td><b>Simbolo</b></td><td><b>Tipo</b></td>
                <td><b>Volume</b></td><td><b>Prezzo</b></td><td><b>S / L</b></td><td><b>T / P</b></td>
                <td><b>Ora</b></td><td><b>Prezzo</b></td><td><b>Commissioni</b></td><td><b>Swap</b></td>
                <td colspan="2"><b>Profitto</b></td>
            </tr>
            <tr align="right">
                <td>2025.09.22 13:42:50</td><td>310402409</td><td>XAUUSD</td><td>buy</td>
                <td>2</td><td>3726.65</td><td>3725.75</td><td>3727.20</td>
                <td>2025.09.22 13:43:20</td><td>3725.65</td><td>-10.44</td><td>0.00</td>
                <td colspan="2">-200.00</td>
            </tr>
            <tr><th colspan="14"><div><b>Ordini</b></div></th></tr>
        </table>
    </body>
    </html>
    """

async def test_import_mt5_success(async_client: AsyncClient, db_session: AsyncSession, valid_mt5_html_content, mocker):
    """
    Testa che il controller per l'import di MT5 crei la ImportRun e accodi il task.
    """
    mocker.patch("app.Controllers.import_controller.upload_import_file", return_value="mock/path/report.html")
    mock_delay = mocker.patch("app.Controllers.import_controller.process_import_task.delay")

    trading_account_id = await setup_trading_account(async_client, db_session)
    files = {'file': ('report.html', valid_mt5_html_content, 'text/html')}

    response = await async_client.post(
        f"/api/v1/import/mt5/{trading_account_id}",
        files=files
    )

    # CORREZIONE: Lo status corretto è 202 Accepted
    assert response.status_code == 202
    import_run_data = response.json()
    assert import_run_data['status'] == 'queued'
    assert import_run_data['source_type'] == 'html'

    mock_delay.assert_called_once_with(
        import_run_data['id'],
        "mock/path/report.html",
        "mt5"
    )
