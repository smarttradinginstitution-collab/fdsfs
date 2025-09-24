# app/Services/trading_account_service.py
from __future__ import annotations

from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status

from app.Repositories.trading_account_repository import TradingAccountRepository
from app.Repositories.general_account_repository import GeneralAccountRepository
from app.Schemas.trading_account import TradingAccountCreate, TradingAccountRead
from app.Infrastructure.db import get_db


class TradingAccountService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.repo = TradingAccountRepository(db)
        self.general_account_repo = GeneralAccountRepository(db)

    def create_trading_account_for_user(
        self, claims: dict, account_data: TradingAccountCreate
    ) -> TradingAccountRead:
        """
        Crea un TradingAccount per l'utente corrente.
        Verifica prima che l'utente abbia un GeneralAccount.
        """
        user_id = UUID(claims["sub"])
        # 1. Recupera il GeneralAccount dell'utente
        general_account = self.general_account_repo.get_by_user_id(user_id)
        if not general_account:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="L'utente non ha un General Account. Creane uno prima.",
            )

        # 2. Crea il TradingAccount
        db_account = self.repo.create_trading_account(
            general_account_id=general_account.id,
            account_data=account_data,
        )

        return TradingAccountRead.from_orm(db_account)

    def get_trading_accounts_for_user(
        self, claims: dict
    ) -> List[TradingAccountRead]:
        """
        Elenca tutti i TradingAccount per l'utente corrente.
        """
        user_id = UUID(claims["sub"])
        general_account = self.general_account_repo.get_by_user_id(user_id)
        if not general_account:
            return []  # Se non c'è GeneralAccount, non ci sono TradingAccount

        db_accounts = self.repo.list_by_general_account_id(general_account.id)
        return [TradingAccountRead.from_orm(acc) for acc in db_accounts]

    def get_trading_account_by_id(
        self, account_id: UUID, claims: dict
    ) -> Optional[TradingAccountRead]:
        """
        Recupera un singolo TradingAccount per ID, verificando che appartenga all'utente.
        """
        user_id = UUID(claims["sub"])
        general_account = self.general_account_repo.get_by_user_id(user_id)
        if not general_account:
            return None

        db_account = self.repo.get_by_id(account_id)
        if db_account and db_account.general_account_id == general_account.id:
            return TradingAccountRead.from_orm(db_account)

        return None