# app/Repositories/trading_account_repository.py
from __future__ import annotations

from uuid import UUID
from typing import Optional, List

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.Models.trading_account import TradingAccount
from app.Schemas.trading_account import TradingAccountCreate


class TradingAccountRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, account_id: UUID) -> Optional[TradingAccount]:
        """Recupera un TradingAccount tramite il suo ID."""
        return self.db.get(TradingAccount, account_id)

    def list_by_general_account_id(self, general_account_id: UUID) -> List[TradingAccount]:
        """Elenca tutti i TradingAccount per un dato GeneralAccount."""
        stmt = select(TradingAccount).where(TradingAccount.general_account_id == general_account_id)
        return self.db.scalars(stmt).all()

    def create_trading_account(
        self, general_account_id: UUID, account_data: TradingAccountCreate
    ) -> TradingAccount:
        """Crea un nuovo TradingAccount."""
        db_account = TradingAccount(
            general_account_id=general_account_id,
            label=account_data.label,
            broker_id=account_data.broker_id,
        )
        self.db.add(db_account)
        self.db.commit()
        self.db.refresh(db_account)
        return db_account