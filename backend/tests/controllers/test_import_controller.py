# backend/tests/controllers/test_import_controller.py
import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from sqlalchemy import select

from app.Models.import_run import ImportRun
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
        json={"label": "Test Trading Account", "broker_id": broker_id}
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]

@pytest.fixture
def valid_csv_content():
    return """
symbol,_priceFormat,_priceFormatType,_tickSize,buyFillId,sellFillId,qty,buyPrice,sellPrice,pnl,boughtTimestamp,soldTimestamp,duration
NQZ5,-2,0,0.25,1,2,1,24861.0,24878.0,$340.00,09/22/2025 15:50:36,09/22/2025 15:54:58,4min 21sec
    """.strip().encode('utf-8')

async def test_import_tradovate_success(async_client: AsyncClient, db_session: AsyncSession, valid_csv_content):
    """
    Test successful import of a Tradovate performance report.
    """
    trading_account_id = await setup_trading_account(async_client, db_session)

    files = {'files': ('performance.csv', valid_csv_content, 'text/csv')}

    # 1. Upload the file
    response = await async_client.post(
        f"/api/v1/import/tradovate/{trading_account_id}",
        files=files
    )

    assert response.status_code == 202
    import_run_data = response.json()
    assert import_run_data['status'] == 'queued'
    assert import_run_data['trading_account_id'] == str(trading_account_id)

    import_run_id = import_run_data['id']

    # 2. Poll for completion
    for _ in range(10): # Poll for up to 30 seconds
        await asyncio.sleep(3)
        status_response = await async_client.get(f"/api/v1/import/status/{import_run_id}")
        if status_response.status_code == 200 and status_response.json()['status'] == 'applied':
            break

    final_status_response = await async_client.get(f"/api/v1/import/status/{import_run_id}")
    assert final_status_response.status_code == 200
    final_run_data = final_status_response.json()

    assert final_run_data['status'] == 'applied'
    assert final_run_data['total_rows'] == 1
    assert final_run_data['inserted_count'] == 1
    assert final_run_data['skipped_count'] == 0

    # 3. Verify trade was inserted in DB
    result = await db_session.execute(
        select(Trade).where(Trade.import_run_id == uuid.UUID(import_run_id))
    )
    inserted_trade = result.scalars().first()
    assert inserted_trade is not None
    assert inserted_trade.p_l == 340.0
    assert inserted_trade.symbol_snapshot == "NQZ5"

async def test_import_fails_without_performance_report(async_client: AsyncClient, db_session: AsyncSession):
    """
    Test that the import fails if a file not named 'performance' is uploaded.
    """
    trading_account_id = await setup_trading_account(async_client, db_session)

    files = {'files': ('other_report.csv', b'some,content', 'text/csv')}

    response = await async_client.post(
        f"/api/v1/import/tradovate/{trading_account_id}",
        files=files
    )

    assert response.status_code == 400
    assert "A 'Performance' report CSV file is required" in response.json()['detail']

async def test_import_fails_with_too_many_files(async_client: AsyncClient, db_session: AsyncSession, valid_csv_content):
    """
    Test that the import fails if more than 5 files are uploaded.
    """
    trading_account_id = await setup_trading_account(async_client, db_session)

    file_list = [('files', (f'file{i}.csv', valid_csv_content, 'text/csv')) for i in range(6)]

    response = await async_client.post(
        f"/api/v1/import/tradovate/{trading_account_id}",
        files=file_list
    )

    assert response.status_code == 400
    assert "Cannot upload more than 5 files at once" in response.json()['detail']