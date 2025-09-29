from __future__ import annotations

from typing import Optional, Sequence
from uuid import UUID
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.Models.mistake import Mistake
from app.Models.general_account import GeneralAccount
from app.Schemas.mistake import MistakeCreate, MistakeUpdate


class MistakeRepository:
    """Repository for Mistake CRUD operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, mistake_id: UUID) -> Optional[Mistake]:
        """Recupera un errore specifico per ID."""
        stmt = select(Mistake).where(Mistake.id == mistake_id).limit(1)
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def create(self, mistake_in: MistakeCreate, general_account_id: UUID) -> Mistake:
        """Crea un nuovo errore."""
        db_mistake = Mistake(
            **mistake_in.model_dump(),
            general_account_id=general_account_id
        )
        self.db.add(db_mistake)
        await self.db.commit()
        await self.db.refresh(db_mistake)
        return db_mistake

    async def update(self, db_obj: Mistake, obj_in: MistakeUpdate) -> Mistake:
        """Aggiorna un errore esistente."""
        update_data = obj_in.model_dump(exclude_unset=True)
        if not update_data:
            return db_obj

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, db_obj: Mistake) -> None:
        """Elimina un errore."""
        await self.db.delete(db_obj)
        await self.db.commit()

    async def list_by_general_account_id(self, general_account_id: UUID) -> Sequence[Mistake]:
        """Lista tutti gli errori per un dato general_account_id."""
        stmt = select(Mistake).where(Mistake.general_account_id == general_account_id).order_by(Mistake.name.asc())
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def list_all_mistakes_grouped_by_account(self) -> Sequence[GeneralAccount]:
        """
        Lista tutti i GeneralAccount con i loro errori e utenti associati.
        Utile per l'endpoint admin.
        """
        stmt = (
            select(GeneralAccount)
            .options(
                joinedload(GeneralAccount.user),
                selectinload(GeneralAccount.mistakes)
            )
            .order_by(GeneralAccount.created_at.asc())
        )
        res = await self.db.execute(stmt)
        return res.scalars().unique().all()

    async def upsert_by_name(self, general_account_id: UUID, name: str) -> Mistake:
        """
        Cerca un errore per nome; se non esiste, lo crea.
        """
        stmt = select(Mistake).where(Mistake.general_account_id == general_account_id, Mistake.name == name).limit(1)
        res = await self.db.execute(stmt)
        row = res.scalars().first()
        if row:
            return row

        stmt_ins = insert(Mistake).values(general_account_id=general_account_id, name=name).returning(Mistake)
        res_ins = await self.db.execute(stmt_ins)
        new_row = res_ins.scalar_one()
        await self.db.flush()
        return new_row