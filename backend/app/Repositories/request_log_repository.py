# app/Repositories/request_log_repository.py
from typing import Sequence, Optional
from sqlalchemy import select, delete, asc, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.Models.request_log import RequestLog

class RequestLogRepository:
    """
    Repository per la tabella `public.request_logs`.
    Espone metodi per leggere e cancellare i log delle richieste.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list(
        self,
        offset: int = 0,
        limit: int = 100,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        status_code_filter: Optional[int] = None,
    ) -> Sequence[RequestLog]:
        """
        Ritorna un elenco di log delle richieste con paginazione, ordinamento e filtri.
        """
        stmt = select(RequestLog)

        # Applica il filtro per status code, se fornito
        if status_code_filter is not None:
            stmt = stmt.where(RequestLog.status_code == status_code_filter)

        # Applica l'ordinamento
        order_column = getattr(RequestLog, sort_by, RequestLog.created_at)
        if sort_order.lower() == "asc":
            stmt = stmt.order_by(asc(order_column))
        else:
            stmt = stmt.order_by(desc(order_column))

        # Applica la paginazione
        stmt = stmt.offset(offset).limit(limit)

        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def count(
        self,
        status_code_filter: Optional[int] = None,
    ) -> int:
        """
        Ritorna il conteggio totale dei log, applicando gli stessi filtri di `list`.
        """
        stmt = select(func.count()).select_from(RequestLog)

        # Applica il filtro per status code, se fornito
        if status_code_filter is not None:
            stmt = stmt.where(RequestLog.status_code == status_code_filter)

        res = await self.db.execute(stmt)
        return res.scalar() or 0

    async def delete_all(self) -> int:
        """
        Elimina tutti i log delle richieste dalla tabella.
        Ritorna il numero di righe cancellate.
        """
        stmt = delete(RequestLog)
        res = await self.db.execute(stmt)
        await self.db.commit()
        return res.rowcount or 0