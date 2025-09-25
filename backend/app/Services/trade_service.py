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
from app.Schemas.trade import TradeCreate, TradeUpdate, TradeRead
from app.Infrastructure.db import get_db
from app.Models.trade import Trade
from app.Models.tag import Tag
from app.Models.mistake import Mistake
from app.Models.playbook import Playbook
from app.Models.news_impact import NewsImpact
from app.Models.psychology_state import PsychologyState


class TradeService:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db
        self.repo = TradeRepository(db)
        self.trading_account_repo = TradingAccountRepository(db)
        self.general_account_repo = GeneralAccountRepository(db)

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

    async def _get_related_entities(self, general_account_id: UUID, model, ids: List[UUID]) -> list:
        """Funzione helper per recuperare entità M2M e validare la loro appartenenza."""
        if not ids:
            return []

        query = select(model).where(
            model.general_account_id == general_account_id,
            model.id.in_(ids)
        )
        result = await self.db.execute(query)
        entities = result.scalars().all()

        if len(entities) != len(set(ids)):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Uno o più ID per {model.__name__} non sono validi o non appartengono al tuo account.")

        return entities

    async def create_trade(self, claims: dict, trade_data: TradeCreate) -> TradeRead:
        """Crea un nuovo trade per l'utente."""

        _, general_account_id = await self._validate_and_get_trading_account(claims, trade_data.trading_account_id)

        trade_dict = trade_data.model_dump(exclude={'tag_ids', 'mistake_ids', 'playbook_ids', 'news_impact_ids', 'psychology_state_ids'})
        db_trade = Trade(**trade_dict)

        db_trade.tags = await self._get_related_entities(general_account_id, Tag, trade_data.tag_ids)
        db_trade.mistakes = await self._get_related_entities(general_account_id, Mistake, trade_data.mistake_ids)
        db_trade.playbooks = await self._get_related_entities(general_account_id, Playbook, trade_data.playbook_ids)
        db_trade.news_impacts = await self._get_related_entities(general_account_id, NewsImpact, trade_data.news_impact_ids)
        db_trade.psychology_states = await self._get_related_entities(general_account_id, PsychologyState, trade_data.psychology_state_ids)

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

    async def list_trades_by_trading_account(self, claims: dict, trading_account_id: UUID) -> List[TradeRead]:
        """Elenca tutti i trade per un trading account specifico, verificando l'appartenenza."""
        await self._validate_and_get_trading_account(claims, trading_account_id)

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