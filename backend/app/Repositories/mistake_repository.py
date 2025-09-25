# app/Repositories/mistake_repository.py
from __future__ import annotations

from typing import Sequence
from uuid import UUID
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.Models.mistake import Mistake


class MistakeRepository:
    """CRUD minimale + upsert (general_account_id, name) per Mistake."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def upsert_by_name(self, general_account_id: UUID, name: str) -> Mistake:
        # Cerca se l'errore esiste già
        stmt = select(Mistake).where(Mistake.general_account_id == general_account_id, Mistake.name == name).limit(1)
        res = await self.db.execute(stmt)
        row = res.scalars().first()
        if row:
            return row

        # Se non esiste, lo crea
        stmt_ins = insert(Mistake).values(general_account_id=general_account_id, name=name).returning(Mistake)
        res_ins = await self.db.execute(stmt_ins)
        new_row = res_ins.scalar_one()
        await self.db.flush()
        return new_row

    async def list_mistakes_by_general_account_id(self, general_account_id: UUID) -> Sequence[Mistake]:
        stmt = select(Mistake).where(Mistake.general_account_id == general_account_id).order_by(Mistake.name.asc())
        res = await self.db.execute(stmt)
        return res.scalars().all()