import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.Models.request_log import RequestLog

@pytest.mark.anyio
async def test_middleware_logs_request(admin_async_client: AsyncClient, db_session: AsyncSession):
    """
    Verifica che il middleware registri correttamente una richiesta nel database.
    """
    # Pulisci i log precedenti per avere un ambiente di test pulito
    await db_session.execute(select(RequestLog))
    await db_session.commit()
    delete_stmt = RequestLog.__table__.delete()
    await db_session.execute(delete_stmt)
    await db_session.commit()

    # Fai una richiesta a un endpoint esistente (es. la rotta health)
    response = await admin_async_client.get("/")
    assert response.status_code == 200

    # Verifica che un log sia stato creato nel database
    stmt = select(RequestLog).where(RequestLog.path == "/")
    result = await db_session.execute(stmt)
    log_entry = result.scalars().first()

    assert log_entry is not None
    assert log_entry.method == "GET"
    assert log_entry.path == "/"
    assert log_entry.status_code == 200
    assert log_entry.response_time_ms > 0

@pytest.mark.anyio
async def test_request_logs_access_permissions(admin_async_client: AsyncClient, async_client: AsyncClient, db_session: AsyncSession):
    """
    Verifica che solo gli amministratori possano accedere agli endpoint dei log.
    """
    # Setup: crea un log di esempio
    log = RequestLog(method='GET', path='/api/v1/dummy', status_code=200, response_time_ms=10)
    db_session.add(log)
    await db_session.commit()

    # Test: L'admin può accedere a GET
    get_response_admin = await admin_async_client.get("/api/v1/request-logs")
    assert get_response_admin.status_code == 200
    assert len(get_response_admin.json()) > 0

    # Test: L'utente normale non può accedere a GET
    get_response_user = await async_client.get("/api/v1/request-logs")
    assert get_response_user.status_code == 403

    # Test: L'admin può accedere a DELETE
    delete_response_admin = await admin_async_client.delete("/api/v1/request-logs")
    assert delete_response_admin.status_code == 200
    assert "deleted_count" in delete_response_admin.json()

    # Ricrea il log per il prossimo test
    db_session.add(log)
    await db_session.commit()

    # Test: L'utente normale non può accedere a DELETE
    delete_response_user = await async_client.delete("/api/v1/request-logs")
    assert delete_response_user.status_code == 403

@pytest.mark.anyio
async def test_get_request_logs_with_filters_and_sorting(admin_async_client: AsyncClient, db_session: AsyncSession):
    """
    Testa le funzionalità di filtro, ordinamento e paginazione dell'endpoint GET.
    """
    # Setup: Pulisci e crea dati di test
    delete_stmt = RequestLog.__table__.delete()
    await db_session.execute(delete_stmt)
    await db_session.commit()

    log1 = RequestLog(method='GET', path='/path1', status_code=200, response_time_ms=150)
    log2 = RequestLog(method='POST', path='/path2', status_code=500, response_time_ms=50)
    log3 = RequestLog(method='GET', path='/path3', status_code=200, response_time_ms=100)
    db_session.add_all([log1, log2, log3])
    await db_session.commit()

    # Test: Filtro per status code
    response = await admin_async_client.get("/api/v1/request-logs?status_code_filter=200")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(item['status_code'] == 200 for item in data)

    # Test: Ordinamento per tempo di risposta
    response = await admin_async_client.get("/api/v1/request-logs?sort_by=response_time_ms&sort_order=asc")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]['response_time_ms'] == 50
    assert data[1]['response_time_ms'] == 100
    assert data[2]['response_time_ms'] == 150

    # Test: Paginazione
    response = await admin_async_client.get("/api/v1/request-logs?limit=1&offset=1&sort_by=response_time_ms&sort_order=asc")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['response_time_ms'] == 100