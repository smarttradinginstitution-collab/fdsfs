import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.Models.request_log import RequestLog
from app.Repositories.request_log_repository import RequestLogRepository

@pytest.mark.anyio
async def test_request_log_repository_operations(db_session: AsyncSession):
    """
    Testa le operazioni di base del RequestLogRepository: creazione (implicita),
    elenco con filtri/ordinamento e cancellazione.
    """
    repo = RequestLogRepository(db_session)

    # 1. Setup: Crea alcuni dati di log di esempio
    log1 = RequestLog(method='GET', path='/api/v1/test1', status_code=200, response_time_ms=100)
    log2 = RequestLog(method='POST', path='/api/v1/test2', status_code=404, response_time_ms=250)
    log3 = RequestLog(method='GET', path='/api/v1/test3', status_code=200, response_time_ms=50)

    db_session.add_all([log1, log2, log3])
    await db_session.commit()

    # 2. Test: Elenco base
    all_logs = await repo.list()
    assert len(all_logs) == 3, "Dovrebbe restituire tutti e 3 i log"

    # 3. Test: Elenco con filtro per status code
    success_logs = await repo.list(status_code_filter=200)
    assert len(success_logs) == 2, "Dovrebbe restituire solo i 2 log con status 200"
    assert all(log.status_code == 200 for log in success_logs)

    not_found_logs = await repo.list(status_code_filter=404)
    assert len(not_found_logs) == 1, "Dovrebbe restituire solo il log con status 404"
    assert not_found_logs[0].path == '/api/v1/test2'

    # 4. Test: Elenco con ordinamento
    # Ordina per tempo di risposta ascendente
    fastest_first = await repo.list(sort_by='response_time_ms', sort_order='asc')
    assert len(fastest_first) == 3
    assert fastest_first[0].response_time_ms == 50
    assert fastest_first[1].response_time_ms == 100
    assert fastest_first[2].response_time_ms == 250

    # Ordina per tempo di risposta discendente
    slowest_first = await repo.list(sort_by='response_time_ms', sort_order='desc')
    assert len(slowest_first) == 3
    assert slowest_first[0].response_time_ms == 250
    assert slowest_first[1].response_time_ms == 100
    assert slowest_first[2].response_time_ms == 50

    # 5. Test: Paginazione
    paginated_logs = await repo.list(offset=1, limit=1, sort_by='created_at', sort_order='asc')
    assert len(paginated_logs) == 1, "La paginazione dovrebbe restituire un solo log"
    # L'ordinamento di default è per `created_at`, quindi il secondo log inserito dovrebbe essere log2
    assert paginated_logs[0].path == '/api/v1/test2'

    # 6. Test: Cancellazione
    deleted_count = await repo.delete_all()
    assert deleted_count == 3, "Dovrebbe riportare che 3 log sono stati cancellati"

    # Verifica che la tabella sia vuota
    logs_after_delete = await repo.list()
    assert len(logs_after_delete) == 0, "La tabella dei log dovrebbe essere vuota dopo la cancellazione"