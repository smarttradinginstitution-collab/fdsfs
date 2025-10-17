# app/Repositories/trading_account_repository.py
from __future__ import annotations

from uuid import UUID
from typing import Optional, List

from sqlalchemy import select, update
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

    async def list_selected_by_general_account_id(self, general_account_id: UUID) -> List[TradingAccount]:
        """Elenca tutti i TradingAccount selezionati per un dato GeneralAccount."""
        stmt = (
            select(TradingAccount)
            .where(
                TradingAccount.general_account_id == general_account_id,
                TradingAccount.is_selected == True,
            )
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

    async def update_selection_for_user(
        self, general_account_id: UUID, selected_ids: List[UUID]
    ):
        """
        Aggiorna il flag 'is_selected' per i trading account di un utente.
        Prima imposta tutti gli account a False, poi imposta a True quelli selezionati.
        """
        # Step 1: Deseleziona tutti gli account per questo general_account
        stmt_deselect = (
            update(TradingAccount)
            .where(TradingAccount.general_account_id == general_account_id)
            .values(is_selected=False)
        )
        await self.db.execute(stmt_deselect)

        # Step 2: Seleziona solo gli account nella lista fornita
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