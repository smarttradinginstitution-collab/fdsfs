# app/Repositories/playbook_repository.py
from __future__ import annotations

from typing import Optional, Sequence
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import select, insert, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.Models.playbook import Playbook
from app.Models.general_account import GeneralAccount
from app.Schemas.playbook import PlaybookCreate, PlaybookUpdate


class PlaybookRepository:
    """Repository for Playbook CRUD operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def _check_duplicate_title(self, general_account_id: UUID, title: str, current_playbook_id: Optional[UUID] = None) -> None:
        """Checks for a duplicate playbook title within the same general account."""
        query = select(Playbook).where(
            Playbook.general_account_id == general_account_id,
            Playbook.title == title
        )
        if current_playbook_id:
            query = query.where(Playbook.id != current_playbook_id)

        result = await self.db.execute(query)
        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A playbook with this title already exists."
            )

    async def get_by_id(self, playbook_id: UUID) -> Optional[Playbook]:
        stmt = (
            select(Playbook)
            .where(Playbook.id == playbook_id)
            .options(selectinload(Playbook.rules_groups))
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_by_id_with_trades(self, playbook_id: UUID) -> Optional[Playbook]:
        stmt = (
            select(Playbook)
            .where(Playbook.id == playbook_id)
            .options(
                selectinload(Playbook.trades),
                joinedload(Playbook.general_account) # Per il controllo utente
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def list_by_general_account_id(self, general_account_id: UUID) -> Sequence[Playbook]:
        stmt = (
            select(Playbook)
            .where(Playbook.general_account_id == general_account_id)
            .options(selectinload(Playbook.rules_groups))
            .order_by(Playbook.title.asc())
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def list_by_general_account_id_with_trades(self, general_account_id: UUID) -> Sequence[Playbook]:
        stmt = (
            select(Playbook)
            .where(Playbook.general_account_id == general_account_id)
            .options(
                selectinload(Playbook.rules_groups),
                selectinload(Playbook.trades)  # Eager load trades
            )
            .order_by(Playbook.title.asc())
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def create(self, playbook_in: PlaybookCreate, general_account_id: UUID) -> Playbook:
        await self._check_duplicate_title(general_account_id, playbook_in.title)

        db_playbook = Playbook(
            **playbook_in.model_dump(),
            general_account_id=general_account_id
        )
        self.db.add(db_playbook)
        await self.db.commit()
        await self.db.refresh(db_playbook)
        # Ricarica l'oggetto con le relazioni per essere sicuri che siano caricate
        return await self.get_by_id(db_playbook.id)

    async def update(self, db_obj: Playbook, obj_in: PlaybookUpdate) -> Playbook:
        update_data = obj_in.model_dump(exclude_unset=True)

        if 'title' in update_data and update_data['title'] != db_obj.title:
            await self._check_duplicate_title(db_obj.general_account_id, update_data['title'], db_obj.id)

        for field, value in update_data.items():
            setattr(db_obj, field, value)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return await self.get_by_id(db_obj.id)

    async def delete(self, db_obj: Playbook) -> None:
        await self.db.delete(db_obj)
        await self.db.commit()

    async def upsert_by_title(self, general_account_id: UUID, title: str) -> Playbook:
        stmt = select(Playbook).where(Playbook.general_account_id == general_account_id, Playbook.title == title).limit(1)
        res = await self.db.execute(stmt)
        row = res.scalars().first()
        if row:
            return row

        # La descrizione è NOT NULL, quindi forniamo un default vuoto
        stmt_ins = insert(Playbook).values(
            general_account_id=general_account_id,
            title=title,
            description=""
        ).returning(Playbook.id)
        res_ins = await self.db.execute(stmt_ins)
        new_id = res_ins.scalar_one()
        await self.db.commit()
        return await self.get_by_id(new_id)

    async def list_all_playbooks_grouped_by_account(self) -> Sequence[GeneralAccount]:
        """
        Lista tutti i GeneralAccount con i loro playbook e utenti associati.
        Utile per l'endpoint admin.
        """
        stmt = (
            select(GeneralAccount)
            .options(
                joinedload(GeneralAccount.user),
                selectinload(GeneralAccount.playbooks).selectinload(Playbook.rules_groups)
            )
            .order_by(GeneralAccount.created_at.asc())
        )
        res = await self.db.execute(stmt)
        return res.scalars().unique().all()