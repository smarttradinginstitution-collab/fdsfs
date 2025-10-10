from __future__ import annotations

from typing import Optional, Sequence
from uuid import UUID
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.Models.psychology_state import PsychologyState
from app.Models.general_account import GeneralAccount
from app.Schemas.psychology_state import PsychologyStateCreate, PsychologyStateUpdate


class PsychologyStateRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_psychology_state_by_id(self, psychology_state_id: UUID) -> Optional[PsychologyState]:
        """Recupera uno stato psicologico specifico per ID."""
        stmt = select(PsychologyState).where(PsychologyState.id == psychology_state_id).limit(1)
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def create_psychology_state(self, general_account_id: UUID, psychology_state_data: PsychologyStateCreate) -> PsychologyState:
        """Crea un nuovo stato psicologico."""
        db_psychology_state = PsychologyState(
            **psychology_state_data.model_dump(),
            general_account_id=general_account_id
        )
        self.db.add(db_psychology_state)
        await self.db.commit()
        await self.db.refresh(db_psychology_state)
        return db_psychology_state

    async def update_psychology_state(self, db_obj: PsychologyState, psychology_state_data: PsychologyStateUpdate) -> PsychologyState:
        """Aggiorna uno stato psicologico esistente."""
        update_data = psychology_state_data.model_dump(exclude_unset=True)
        if not update_data:
            return db_obj

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete_psychology_state(self, db_obj: PsychologyState) -> None:
        """Elimina uno stato psicologico."""
        await self.db.delete(db_obj)
        await self.db.commit()

    async def list_psychology_states_by_general_account_id(self, general_account_id: UUID) -> Sequence[PsychologyState]:
        """Lista tutti gli stati psicologici per un dato general_account_id."""
        stmt = select(PsychologyState).where(PsychologyState.general_account_id == general_account_id).order_by(PsychologyState.name.asc())
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def list_all_psychology_states_grouped_by_account(self) -> Sequence[GeneralAccount]:
        """
        Lista tutti i GeneralAccount con i loro stati psicologici e utenti associati.
        Utile per l'endpoint admin.
        """
        stmt = (
            select(GeneralAccount)
            .options(
                joinedload(GeneralAccount.user),
                selectinload(GeneralAccount.psychology_states)
            )
            .order_by(GeneralAccount.created_at.asc())
        )
        res = await self.db.execute(stmt)
        return res.scalars().unique().all()

    async def upsert_by_state(self, general_account_id: UUID, state: str) -> PsychologyState:
        """
        Cerca uno stato psicologico per nome; se non esiste, lo crea.
        Mantenuto per compatibilità con altre parti del sistema (es. import).
        """
        stmt = select(PsychologyState).where(PsychologyState.general_account_id == general_account_id, PsychologyState.name == state).limit(1)
        res = await self.db.execute(stmt)
        row = res.scalars().first()
        if row:
            return row

        stmt_ins = insert(PsychologyState).values(general_account_id=general_account_id, name=state).returning(PsychologyState)
        res_ins = await self.db.execute(stmt_ins)
        new_row = res_ins.scalar_one()
        await self.db.flush()
        return new_row