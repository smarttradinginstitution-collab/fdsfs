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

    async def recalculate_account_metrics(self, account_id: UUID) -> None:
        """
        Recalculates all performance metrics for a given trading account and
        updates the trading_account table with the new values.
        """
        from app.Services.analytics_service import AnalyticsService

        # We need to get the full date range of trades for the account
        # to ensure all metrics are calculated correctly.
        # This is a simplified approach; a more optimized version might
        # store start/end dates or use a different method to get the range.
        all_trades = await self.list_by_trading_account_id(account_id)
        if not all_trades:
            # Handle case with no trades
            account = await self.get_by_id(account_id)
            if account:
                account.total_pnl = 0
                await self.db.commit()
            return

        start_date = min(t.entry_timestamp.date() for t in all_trades if t.entry_timestamp)
        end_date = max(t.exit_timestamp.date() for t in all_trades if t.exit_timestamp)

        if not start_date or not end_date:
            # Handle case where trades have no timestamps
            return

        analytics_service = AnalyticsService(self.db)
        metrics = await analytics_service.get_performance_metrics(
            trading_account_id=account_id,
            start_date=start_date,
            end_date=end_date,
        )

        account = await self.get_by_id(account_id)
        if account:
            account.total_pnl = metrics.stats.net_pnl
            # Add other metrics to be updated here
            await self.db.commit()