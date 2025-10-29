# app/Repositories/trading_account_repository.py
from __future__ import annotations

from uuid import UUID
from typing import Optional, List

from sqlalchemy import select, func, Date, update
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, timedelta

from app.Models.trading_account import TradingAccount
from app.Models.trade import Trade
from app.Schemas.trading_account import TradingAccountCreate


class TradingAccountRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, account_id: UUID) -> Optional[TradingAccount]:
        """Recupera un TradingAccount tramite il suo ID, includendo il broker."""
        stmt = (
            select(TradingAccount)
            .where(TradingAccount.id == account_id)
            .options(joinedload(TradingAccount.broker))
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def list_by_general_account_id(self, general_account_id: UUID) -> List[TradingAccount]:
        """Elenca tutti i TradingAccount per un dato GeneralAccount, includendo il broker."""
        stmt = (
            select(TradingAccount)
            .where(TradingAccount.general_account_id == general_account_id)
            .options(joinedload(TradingAccount.broker))
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

    async def deselect_all_accounts(self, general_account_id: UUID):
        """Deseleziona tutti i trading account per un dato general account."""
        stmt = (
            update(TradingAccount)
            .where(TradingAccount.general_account_id == general_account_id)
            .values(is_selected=False)
        )
        await self.db.execute(stmt)
        # Il commit verrà gestito dal service layer che chiama questa funzione.

    async def bulk_update_selection(
        self, general_account_id: UUID, selected_ids: List[UUID]
    ) -> List[TradingAccount]:
        """
        Aggiorna quali account sono selezionati e restituisce l'elenco aggiornato.
        """
        # 1. Deseleziona tutti gli account
        stmt_deselect = (
            update(TradingAccount)
            .where(TradingAccount.general_account_id == general_account_id)
            .values(is_selected=False)
        )
        await self.db.execute(stmt_deselect)

        # 2. Seleziona solo gli ID forniti
        if selected_ids:
            stmt_select = (
                update(TradingAccount)
                .where(
                    TradingAccount.general_account_id == general_account_id,
                    TradingAccount.id.in_(selected_ids),
                )
                .values(is_selected=True)
            )
            await self.db.execute(stmt_select)

        # Commit delle modifiche prima di ricaricare
        await self.db.commit()

        # 3. Restituisce l'elenco aggiornato di tutti gli account
        return await self.list_by_general_account_id(general_account_id)


    async def get_daily_balances(self, account_id: UUID, start_date: date, end_date: date) -> List[dict]:
        """
        Calcola e restituisce i saldi giornalieri aggregati basati sul P/L dei trade.
        Nota: Questo simula la tabella 'trading_account_daily_balances'.
        """
        # Ottieni il saldo iniziale
        account = await self.get_by_id(account_id)
        initial_balance = account.initial_balance if account else 0

        # Query per ottenere il P/L giornaliero
        stmt = (
            select(
                func.cast(Trade.exit_timestamp, Date).label("date"),
                func.sum(Trade.p_l).label("daily_pnl")
            )
            .where(
                Trade.trading_account_id == account_id,
                Trade.exit_timestamp.between(start_date, end_date),
                Trade.status == 'closed'
            )
            .group_by(func.cast(Trade.exit_timestamp, Date))
            .order_by(func.cast(Trade.exit_timestamp, Date))
        )

        result = await self.db.execute(stmt)
        daily_pnls = result.all()

        # Calcola il saldo cumulativo
        balances = []
        cumulative_pnl = 0
        current_balance = float(initial_balance)

        # Crea un dizionario per un accesso rapido ai PNL
        pnl_map = {row.date: float(row.daily_pnl) for row in daily_pnls}

        # Itera attraverso l'intervallo di date per garantire che ogni giorno sia presente
        current_date = start_date
        while current_date <= end_date:
            daily_pnl = pnl_map.get(current_date, 0)
            current_balance += daily_pnl
            balances.append({"date": current_date, "balance": current_balance})
            current_date += timedelta(days=1)

        return balances