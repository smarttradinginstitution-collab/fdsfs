# app/Repositories/general_account_repository.py
from __future__ import annotations

from uuid import UUID
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from app.Models.general_account import GeneralAccount
from app.Schemas.general_account import GeneralAccountCreate


class GeneralAccountRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: UUID) -> Optional[GeneralAccount]:
        """Recupera un GeneralAccount tramite user_id."""
        stmt = select(GeneralAccount).where(GeneralAccount.user_id == user_id)
        return self.db.scalars(stmt).first()

    def create_general_account(
        self, user_id: UUID, account_data: GeneralAccountCreate
    ) -> GeneralAccount:
        """
        Crea un nuovo GeneralAccount per un utente.
        Se l'utente ha già un account, lo restituisce senza crearne uno nuovo.
        """
        # Verifica se esiste già un account
        existing_account = self.get_by_user_id(user_id)
        if existing_account:
            return existing_account

        # Crea un nuovo account
        db_account = GeneralAccount(
            user_id=user_id,
            label=account_data.label
        )
        self.db.add(db_account)
        try:
            self.db.commit()
            self.db.refresh(db_account)
        except IntegrityError:
            self.db.rollback()
            # Potrebbe accadere in caso di race condition, quindi riproviamo a prenderlo
            existing_account = self.get_by_user_id(user_id)
            if existing_account:
                return existing_account
            else:
                # Se ancora non esiste, rilancia l'eccezione originale
                raise

        return db_account