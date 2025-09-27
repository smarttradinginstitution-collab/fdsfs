import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.Models.broker import Broker
from app.Models.enums import ImportSourceType
from app.Models.import_run import ImportRun
from sqlalchemy import select

# Helper to create a broker, needed for trading account setup
async def setup_broker(db_session: AsyncSession) -> str:
    new_broker = Broker(name=f"Test Broker {uuid.uuid4()}")
    db_session.add(new_broker)
    await db_session.commit()
    await db_session.refresh(new_broker)
    return str(new_broker.id)

# Updated helper to create a trading account with required fields
async def setup_trading_account(client: AsyncClient, db_session: AsyncSession) -> str:
    """Helper per creare un General e un Trading Account e restituire l'ID di quest'ultimo."""
    await client.post("/api/v1/general-accounts/")
    broker_id = await setup_broker(db_session)
    response = await client.post(
        "/api/v1/trading-accounts/",
        json={
            "label": "Test Trading Account",
            "broker_id": broker_id,
            "initial_balance": 100000.0,
            "currency": "USD"
        }
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


@pytest.fixture
def valid_csv_content():
    return b'symbol,_priceFormat,_priceFormatType,_tickSize,buyFillId,sellFillId,qty,buyPrice,sellPrice,pnl,boughtTimestamp,soldTimestamp,duration\nNQZ5,-2,0,0.25,1,2,1,24861.0,24878.0,$340.00,09/22/2025 15:50:36,09/22/2025 15:54:58,4min 21sec'

@pytest.fixture
def valid_html_content():
    return b"""
    <!DOCTYPE html><html><head><title>Test Report</title></head><body>
    <div align="center"><table><tr align="center"><th colspan="14">
    <div style="font: 10pt Tahoma"><b>Posizioni</b></div></th></tr>
    <tr align="center" bgcolor="#E5F0FC">
        <td><b>Ora</b></td><td><b>Posizione</b></td><td><b>Simbolo</b></td><td><b>Tipo</b></td><td><b>Volume</b></td><td><b>Prezzo</b></td><td><b>S / L</b></td><td><b>T / P</b></td><td><b>Ora</b></td><td><b>Prezzo</b></td><td><b>Commissioni</b></td><td><b>Swap</b></td><td colspan="2"><b>Profitto</b></td>
    </tr>
    <tr bgcolor="#FFFFFF" align="right">
        <td>2025.09.22 13:42:50</td><td>310402409</td><td>XAUUSD</td><td>buy</td><td>2</td><td>3726.65</td><td>3725.75</td><td>3727.20</td><td>2025.09.22 13:43:20</td><td>3725.65</td><td>-10.44</td><td>0.00</td><td colspan="2">-200.00</td>
    </tr>
    </table></div></body></html>
    """

# Test successful import of a Tradovate CSV
async def test_import_tradovate_csv_success(async_client: AsyncClient, db_session: AsyncSession, valid_csv_content):
    trading_account_id = await setup_trading_account(async_client, db_session)

    files = {'file': ('performance.csv', valid_csv_content, 'text/csv')}

    response = await async_client.post(
        f"/api/v1/import/file/{trading_account_id}",
        files=files
    )

    assert response.status_code == 202
    run_data = response.json()
    assert run_data['source_type'] == ImportSourceType.TRADOVATE_CSV
    assert run_data['status'] == 'queued'

# Test successful import of an MT5 HTML file
async def test_import_mt5_html_success(async_client: AsyncClient, db_session: AsyncSession, valid_html_content):
    trading_account_id = await setup_trading_account(async_client, db_session)

    files = {'file': ('report.html', valid_html_content, 'text/html')}

    response = await async_client.post(
        f"/api/v1/import/file/{trading_account_id}",
        files=files
    )

    assert response.status_code == 202
    run_data = response.json()
    assert run_data['source_type'] == ImportSourceType.MT5_HTML
    assert run_data['status'] == 'queued'

# Test import fails if the Tradovate file is not a performance report
async def test_import_tradovate_fails_without_performance_report(async_client: AsyncClient, db_session: AsyncSession):
    trading_account_id = await setup_trading_account(async_client, db_session)

    files = {'file': ('other_report.csv', b'some,content', 'text/csv')}

    response = await async_client.post(
        f"/api/v1/import/file/{trading_account_id}",
        files=files
    )

    assert response.status_code == 400
    assert "a 'Performance' report CSV file is required" in response.text

# Test import fails for unsupported file types
async def test_import_fails_with_unsupported_file_type(async_client: AsyncClient, db_session: AsyncSession):
    trading_account_id = await setup_trading_account(async_client, db_session)

    files = {'file': ('document.txt', b'some text', 'text/plain')}

    response = await async_client.post(
        f"/api/v1/import/file/{trading_account_id}",
        files=files
    )

    assert response.status_code == 415
    assert "Unsupported file type" in response.text

from typing import Dict

# Test getting import status
async def test_get_import_status(async_client: AsyncClient, db_session: AsyncSession, mock_user_claims: Dict[str, str]):
    trading_account_id = await setup_trading_account(async_client, db_session)
    user_id = uuid.UUID(mock_user_claims["sub"])

    # Manually create an import run to fetch
    new_run = ImportRun(
        id=uuid.uuid4(),
        user_id=user_id,
        trading_account_id=uuid.UUID(trading_account_id),
        source_type=ImportSourceType.TRADOVATE_CSV,
        file_name="test.csv",
        status="applied",
    )
    db_session.add(new_run)
    await db_session.commit()

    response = await async_client.get(f"/api/v1/import/status/{new_run.id}")

    assert response.status_code == 200
    run_data = response.json()
    assert run_data['id'] == str(new_run.id)
    assert run_data['status'] == 'applied'