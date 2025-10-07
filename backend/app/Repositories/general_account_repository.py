# app/Repositories/general_account_repository.py
from __future__ import annotations

from uuid import UUID
from typing import Optional

from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.Models.general_account import GeneralAccount
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
        """
        Crea un nuovo GeneralAccount per un utente.
        Se l'utente ha già un account, lo restituisce senza crearne uno nuovo.
        """
        existing_account = await self.get_by_user_id(user_id)
        if existing_account:
            return existing_account

        db_account = GeneralAccount(
            user_id=user_id,
            label=account_data.label
        )
        self.db.add(db_account)
        try:
            await self.db.commit()
            await self.db.refresh(db_account)
        except IntegrityError:
            await self.db.rollback()
            existing_account = await self.get_by_user_id(user_id)
            if existing_account:
                return existing_account
            else:
                raise

        return db_account