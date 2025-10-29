# app/Services/trading_account_service.py
from __future__ import annotations
from decimal import Decimal
from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status

from app.Repositories.trading_account_repository import TradingAccountRepository
from app.Repositories.general_account_repository import GeneralAccountRepository
from app.Repositories.trade_repository import TradeRepository  # Import TradeRepository
from app.Schemas.trading_account import TradingAccountCreate, TradingAccountRead
from app.Models.trading_account import TradingAccount
from app.Infrastructure.db import get_db


class TradingAccountService:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db
        self.repo = TradingAccountRepository(db)
        self.general_account_repo = GeneralAccountRepository(db)
        self.trade_repo = TradeRepository(db)  # Instantiate TradeRepository

    async def create_trading_account_for_user(
        self, claims: dict, account_data: TradingAccountCreate
    ) -> TradingAccountRead:
        """
        Crea un TradingAccount per l'utente corrente.
        Verifica prima che l'utente abbia un GeneralAccount.
        """
        user_id = UUID(claims["sub"])
        general_account = await self.general_account_repo.get_by_user_id(user_id)
        if not general_account:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="L'utente non ha un General Account. Creane uno prima.",
            )

        # Prima di creare, deseleziona tutti gli altri account
        await self.repo.deselect_all_accounts(general_account.id)

        db_account = await self.repo.create_trading_account(
            general_account_id=general_account.id,
            account_data=account_data,
        )

        # Imposta il nuovo account come selezionato
        db_account.is_selected = True
        await self.db.commit()
        await self.db.refresh(db_account)


        # Dopo la creazione, ricarica l'account con la relazione del broker per
        # garantire che la risposta API sia completa e non causi errori.
        stmt = (
            select(TradingAccount)
            .where(TradingAccount.id == db_account.id)
            .options(selectinload(TradingAccount.broker))
        )
        result = await self.db.execute(stmt)
        refreshed_account = result.scalar_one()

        # Costruisce la risposta arricchita, come nella funzione di elenco
        account_read = TradingAccountRead.model_validate(refreshed_account)
        if refreshed_account.broker:
            account_read.broker = refreshed_account.broker
            account_read.broker_name = refreshed_account.broker.name

        return account_read

    async def get_trading_accounts_for_user(
        self, claims: dict
    ) -> List[TradingAccountRead]:
        """
        Elenca tutti i TradingAccount per l'utente corrente, includendo i dati del broker.
        """
        user_id = UUID(claims["sub"])
        general_account = await self.general_account_repo.get_by_user_id(user_id)
        if not general_account:
            return []

        db_accounts = await self.repo.list_by_general_account_id(general_account.id)

        # Arricchisce i dati con il nome del broker
        accounts_with_broker_info = []
        for acc in db_accounts:
            account_read = TradingAccountRead.model_validate(acc)
            if acc.broker:
                # Popola sia l'oggetto broker che il campo broker_name per flessibilità nel frontend
                account_read.broker = acc.broker
                account_read.broker_name = acc.broker.name
            accounts_with_broker_info.append(account_read)

        return accounts_with_broker_info

    async def get_trading_account_by_id(
        self, account_id: UUID, claims: dict
    ) -> Optional[TradingAccountRead]:
        """
        Recupera un singolo TradingAccount per ID, verificando che appartenga all'utente.
        """
        user_id = UUID(claims["sub"])
        general_account = await self.general_account_repo.get_by_user_id(user_id)
        if not general_account:
            return None

        db_account = await self.repo.get_by_id(account_id)
        if db_account and db_account.general_account_id == general_account.id:
            return TradingAccountRead.model_validate(db_account)

        return None

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
        all_trades = await self.trade_repo.list_by_trading_account_id(account_id)

        account = await self.repo.get_by_id(account_id)
        if not account:
            # Should not happen if called from a valid context
            return

        if not all_trades:
            # Handle case with no trades by resetting PnL
            account.total_pnl = 0
            await self.db.commit()
            return

        entry_dates = [t.entry_timestamp.date() for t in all_trades if t.entry_timestamp]
        exit_dates = [t.exit_timestamp.date() for t in all_trades if t.exit_timestamp]

        if not entry_dates or not exit_dates:
            # If trades exist but have no timestamps, we can't calculate metrics
            # but we should ensure PnL is summed up.
            total_pnl = sum((Decimal(str(trade.p_l)) for trade in all_trades if trade.p_l is not None), Decimal('0.0'))
            account.total_pnl = total_pnl
            await self.db.commit()
            return

        start_date = min(entry_dates)
        end_date = max(exit_dates)

        analytics_service = AnalyticsService(self.db)
        metrics = await analytics_service.get_performance_metrics(
            trading_account_id=account_id,
            start_date=start_date,
            end_date=end_date,
        )

        account.total_pnl = metrics.stats.net_pnl
        # Add other metrics to be updated here
        await self.db.commit()

    async def update_selection_for_user(
        self, claims: dict, selected_ids: List[UUID]
    ) -> None:
        """
        Aggiorna in blocco quali Trading Accounts sono contrassegnati come 'selezionati'.
        """
        user_id = UUID(claims["sub"])
        general_account = await self.general_account_repo.get_by_user_id(user_id)
        if not general_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="General Account non trovato.",
            )

        await self.repo.bulk_update_selection(
            general_account_id=general_account.id,
            selected_ids=selected_ids,
        )