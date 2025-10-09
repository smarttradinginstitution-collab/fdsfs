# app/Repositories/news_impact_repository.py
from __future__ import annotations

from typing import Sequence
from uuid import UUID
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.Models.news_impact import NewsImpact


class NewsImpactRepository:
    """CRUD minimale + upsert (general_account_id, title) per NewsImpact."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def upsert_by_title(self, general_account_id: UUID, title: str) -> NewsImpact:
        # Cerca se l'impatto della notizia esiste già
        stmt = select(NewsImpact).where(NewsImpact.general_account_id == general_account_id, NewsImpact.title == title).limit(1)
        res = await self.db.execute(stmt)
        row = res.scalars().first()
        if row:
            return row

        # Se non esiste, lo crea
        stmt_ins = insert(NewsImpact).values(general_account_id=general_account_id, title=title).returning(NewsImpact)
        res_ins = await self.db.execute(stmt_ins)
        new_row = res_ins.scalar_one()
        await self.db.flush()
        return new_row

    async def list_news_impacts_by_general_account_id(self, general_account_id: UUID) -> Sequence[NewsImpact]:
        stmt = select(NewsImpact).where(NewsImpact.general_account_id == general_account_id).order_by(NewsImpact.title.asc())
        res = await self.db.execute(stmt)
        return res.scalars().all()