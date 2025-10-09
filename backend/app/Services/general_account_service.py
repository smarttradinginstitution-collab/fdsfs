# app/Services/general_account_service.py
from __future__ import annotations

from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status

from app.Repositories.general_account_repository import GeneralAccountRepository
from app.Schemas.general_account import (
    GeneralAccountCreate,
    GeneralAccountRead,
    GeneralAccountWithData,
)
from app.Infrastructure.db import get_db
from app.Services.notebook_service import NotebookService


class GeneralAccountService:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db
        self.repo = GeneralAccountRepository(db)

    async def create_general_account_for_user(
        self, claims: dict, notebook_service: NotebookService
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

        # Automatically create system folders for the new account
        await notebook_service._ensure_system_folders_exist(db_account.id)

        return GeneralAccountRead.model_validate(db_account)

    async def get_general_account_for_user(
        self, claims: dict
    ) -> Optional[GeneralAccountRead]:
        """Recupera il GeneralAccount per l'utente corrente."""
        user_id = UUID(claims["sub"])
        db_account = await self.repo.get_by_user_id(user_id=user_id)
        if db_account:
            return GeneralAccountRead.model_validate(db_account)
        return None

    async def get_general_account_with_all_data(
        self, account_id: UUID, claims: dict
    ) -> GeneralAccountWithData:
        """
        Recupera un GeneralAccount con tutte le sue relazioni (mistakes, news, ecc.)
        verificando che l'utente sia il proprietario.
        """
        user_id = UUID(claims["sub"])
        db_account = await self.repo.get_by_id_with_all_data(account_id=account_id)

        if not db_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="General account not found.",
            )

        if db_account.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not authorized to access this account.",
            )

        return GeneralAccountWithData.model_validate(db_account)