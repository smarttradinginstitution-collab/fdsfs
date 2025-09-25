# app/Repositories/tag_repository.py

from __future__ import annotations

from typing import Optional, Sequence
from uuid import UUID
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.Models.tag import Tag


class TagRepository:
    """CRUD minimale + upsert (general_account_id, name) per Tag."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def upsert_by_name(self, general_account_id: UUID, name: str, color: Optional[str] = None) -> Tag:
        # prova get
        stmt = select(Tag).where(Tag.general_account_id == general_account_id, Tag.name == name).limit(1)
        res = await self.db.execute(stmt)
        row = res.scalars().first()
        if row:
            if color and row.color != color:
                row.color = color
                await self.db.flush()
            return row

        # crea
        stmt_ins = insert(Tag).values(general_account_id=general_account_id, name=name, color=color).returning(Tag)
        res_ins = await self.db.execute(stmt_ins)
        new_row = res_ins.scalar_one()
        await self.db.flush()
        return new_row

    async def list_tags_by_general_account_id(self, general_account_id: UUID) -> Sequence[Tag]:
        stmt = select(Tag).where(Tag.general_account_id == general_account_id).order_by(Tag.name.asc())
        res = await self.db.execute(stmt)
        return res.scalars().all()