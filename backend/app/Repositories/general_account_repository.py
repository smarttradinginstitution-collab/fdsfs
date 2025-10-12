# app/Repositories/general_account_repository.py
from __future__ import annotations

from uuid import UUID
from typing import Optional

from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.Models.general_account import GeneralAccount
from app.Models.tags_group import TagsGroup
from app.Schemas.general_account import GeneralAccountCreate


class GeneralAccountRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user_id(self, user_id: UUID) -> Optional[GeneralAccount]:
        """Recupera un GeneralAccount tramite user_id, con eager loading dell'utente."""
        stmt = (
            select(GeneralAccount)
            .options(
                selectinload(GeneralAccount.user),
                selectinload(GeneralAccount.images)
            )
            .where(GeneralAccount.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def create_general_account(
        self, user_id: UUID, account_data: GeneralAccountCreate
    ) -> GeneralAccount:
        """Crea un nuovo GeneralAccount, lo aggiunge alla sessione e lo flusha."""
        db_account = GeneralAccount(user_id=user_id, label=account_data.label)
        self.db.add(db_account)
        await self.db.flush()
        await self.db.refresh(db_account)
        return db_account

    async def get_by_id_with_all_data(self, account_id: UUID) -> Optional[GeneralAccount]:
        """
        Recupera un GeneralAccount tramite il suo ID con tutte le relazioni caricate (eager loading).
        """
        stmt = (
            select(GeneralAccount)
            .where(GeneralAccount.id == account_id)
            .options(
                selectinload(GeneralAccount.mistakes),
                selectinload(GeneralAccount.news_impacts),
                selectinload(GeneralAccount.psychology_states),
                selectinload(GeneralAccount.tags_groups).selectinload(TagsGroup.tags),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()