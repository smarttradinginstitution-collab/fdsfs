# app/Services/general_account_service.py
from __future__ import annotations

from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.Repositories.general_account_repository import GeneralAccountRepository
from app.Schemas.general_account import GeneralAccountCreate, GeneralAccountRead
from app.Infrastructure.db import get_db


class GeneralAccountService:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db
        self.repo = GeneralAccountRepository(db)

    async def create_general_account_for_user(
        self, claims: dict
    ) -> GeneralAccountRead:
        """
        Crea un GeneralAccount per l'utente corrente, usando la sua email come label.
        """
        user_id = UUID(claims["sub"])
        user_email = claims["email"]

        account_create_schema = GeneralAccountCreate(label=user_email)

        db_account = await self.repo.create_general_account(
            user_id=user_id,
            account_data=account_create_schema
        )

        return GeneralAccountRead.from_orm(db_account)

    async def get_general_account_for_user(
        self, claims: dict
    ) -> Optional[GeneralAccountRead]:
        """Recupera il GeneralAccount per l'utente corrente."""
        user_id = UUID(claims["sub"])
        db_account = await self.repo.get_by_user_id(user_id=user_id)
        if db_account:
            return GeneralAccountRead.from_orm(db_account)
        return None