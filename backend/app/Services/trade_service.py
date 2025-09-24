# app/Services/trade_service.py
from __future__ import annotations

from uuid import UUID
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status

from app.Repositories.trade_repository import TradeRepository
from app.Repositories.trading_account_repository import TradingAccountRepository
from app.Repositories.general_account_repository import GeneralAccountRepository
from app.Schemas.trade import TradeCreate, TradeUpdate, TradeRead
from app.Infrastructure.db import get_db
from app.Models.auth_user import AuthUser
from app.Models.trade import Trade
from app.Models.tag import Tag
from app.Models.mistake import Mistake
from app.Models.playbook import Playbook
from app.Models.news_impact import NewsImpact
from app.Models.psychology_state import PsychologyState


class TradeService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.repo = TradeRepository(db)
        self.trading_account_repo = TradingAccountRepository(db)
        self.general_account_repo = GeneralAccountRepository(db)

    def _validate_and_get_trading_account(self, user: AuthUser, trading_account_id: UUID) -> tuple[UUID, UUID]:
        """Verifica che il trading account esista e appartenga all'utente."""
        general_account = self.general_account_repo.get_by_user_id(user.id)
        if not general_account:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "General Account non trovato.")

        trading_account = self.trading_account_repo.get_by_id(trading_account_id)
        if not trading_account or trading_account.general_account_id != general_account.id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Trading Account non valido o non appartenente all'utente.")

        return trading_account.id, general_account.id

    def _get_related_entities(self, general_account_id: UUID, model, ids: List[UUID]) -> list:
        """Funzione helper per recuperare entità M2M e validare la loro appartenenza."""
        if not ids:
            return []

        query = self.db.query(model).filter(
            model.general_account_id == general_account_id,
            model.id.in_(ids)
        )
        entities = query.all()

        if len(entities) != len(set(ids)):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Uno o più ID per {model.__name__} non sono validi o non appartengono al tuo account.")

        return entities

    def create_trade(self, user: AuthUser, trade_data: TradeCreate) -> TradeRead:
        """Crea un nuovo trade per l'utente."""

        _, general_account_id = self._validate_and_get_trading_account(user, trade_data.trading_account_id)

        tags = self._get_related_entities(general_account_id, Tag, trade_data.tag_ids)
        mistakes = self._get_related_entities(general_account_id, Mistake, trade_data.mistake_ids)
        playbooks = self._get_related_entities(general_account_id, Playbook, trade_data.playbook_ids)
        news_impacts = self._get_related_entities(general_account_id, NewsImpact, trade_data.news_impact_ids)
        psychology_states = self._get_related_entities(general_account_id, PsychologyState, trade_data.psychology_state_ids)

        trade_dict = trade_data.dict(exclude={'tag_ids', 'mistake_ids', 'playbook_ids', 'news_impact_ids', 'psychology_state_ids'})
        db_trade = Trade(**trade_dict)

        db_trade.tags = tags
        db_trade.mistakes = mistakes
        db_trade.playbooks = playbooks
        db_trade.news_impacts = news_impacts
        db_trade.psychology_states = psychology_states

        self.db.add(db_trade)
        self.db.commit()
        self.db.refresh(db_trade)

        return TradeRead.from_orm(db_trade)

    def get_trade(self, user: AuthUser, trade_id: UUID) -> Optional[TradeRead]:
        """Recupera un singolo trade, verificando l'appartenenza."""
        # Trova il trade tramite ID
        trade = self.repo.db.query(Trade).filter(Trade.id == trade_id).first()
        if not trade:
            return None

        # Verifica l'appartenenza
        self._validate_and_get_trading_account(user, trade.trading_account_id)

        return TradeRead.from_orm(trade)

    def list_trades_by_trading_account(self, user: AuthUser, trading_account_id: UUID) -> List[TradeRead]:
        """Elenca tutti i trade per un trading account specifico, verificando l'appartenenza."""
        self._validate_and_get_trading_account(user, trading_account_id)

        trades = self.repo.list_by_trading_account_id(trading_account_id)
        return [TradeRead.from_orm(trade) for trade in trades]

    def update_trade(self, user: AuthUser, trade_id: UUID, update_data: TradeUpdate) -> Optional[TradeRead]:
        """Aggiorna un trade esistente."""

        db_trade = self.repo.db.query(Trade).filter(Trade.id == trade_id).first()
        if not db_trade:
            return None

        trading_account_id, general_account_id = self._validate_and_get_trading_account(user, db_trade.trading_account_id)

        # Aggiorna i campi semplici
        update_dict = update_data.dict(exclude_unset=True, exclude={'tag_ids', 'mistake_ids', 'playbook_ids', 'news_impact_ids', 'psychology_state_ids'})
        for key, value in update_dict.items():
            setattr(db_trade, key, value)

        # Aggiorna le relazioni M2M se fornite nel payload
        if update_data.tag_ids is not None:
            db_trade.tags = self._get_related_entities(general_account_id, Tag, update_data.tag_ids)
        if update_data.mistake_ids is not None:
            db_trade.mistakes = self._get_related_entities(general_account_id, Mistake, update_data.mistake_ids)
        if update_data.playbook_ids is not None:
            db_trade.playbooks = self._get_related_entities(general_account_id, Playbook, update_data.playbook_ids)
        if update_data.news_impact_ids is not None:
            db_trade.news_impacts = self._get_related_entities(general_account_id, NewsImpact, update_data.news_impact_ids)
        if update_data.psychology_state_ids is not None:
            db_trade.psychology_states = self._get_related_entities(general_account_id, PsychologyState, update_data.psychology_state_ids)

        self.db.commit()
        self.db.refresh(db_trade)

        return TradeRead.from_orm(db_trade)

    def delete_trade(self, user: AuthUser, trade_id: UUID) -> bool:
        """Elimina un trade, verificando l'appartenenza."""
        db_trade = self.repo.db.query(Trade).filter(Trade.id == trade_id).first()
        if not db_trade:
            return False

        self._validate_and_get_trading_account(user, db_trade.trading_account_id)

        self.repo.delete_trade(db_trade)
        return True