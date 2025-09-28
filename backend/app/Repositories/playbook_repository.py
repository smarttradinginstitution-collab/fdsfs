# app/Repositories/playbook_repository.py
from __future__ import annotations

from typing import Optional, Sequence
from uuid import UUID
from sqlalchemy import select, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.Models.playbook import Playbook
from app.Models.general_account import GeneralAccount
from app.Schemas.playbook import PlaybookCreate, PlaybookUpdate


class PlaybookRepository:
    """Repository for Playbook CRUD operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, playbook_id: UUID) -> Optional[Playbook]:
        stmt = select(Playbook).where(Playbook.id == playbook_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def list_by_general_account_id(self, general_account_id: UUID) -> Sequence[Playbook]:
        stmt = select(Playbook).where(Playbook.general_account_id == general_account_id).order_by(Playbook.title.asc())
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def create(self, playbook_in: PlaybookCreate, general_account_id: UUID) -> Playbook:
        db_playbook = Playbook(
            **playbook_in.model_dump(),
            general_account_id=general_account_id
        )
        self.db.add(db_playbook)
        await self.db.commit()
        await self.db.refresh(db_playbook)
        return db_playbook

    async def update(self, db_obj: Playbook, obj_in: PlaybookUpdate) -> Playbook:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, db_obj: Playbook) -> None:
        await self.db.delete(db_obj)
        await self.db.commit()

    async def upsert_by_title(self, general_account_id: UUID, title: str) -> Playbook:
        stmt = select(Playbook).where(Playbook.general_account_id == general_account_id, Playbook.title == title).limit(1)
        res = await self.db.execute(stmt)
        row = res.scalars().first()
        if row:
            return row

        stmt_ins = insert(Playbook).values(general_account_id=general_account_id, title=title).returning(Playbook)
        res_ins = await self.db.execute(stmt_ins)
        new_row = res_ins.scalar_one()
        await self.db.flush()
        return new_row

    async def list_all_playbooks_grouped_by_account(self) -> Sequence[GeneralAccount]:
        """
        Lista tutti i GeneralAccount con i loro playbook e utenti associati.
        Utile per l'endpoint admin.
        """
        stmt = (
            select(GeneralAccount)
            .options(
                joinedload(GeneralAccount.user),
                selectinload(GeneralAccount.playbooks)
            )
            .order_by(GeneralAccount.created_at.asc())
        )
        res = await self.db.execute(stmt)
        return res.scalars().unique().all()