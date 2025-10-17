# app/Repositories/trade_repository.py
from __future__ import annotations

from uuid import UUID
from typing import List, Optional, Any
from datetime import date

from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy import select, func, case, Float
from sqlalchemy.ext.asyncio import AsyncSession

from app.Models.trade import Trade
from app.Models.tag import Tag
from app.Models.trades_tags import TradesTags
from app.Models.trading_account import TradingAccount
from app.Schemas.trade import TradeCreate, TradeUpdate
from app.Models.rule_playbook import RulePlaybook


class TradeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _get_trade_query(self):
        """Costruisce la query base per i trade con tutte le relazioni pre-caricate."""
        return (
            select(Trade)
            .options(
                selectinload(Trade.tags).joinedload(Tag.group),
                joinedload(Trade.mistakes),
                joinedload(Trade.playbook),
                joinedload(Trade.news_impacts),
                joinedload(Trade.psychology_states),
                joinedload(Trade.asset),
                selectinload(Trade.rules_followed),
                # Eager load the trading account to access initial_balance for ROI calculation
                joinedload(Trade.trading_account),
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
        # .unique() is mandatory here to consolidate rows for the same Trade
        # when multiple "to-many" relationships (like tags, mistakes) are joined.
        return result.unique().scalars().first()

    async def get_by_id_and_general_account(
        self, trade_id: UUID, general_account_id: UUID
    ) -> Optional[Trade]:
        """Recupera un trade per ID, assicurandosi che appartenga al general account corretto."""
        query = (
            self._get_trade_query()
            .join(Trade.trading_account)
            .where(
                Trade.id == trade_id,
                TradingAccount.general_account_id == general_account_id,
            )
        )
        result = await self.db.execute(query)
        return result.unique().scalars().first()

    async def list_by_trading_account_id(
        self, trading_account_id: UUID
    ) -> List[Trade]:
        """Elenca tutti i trade per un dato trading account."""
        query = self._get_trade_query().where(Trade.trading_account_id == trading_account_id)
        result = await self.db.execute(query)
        return result.unique().scalars().all()

    async def get_trades_for_dna_analysis(
        self,
        general_account_id: UUID,
        tag_ids: Optional[List[UUID]] = None,
        mistake_ids: Optional[List[UUID]] = None,
        psychology_state_ids: Optional[List[UUID]] = None,
        news_impact_ids: Optional[List[UUID]] = None,
    ) -> List[Trade]:
        """
        Fetches trades for a general account, dynamically filtering by any combination
        of provided label IDs.
        """
        from app.Models.trades_tags import TradesTags
        from app.Models.trades_mistakes import TradesMistakes
        from app.Models.trades_psychology import TradesPsychology
        from app.Models.trades_news_impacts import TradesNewsImpacts

        query = self._get_trade_query().join(Trade.trading_account).where(
            TradingAccount.general_account_id == general_account_id
        )

        if tag_ids:
            query = query.join(
                TradesTags.__table__, Trade.id == TradesTags.__table__.c.trade_id
            ).where(TradesTags.__table__.c.tag_id.in_(tag_ids))

        if mistake_ids:
            query = query.join(
                TradesMistakes.__table__, Trade.id == TradesMistakes.__table__.c.trade_id
            ).where(TradesMistakes.__table__.c.mistake_id.in_(mistake_ids))

        if psychology_state_ids:
            query = query.join(
                TradesPsychology.__table__, Trade.id == TradesPsychology.__table__.c.trade_id
            ).where(TradesPsychology.__table__.c.psychology_id.in_(psychology_state_ids))

        if news_impact_ids:
            query = query.join(
                TradesNewsImpacts.__table__, Trade.id == TradesNewsImpacts.__table__.c.trade_id
            ).where(TradesNewsImpacts.__table__.c.news_impact_id.in_(news_impact_ids))

        result = await self.db.execute(query)
        return result.unique().scalars().all()

    async def list_by_playbook_id(self, playbook_id: UUID) -> List[Trade]:
        """Elenca tutti i trade per un dato playbook."""
        query = self._get_trade_query().where(Trade.playbook_id == playbook_id)
        result = await self.db.execute(query)
        return result.unique().scalars().all()

    async def list_recent_by_general_account_id(
        self, general_account_id: UUID, limit: int = 20
    ) -> List[tuple[Trade, bool]]:
        """
        Lists the most recent trades for a given general account,
        and includes a boolean indicating if each trade is linked to a note.
        """
        from app.Models.note import Note
        from sqlalchemy import exists

        # Correlated subquery to check if a note exists for the trade.
        has_note_subquery = (
            select(Note.id).where(Note.trade_id == Trade.id).exists()
        ).label("is_linked_to_note")

        # The main query selects the Trade object and the boolean result of the subquery.
        # It's crucial to retain the eager loading options for related entities.
        query = (
            select(Trade, has_note_subquery)
            .options(
                joinedload(Trade.tags),
                joinedload(Trade.mistakes),
                joinedload(Trade.playbook),
                joinedload(Trade.news_impacts),
                joinedload(Trade.psychology_states),
                joinedload(Trade.asset),
            )
            .join(Trade.trading_account)
            .where(TradingAccount.general_account_id == general_account_id)
            .order_by(Trade.entry_timestamp.desc())
            .limit(limit)
        )
        result = await self.db.execute(query)

        # .unique() is mandatory here because the eager loads on collections (e.g., tags)
        # can cause duplicate rows in the result set. This was the cause of the error.
        return result.unique().all()

    async def get_filtered_trades(
        self,
        trading_account_id: UUID,
        start_date: date,
        end_date: date
    ) -> List[Trade]:
        """Recupera i trade filtrati per un intervallo di date, includendo l'intero giorno di fine."""
        from datetime import datetime, time

        start_datetime = datetime.combine(start_date, time.min)
        end_datetime = datetime.combine(end_date, time.max)

        query = self._get_trade_query().where(
            Trade.trading_account_id == trading_account_id,
            Trade.entry_timestamp >= start_datetime,
            Trade.entry_timestamp <= end_datetime
        )
        result = await self.db.execute(query)
        return result.unique().scalars().all()

    async def get_trade_by_id_simple(self, trade_id: UUID) -> Optional[Trade]:
        """Recupera un trade per ID senza controlli di appartenenza."""
        query = self._get_trade_query().where(Trade.id == trade_id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_trade_for_details_view(self, trade_id: UUID) -> Optional[Trade]:
        """
        Recupera un trade per ID, caricando esplicitamente tutte le relazioni e i campi
        necessari per la vista dettagliata e i calcoli delle metriche.
        Questo previene problemi di lazy-loading con la sessione asincrona.
        """
        """
        Recupera un trade per ID, caricando esplicitamente tutte le relazioni necessarie
        per la vista dettagliata e i calcoli, utilizzando la query di base.
        """
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

    async def update_trade_rules(self, trade: Trade, rule_ids: list[UUID]):
        """
        Aggiorna le regole 'seguite' per un trade specifico.
        Sostituisce completamente le regole esistenti con la nuova lista.
        """
        # Carica le istanze complete delle regole per assicurarsi che esistano
        rules_result = await self.db.execute(
            select(RulePlaybook).where(RulePlaybook.id.in_(rule_ids))
        )
        rules = rules_result.scalars().all()

        # Verifica che tutti gli ID richiesti corrispondano a regole esistenti
        if len(rules) != len(rule_ids):
            raise ValueError("Una o più Rule ID non sono valide.")

        # Sostituisci la lista delle regole associate al trade
        trade.rules_followed = rules

        # Il commit verrà gestito dal service layer

    async def get_trades_by_day(
        self, general_account_id: UUID, day: date
    ) -> List[Trade]:
        """Recupera tutti i trade per un dato general account in un giorno specifico."""
        from datetime import datetime, time

        start_datetime = datetime.combine(day, time.min)
        end_datetime = datetime.combine(day, time.max)

        query = (
            self._get_trade_query()
            .join(Trade.trading_account)
            .where(
                TradingAccount.general_account_id == general_account_id,
                Trade.exit_timestamp >= start_datetime,
                Trade.exit_timestamp <= end_datetime,
            )
        )
        result = await self.db.execute(query)
        return result.unique().scalars().all()

    async def get_tag_performance_stats(
        self,
        trading_account_id: UUID,
        start_date: date,
        end_date: date,
    ) -> List[Any]:
        """
        Calcola le statistiche di performance per ogni tag in un dato periodo.
        """
        from datetime import datetime, time

        start_datetime = datetime.combine(start_date, time.min)
        end_datetime = datetime.combine(end_date, time.max)

        # Define aggregate functions
        total_pnl = func.sum(Trade.p_l).label("total_pnl")
        total_trades = func.count(Trade.id).label("total_trades")

        # Calculate win rate safely, avoiding division by zero
        winning_trades = func.count(case((Trade.p_l > 0, 1)))
        win_rate = case(
            (total_trades > 0, (winning_trades.cast(Float) * 100 / total_trades)),
            else_=0.0
        ).label("win_rate")

        # Calculate average R-Multiple, handling NULLs and defaulting to 0
        avg_r_multiple = func.coalesce(func.avg(Trade.r_multiple), 0.0).label("avg_r_multiple")

        stmt = (
            select(
                Tag.id.label("tag_id"),
                Tag.name.label("tag_name"),
                Tag.color.label("tag_color"),
                total_pnl,
                total_trades,
                win_rate,
                avg_r_multiple,
            )
            .select_from(Tag)
            .join(TradesTags.__table__, Tag.id == TradesTags.__table__.c.tag_id)
            .join(Trade, Trade.id == TradesTags.__table__.c.trade_id)
            .where(
                Trade.trading_account_id == trading_account_id,
                Trade.entry_timestamp >= start_datetime,
                Trade.entry_timestamp <= end_datetime,
            )
            .group_by(Tag.id, Tag.name, Tag.color)
            .order_by(total_pnl.desc())
        )

        result = await self.db.execute(stmt)
        return result.all()