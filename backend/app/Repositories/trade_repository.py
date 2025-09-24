# app/Repositories/trade_repository.py
from __future__ import annotations

from uuid import UUID
from typing import List, Optional

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select

from app.Models.trade import Trade
from app.Schemas.trade import TradeCreate, TradeUpdate


class TradeRepository:
    def __init__(self, db: Session):
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

    def get_by_id(
        self, trade_id: UUID, trading_account_id: UUID
    ) -> Optional[Trade]:
        """Recupera un trade per ID, assicurandosi che appartenga al trading account corretto."""
        query = self._get_trade_query().where(
            Trade.id == trade_id,
            Trade.trading_account_id == trading_account_id
        )
        return self.db.scalars(query).first()

    def list_by_trading_account_id(
        self, trading_account_id: UUID
    ) -> List[Trade]:
        """Elenca tutti i trade per un dato trading account."""
        query = self._get_trade_query().where(Trade.trading_account_id == trading_account_id)
        return self.db.scalars(query).all()

    def create_trade(self, trade_data: TradeCreate) -> Trade:
        """Crea un nuovo trade."""

        # Estrai gli ID delle relazioni
        tag_ids = trade_data.tag_ids or []
        mistake_ids = trade_data.mistake_ids or []
        playbook_ids = trade_data.playbook_ids or []
        news_impact_ids = trade_data.news_impact_ids or []
        psychology_state_ids = trade_data.psychology_state_ids or []

        # Crea l'oggetto Trade senza le relazioni M2M
        trade_dict = trade_data.dict(exclude={'tag_ids', 'mistake_ids', 'playbook_ids', 'news_impact_ids', 'psychology_state_ids'})
        db_trade = Trade(**trade_dict)

        # Aggiungi le relazioni (assumendo che gli ID siano validi)
        # La validazione avverrà nel service
        # NOTA: Questo richiede che i modelli corrispondenti (Tag, Mistake, etc.) siano caricati nella sessione
        # o che vengano gestiti correttamente da SQLAlchemy. Il Service si occuperà di questo.

        self.db.add(db_trade)
        self.db.commit()
        self.db.refresh(db_trade)

        # La gestione effettiva dei link avverrà nel service
        return db_trade

    def update_trade(
        self, db_trade: Trade, update_data: TradeUpdate
    ) -> Trade:
        """Aggiorna un trade esistente."""

        update_dict = update_data.dict(exclude_unset=True, exclude={'tag_ids', 'mistake_ids', 'playbook_ids', 'news_impact_ids', 'psychology_state_ids'})

        for key, value in update_dict.items():
            setattr(db_trade, key, value)

        self.db.commit()
        self.db.refresh(db_trade)

        # La gestione dei link M2M avverrà nel service
        return db_trade

    def delete_trade(self, db_trade: Trade) -> None:
        """Elimina un trade."""
        self.db.delete(db_trade)
        self.db.commit()