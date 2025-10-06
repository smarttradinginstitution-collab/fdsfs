# app/Services/general_account_service.py
from __future__ import annotations

from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.Repositories.general_account_repository import GeneralAccountRepository
from app.Repositories.notebook_folder_repository import NotebookFolderRepository
from app.Schemas.general_account import GeneralAccountCreate, GeneralAccountRead
from app.Schemas.notebook import NotebookFolderCreate
from app.Models.enums import FolderType
from app.Infrastructure.db import get_db


class GeneralAccountService:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db
        self.repo = GeneralAccountRepository(db)
        self.notebook_folder_repo = NotebookFolderRepository(db)

    async def _create_system_folders(self, general_account_id: UUID):
        """Creates the default system folders for a new general account."""
        system_folders = [
            {"name": "All Notes", "color": "#8A94A6"},
            {"name": "Trade Notes", "color": "#4A90E2"},
            {"name": "Daily Journal", "color": "#F5A623"},
            {"name": "Session Recap", "color": "#7ED321"},
        ]

        for folder_data in system_folders:
            folder_schema = NotebookFolderCreate(**folder_data)
            await self.notebook_folder_repo.create(
                folder_in=folder_schema,
                general_account_id=general_account_id,
                folder_type=FolderType.SYSTEM,
            )

    async def create_general_account_for_user(
        self, claims: dict
    ) -> GeneralAccountRead:
        """
        Crea un GeneralAccount per l'utente corrente e popola le cartelle di sistema.
        """
        user_id = UUID(claims["sub"])
        user_email = claims["email"]

        account_create_schema = GeneralAccountCreate(label=user_email)

        db_account = await self.repo.create_general_account(
            user_id=user_id,
            account_data=account_create_schema
        )

        # After creating the account, create the system folders
        await self._create_system_folders(db_account.id)

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