# app/Controllers/request_log_controller.py
from typing import Optional
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.Infrastructure.db import get_db
from app.Repositories.request_log_repository import RequestLogRepository
from app.Schemas.request_log import PaginatedRequestLogResponse

class RequestLogController:

    async def list_logs(
        self,
        offset: int = 0,
        limit: int = 100,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        status_code_filter: Optional[int] = None,
        db: AsyncSession = Depends(get_db),
    ) -> PaginatedRequestLogResponse:
        """
        Recupera un elenco paginato di log delle richieste con filtri e ordinamento.
        """
        repo = RequestLogRepository(db)

        # Valida i parametri di ordinamento per evitare injection
        if sort_by not in ["created_at", "response_time_ms", "status_code", "method", "path"]:
            raise HTTPException(status_code=400, detail="Parametro 'sort_by' non valido.")
        if sort_order.lower() not in ["asc", "desc"]:
            raise HTTPException(status_code=400, detail="Parametro 'sort_order' non valido.")

        # Esegui le query in sequenza per evitare conflitti sulla stessa connessione db
        total_count = await repo.count(status_code_filter=status_code_filter)
        logs = await repo.list(
            offset=offset,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
            status_code_filter=status_code_filter,
        )

        return PaginatedRequestLogResponse(total=total_count, data=logs)

    async def clear_logs(
        self,
        db: AsyncSession = Depends(get_db),
    ) -> dict:
        """
        Cancella tutti i log delle richieste.
        """
        repo = RequestLogRepository(db)
        deleted_count = await repo.delete_all()
        return {"deleted_count": deleted_count, "ok": True}