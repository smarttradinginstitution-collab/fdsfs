# app/Repositories/trading_account_repository.py
from __future__ import annotations

from uuid import UUID
from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.Models.trading_account import TradingAccount
from app.Schemas.trading_account import TradingAccountCreate


class TradingAccountRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, account_id: UUID) -> Optional[TradingAccount]:
        """Recupera un TradingAccount tramite il suo ID, includendo il broker."""
        stmt = (
            select(TradingAccount)
            .where(TradingAccount.id == account_id)
            .options(selectinload(TradingAccount.broker))
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def list_by_general_account_id(self, general_account_id: UUID) -> List[TradingAccount]:
        """Elenca tutti i TradingAccount per un dato GeneralAccount, includendo il broker."""
        stmt = (
            select(TradingAccount)
            .where(TradingAccount.general_account_id == general_account_id)
            .options(selectinload(TradingAccount.broker))
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create_trading_account(
        self, general_account_id: UUID, account_data: TradingAccountCreate
    ) -> TradingAccount:
        """Crea un nuovo TradingAccount."""
        db_account = TradingAccount(
            general_account_id=general_account_id,
            label=account_data.label,
            broker_id=account_data.broker_id,
            initial_balance=account_data.initial_balance,
            currency=account_data.currency,
        )
        self.db.add(db_account)
        await self.db.commit()
        await self.db.refresh(db_account)
        return db_account