# app/Repositories/psychology_state_repository.py
from __future__ import annotations

from typing import Sequence
from uuid import UUID
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.Models.psychology_state import PsychologyState


class PsychologyStateRepository:
    """CRUD minimale + upsert (general_account_id, state) per PsychologyState."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def upsert_by_state(self, general_account_id: UUID, state: str) -> PsychologyState:
        # Cerca se lo stato psicologico esiste già
        stmt = select(PsychologyState).where(PsychologyState.general_account_id == general_account_id, PsychologyState.state == state).limit(1)
        res = await self.db.execute(stmt)
        row = res.scalars().first()
        if row:
            return row

        # Se non esiste, lo crea
        stmt_ins = insert(PsychologyState).values(general_account_id=general_account_id, state=state).returning(PsychologyState)
        res_ins = await self.db.execute(stmt_ins)
        new_row = res_ins.scalar_one()
        await self.db.flush()
        return new_row

    async def list_psychology_states_by_general_account_id(self, general_account_id: UUID) -> Sequence[PsychologyState]:
        stmt = select(PsychologyState).where(PsychologyState.general_account_id == general_account_id).order_by(PsychologyState.state.asc())
        res = await self.db.execute(stmt)
        return res.scalars().all()