# app/Repositories/playbook_repository.py
from __future__ import annotations

from typing import Optional, Sequence
from uuid import UUID
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.Models.playbook import Playbook
from app.Models.general_account import GeneralAccount
from app.Models.auth_user import AuthUser
from app.Schemas.playbook import PlaybookCreate, PlaybookUpdate


class PlaybookRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_playbook_by_id(self, playbook_id: UUID) -> Optional[Playbook]:
        """Recupera un playbook specifico per ID."""
        stmt = select(Playbook).where(Playbook.id == playbook_id).limit(1)
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def create_playbook(self, general_account_id: UUID, playbook_data: PlaybookCreate) -> Playbook:
        """Crea un nuovo playbook."""
        db_playbook = Playbook(
            **playbook_data.model_dump(),
            general_account_id=general_account_id
        )
        self.db.add(db_playbook)
        await self.db.commit()
        await self.db.refresh(db_playbook)
        return db_playbook

    async def update_playbook(self, db_obj: Playbook, playbook_data: PlaybookUpdate) -> Playbook:
        """Aggiorna un playbook esistente."""
        update_data = playbook_data.model_dump(exclude_unset=True)
        if not update_data:
            return db_obj

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete_playbook(self, db_obj: Playbook) -> None:
        """Elimina un playbook."""
        await self.db.delete(db_obj)
        await self.db.commit()

    async def list_playbooks_by_general_account_id(self, general_account_id: UUID) -> Sequence[Playbook]:
        """Lista tutti i playbook per un dato general_account_id."""
        stmt = select(Playbook).where(Playbook.general_account_id == general_account_id).order_by(Playbook.name.asc())
        res = await self.db.execute(stmt)
        return res.scalars().all()

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

    async def upsert_by_name(self, general_account_id: UUID, name: str, color: Optional[str] = None) -> Playbook:
        """
        Cerca un playbook per nome; se esiste, lo aggiorna (opzionalmente); altrimenti lo crea.
        Mantenuto per compatibilità con altre parti del sistema (es. import).
        """
        stmt = select(Playbook).where(Playbook.general_account_id == general_account_id, Playbook.name == name).limit(1)
        res = await self.db.execute(stmt)
        row = res.scalars().first()
        if row:
            if color and row.color != color:
                row.color = color
                await self.db.flush()
            return row

        stmt_ins = insert(Playbook).values(general_account_id=general_account_id, name=name, color=color).returning(Playbook)
        res_ins = await self.db.execute(stmt_ins)
        new_row = res_ins.scalar_one()
        await self.db.flush()
        return new_row