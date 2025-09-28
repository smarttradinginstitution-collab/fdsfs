from __future__ import annotations

from typing import Optional, Sequence
from uuid import UUID
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.Models.tag import Tag
from app.Models.general_account import GeneralAccount
from app.Models.auth_user import AuthUser
from app.Schemas.tag import TagCreate, TagUpdate


class TagRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_tag_by_id(self, tag_id: UUID) -> Optional[Tag]:
        """Recupera un tag specifico per ID."""
        stmt = select(Tag).where(Tag.id == tag_id).limit(1)
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def create_tag(self, general_account_id: UUID, tag_data: TagCreate) -> Tag:
        """Crea un nuovo tag."""
        db_tag = Tag(
            **tag_data.model_dump(),
            general_account_id=general_account_id
        )
        self.db.add(db_tag)
        await self.db.commit()
        await self.db.refresh(db_tag)
        return db_tag

    async def update_tag(self, db_obj: Tag, tag_data: TagUpdate) -> Tag:
        """Aggiorna un tag esistente."""
        update_data = tag_data.model_dump(exclude_unset=True)
        if not update_data:
            return db_obj

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete_tag(self, db_obj: Tag) -> None:
        """Elimina un tag."""
        await self.db.delete(db_obj)
        await self.db.commit()

    async def list_tags_by_general_account_id(self, general_account_id: UUID) -> Sequence[Tag]:
        """Lista tutti i tag per un dato general_account_id."""
        stmt = select(Tag).where(Tag.general_account_id == general_account_id).order_by(Tag.name.asc())
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def list_all_tags_grouped_by_account(self) -> Sequence[GeneralAccount]:
        """
        Lista tutti i GeneralAccount con i loro tag e utenti associati.
        Utile per l'endpoint admin.
        """
        stmt = (
            select(GeneralAccount)
            .options(
                joinedload(GeneralAccount.user),
                selectinload(GeneralAccount.tags)
            )
            .order_by(GeneralAccount.created_at.asc())
        )
        res = await self.db.execute(stmt)
        return res.scalars().unique().all()

    async def upsert_by_name(self, general_account_id: UUID, name: str, color: Optional[str] = None) -> Tag:
        """
        Cerca un tag per nome; se esiste, lo aggiorna (opzionalmente); altrimenti lo crea.
        Mantenuto per compatibilità con altre parti del sistema (es. import).
        """
        stmt = select(Tag).where(Tag.general_account_id == general_account_id, Tag.name == name).limit(1)
        res = await self.db.execute(stmt)
        row = res.scalars().first()
        if row:
            if color and row.color != color:
                row.color = color
                await self.db.flush()
            return row

        stmt_ins = insert(Tag).values(general_account_id=general_account_id, name=name, color=color).returning(Tag)
        res_ins = await self.db.execute(stmt_ins)
        new_row = res_ins.scalar_one()
        await self.db.flush()
        return new_row