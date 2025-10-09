# app/Repositories/news_impact_repository.py
from __future__ import annotations
from uuid import UUID
from typing import List, Optional

from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.Models.news_impact import NewsImpact
from app.Schemas.news_impact import NewsImpactCreate, NewsImpactUpdate


class NewsImpactRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, news_impact_id: UUID) -> Optional[NewsImpact]:
        """Recupera un News Impact per ID."""
        result = await self.session.get(NewsImpact, news_impact_id)
        return result

    async def list_by_general_account_id(self, general_account_id: UUID) -> List[NewsImpact]:
        """Recupera tutti i News Impact per un general account."""
        stmt = select(NewsImpact).where(NewsImpact.general_account_id == general_account_id).order_by(NewsImpact.created_at)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, obj_in: NewsImpactCreate, general_account_id: UUID) -> NewsImpact:
        """Crea un nuovo News Impact."""
        new_news_impact = NewsImpact(
            **obj_in.model_dump(),
            general_account_id=general_account_id
        )
        self.session.add(new_news_impact)
        await self.session.commit()
        await self.session.refresh(new_news_impact)
        return new_news_impact

    async def update(self, db_obj: NewsImpact, obj_in: NewsImpactUpdate) -> NewsImpact:
        """Aggiorna un News Impact esistente."""
        update_data = obj_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_obj, key, value)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def delete(self, db_obj: NewsImpact) -> None:
        """Elimina un News Impact."""
        await self.session.delete(db_obj)
        await self.session.commit()
        return None

    async def upsert_by_name(self, general_account_id: UUID, name: str) -> NewsImpact:
        """
        Cerca un news impact per nome; se non esiste, lo crea.
        """
        stmt = select(NewsImpact).where(NewsImpact.general_account_id == general_account_id, NewsImpact.name == name).limit(1)
        res = await self.session.execute(stmt)
        row = res.scalars().first()
        if row:
            return row

        stmt_ins = insert(NewsImpact).values(general_account_id=general_account_id, name=name).returning(NewsImpact)
        res_ins = await self.session.execute(stmt_ins)
        new_row = res_ins.scalar_one()
        await self.session.flush()
        return new_row