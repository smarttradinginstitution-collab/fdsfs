# app/Services/trade_service.py
from __future__ import annotations

from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import Depends, HTTPException, status

from app.Repositories.trade_repository import TradeRepository
from app.Repositories.trading_account_repository import TradingAccountRepository
from app.Repositories.general_account_repository import GeneralAccountRepository
from app.Repositories.tag_repository import TagRepository
from app.Repositories.mistake_repository import MistakeRepository
from app.Repositories.playbook_repository import PlaybookRepository
from app.Repositories.news_impact_repository import NewsImpactRepository
from app.Repositories.psychology_state_repository import PsychologyStateRepository
from app.Schemas.trade import TradeCreate, TradeUpdate, TradeRead
from app.Infrastructure.db import get_db
from app.Models.trade import Trade


class TradeService:
    def _calculate_r_multiple(
        self,
        pnl: Optional[float],
        entry_price: Optional[float],
        stop_loss_price: Optional[float],
        volume: Optional[float]
    ) -> Optional[float]:
        """
        Calculates the R-multiple for a trade.
        Returns the R-multiple as a float, or None if calculation is not possible.
        """
        if pnl is None or entry_price is None or stop_loss_price is None or volume is None:
            return None

        # Avoid calculation if essential values are zero
        if volume == 0 or entry_price == stop_loss_price:
            return None

        risk_per_share = abs(entry_price - stop_loss_price)
        total_risk = risk_per_share * volume

        if total_risk == 0:
            return None # Avoid division by zero

        return pnl / total_risk

    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db
        self.repo = TradeRepository(db)
        self.trading_account_repo = TradingAccountRepository(db)
        self.general_account_repo = GeneralAccountRepository(db)
        self.tag_repo = TagRepository(db)
        self.mistake_repo = MistakeRepository(db)
        self.playbook_repo = PlaybookRepository(db)
        self.news_impact_repo = NewsImpactRepository(db)
        self.psychology_state_repo = PsychologyStateRepository(db)

    async def _validate_and_get_trading_account(self, claims: dict, trading_account_id: UUID) -> tuple[UUID, UUID]:
        """Verifica che il trading account esista e appartenga all'utente."""
        user_id = UUID(claims["sub"])
        general_account = await self.general_account_repo.get_by_user_id(user_id)
        if not general_account:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "General Account non trovato.")

        trading_account = await self.trading_account_repo.get_by_id(trading_account_id)
        if not trading_account or trading_account.general_account_id != general_account.id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Trading Account non valido o non appartenente all'utente.")

        return trading_account.id, general_account.id

    async def _get_or_create_related_entities(self, general_account_id: UUID, values: List[str], repo, upsert_method_name: str, value_field_name: str) -> list:
        """
        Funzione helper generica per recuperare o creare entità M2M tramite 'upsert'.
        """
        if not values:
            return []

        entities = []
        upsert_method = getattr(repo, upsert_method_name)
        for value in values:
            # Passa l'argomento con il nome corretto (es. name=value, title=value, state=value)
            entity = await upsert_method(general_account_id=general_account_id, **{value_field_name: value})
            entities.append(entity)
        return entities

    async def create_trade(self, claims: dict, trade_data: TradeCreate) -> TradeRead:
        """Crea un nuovo trade per l'utente, gestendo le entità correlate tramite nome."""
        _, general_account_id = await self._validate_and_get_trading_account(claims, trade_data.trading_account_id)

        # Gestione campi obsoleti per retrocompatibilità
        playbook_names = trade_data.playbooks or []
        if trade_data.setup and trade_data.setup not in playbook_names:
            playbook_names.append(trade_data.setup)

        psychology_names = trade_data.psychology_states or []
        if trade_data.emotional_state and trade_data.emotional_state not in psychology_names:
            psychology_names.append(trade_data.emotional_state)

        # Escludi i campi gestiti separatamente dal dizionario principale
        trade_dict = trade_data.model_dump(exclude={
            'tags', 'mistakes', 'playbooks', 'news_impacts', 'psychology_states',
            'setup', 'emotional_state' # Escludi anche i campi obsoleti
        })

        # Manually handle the symbol to symbol_snapshot mapping
        if 'symbol' in trade_dict:
            trade_dict['symbol_snapshot'] = trade_dict.pop('symbol')

        # Calculate R-Multiple
        trade_dict['r_multiple'] = self._calculate_r_multiple(
            pnl=trade_data.p_l,
            entry_price=trade_data.entry_price,
            stop_loss_price=trade_data.stop_loss_price,
            volume=trade_data.volume
        )


        db_trade = Trade(**trade_dict)

        # Recupera o crea le entità correlate
        db_trade.tags = await self._get_or_create_related_entities(general_account_id, trade_data.tags, self.tag_repo, "upsert_by_name", "name")
        db_trade.mistakes = await self._get_or_create_related_entities(general_account_id, trade_data.mistakes, self.mistake_repo, "upsert_by_name", "name")
        db_trade.playbooks = await self._get_or_create_related_entities(general_account_id, playbook_names, self.playbook_repo, "upsert_by_title", "title")
        db_trade.news_impacts = await self._get_or_create_related_entities(general_account_id, trade_data.news_impacts, self.news_impact_repo, "upsert_by_title", "title")
        db_trade.psychology_states = await self._get_or_create_related_entities(general_account_id, psychology_names, self.psychology_state_repo, "upsert_by_state", "state")

        self.db.add(db_trade)
        await self.db.commit()
        await self.db.refresh(db_trade, attribute_names=['tags', 'mistakes', 'playbooks', 'news_impacts', 'psychology_states', 'asset'])

        return TradeRead.from_orm(db_trade)

    async def get_trade(self, claims: dict, trade_id: UUID) -> Optional[TradeRead]:
        """Recupera un singolo trade, verificando l'appartenenza."""
        trade = await self.repo.get_trade_by_id_simple(trade_id)
        if not trade:
            return None

        await self._validate_and_get_trading_account(claims, trade.trading_account_id)

        return TradeRead.from_orm(trade)

    async def list_trades_by_trading_account(
        self,
        claims: dict,
        trading_account_id: UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[TradeRead]:
        """
        Elenca i trade per un trading account, con filtro opzionale per data.
        """
        await self._validate_and_get_trading_account(claims, trading_account_id)

        if start_date and end_date:
            trades = await self.repo.get_filtered_trades(
                trading_account_id=trading_account_id,
                start_date=start_date,
                end_date=end_date
            )
        else:
            trades = await self.repo.list_by_trading_account_id(trading_account_id)

        return [TradeRead.from_orm(trade) for trade in trades]

    async def update_trade(self, claims: dict, trade_id: UUID, update_data: TradeUpdate) -> Optional[TradeRead]:
        """Aggiorna un trade esistente."""

        db_trade = await self.repo.get_trade_by_id_simple(trade_id)
        if not db_trade:
            return None

        _, general_account_id = await self._validate_and_get_trading_account(claims, db_trade.trading_account_id)

        update_dict = update_data.model_dump(exclude_unset=True, exclude={'tag_ids', 'mistake_ids', 'playbook_ids', 'news_impact_ids', 'psychology_state_ids'})
        for key, value in update_dict.items():
            setattr(db_trade, key, value)

        # Recalculate R-Multiple if relevant fields are updated
        if any(field in update_dict for field in ['p_l', 'entry_price', 'stop_loss_price', 'volume']):
            db_trade.r_multiple = self._calculate_r_multiple(
                pnl=db_trade.p_l,
                entry_price=db_trade.entry_price,
                stop_loss_price=db_trade.stop_loss_price,
                volume=db_trade.volume
            )

        if update_data.tag_ids is not None:
            db_trade.tags = await self._get_related_entities(general_account_id, Tag, update_data.tag_ids)
        if update_data.mistake_ids is not None:
            db_trade.mistakes = await self._get_related_entities(general_account_id, Mistake, update_data.mistake_ids)
        if update_data.playbook_ids is not None:
            db_trade.playbooks = await self._get_related_entities(general_account_id, Playbook, update_data.playbook_ids)
        if update_data.news_impact_ids is not None:
            db_trade.news_impacts = await self._get_related_entities(general_account_id, NewsImpact, update_data.news_impact_ids)
        if update_data.psychology_state_ids is not None:
            db_trade.psychology_states = await self._get_related_entities(general_account_id, PsychologyState, update_data.psychology_state_ids)

        await self.db.commit()
        await self.db.refresh(db_trade, attribute_names=['tags', 'mistakes', 'playbooks', 'news_impacts', 'psychology_states', 'asset'])

        return TradeRead.from_orm(db_trade)

    async def delete_trade(self, claims: dict, trade_id: UUID) -> bool:
        """Elimina un trade, verificando l'appartenenza."""
        db_trade = await self.repo.get_trade_by_id_simple(trade_id)
        if not db_trade:
            return False

        await self._validate_and_get_trading_account(claims, db_trade.trading_account_id)

        await self.repo.delete_trade(db_trade)
        return True