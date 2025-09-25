# app/Repositories/trade_repository.py
from __future__ import annotations

from uuid import UUID
from typing import List, Optional

from sqlalchemy.orm import joinedload
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.Models.trade import Trade
from app.Schemas.trade import TradeCreate, TradeUpdate


class TradeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _get_trade_query(self):
        """Costruisce la query base per i trade con tutte le relazioni pre-caricate."""
        return (
            select(Trade)
            .options(
                joinedload(Trade.tags),
                joinedload(Trade.mistakes),
                joinedload(Trade.playbooks),
                joinedload(Trade.news_impacts),
                joinedload(Trade.psychology_states),
                joinedload(Trade.asset),
            )
        )

    async def get_by_id(
        self, trade_id: UUID, trading_account_id: UUID
    ) -> Optional[Trade]:
        """Recupera un trade per ID, assicurandosi che appartenga al trading account corretto."""
        query = self._get_trade_query().where(
            Trade.id == trade_id,
            Trade.trading_account_id == trading_account_id
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def list_by_trading_account_id(
        self, trading_account_id: UUID
    ) -> List[Trade]:
        """Elenca tutti i trade per un dato trading account."""
        query = self._get_trade_query().where(Trade.trading_account_id == trading_account_id)
        result = await self.db.execute(query)
        return result.unique().scalars().all()

    async def get_filtered_trades(
        self,
        trading_account_id: UUID,
        start_date: date,
        end_date: date
    ) -> List[Trade]:
        """Recupera i trade filtrati per un intervallo di date."""
        query = self._get_trade_query().where(
            Trade.trading_account_id == trading_account_id,
            Trade.entry_timestamp >= start_date,
            Trade.entry_timestamp <= end_date
        )
        result = await self.db.execute(query)
        return result.unique().scalars().all()

    async def get_trade_by_id_simple(self, trade_id: UUID) -> Optional[Trade]:
        """Recupera un trade per ID senza controlli di appartenenza."""
        query = self._get_trade_query().where(Trade.id == trade_id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def add_and_commit(self, db_trade: Trade) -> Trade:
        """Aggiunge, committa e refresha un'istanza di trade."""
        self.db.add(db_trade)
        await self.db.commit()
        await self.db.refresh(db_trade)
        return db_trade

    async def commit_and_refresh(self, db_trade: Trade) -> Trade:
        """Committa le modifiche e refresha l'istanza."""
        await self.db.commit()
        await self.db.refresh(db_trade)
        return db_trade

    async def delete_trade(self, db_trade: Trade) -> None:
        """Elimina un trade."""
        await self.db.delete(db_trade)
        await self.db.commit()