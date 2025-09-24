# app/Services/general_account_service.py
from __future__ import annotations

from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import Depends

from app.Repositories.general_account_repository import GeneralAccountRepository
from app.Schemas.general_account import GeneralAccountCreate, GeneralAccountRead
from app.Infrastructure.db import get_db
from app.Models.auth_user import AuthUser


class GeneralAccountService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.repo = GeneralAccountRepository(db)

    def create_general_account_for_user(
        self, current_user: AuthUser
    ) -> GeneralAccountRead:
        """
        Crea un GeneralAccount per l'utente corrente, usando la sua email come label.
        """
        account_create_schema = GeneralAccountCreate(label=current_user.email)

        db_account = self.repo.create_general_account(
            user_id=current_user.id,
            account_data=account_create_schema
        )

        return GeneralAccountRead.from_orm(db_account)

    def get_general_account_for_user(
        self, current_user: AuthUser
    ) -> Optional[GeneralAccountRead]:
        """Recupera il GeneralAccount per l'utente corrente."""
        db_account = self.repo.get_by_user_id(user_id=current_user.id)
        if db_account:
            return GeneralAccountRead.from_orm(db_account)
        return None