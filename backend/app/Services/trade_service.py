# app/Services/trade_service.py
from __future__ import annotations

from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import Depends, HTTPException, status
from datetime import date

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
from decimal import Decimal
from app.Models.trade import Trade
from app.Models.tag import Tag
from app.Models.mistake import Mistake
from app.Models.playbook import Playbook
from app.Models.news_impact import NewsImpact
from app.Models.psychology_state import PsychologyState
from app.Services.metrics.trade_enricher import calculate_advanced_trade_metrics


class TradeService:
    # All calculation logic is now centralized in `calculate_advanced_trade_metrics`.
    # The private methods _calculate_r_multiple, _calculate_trade_risk,
    # and _calculate_net_roi have been removed.

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
            entity = await upsert_method(general_account_id=general_account_id, **{value_field_name: value})
            entities.append(entity)
        return entities

    async def _get_related_entities(self, general_account_id: UUID, model_class, entity_ids: List[UUID]) -> list:
        """
        Recupera un elenco di entità correlate tramite i loro ID, assicurando che appartengano
        al general account corretto.
        """
        if not entity_ids:
            return []

        stmt = select(model_class).where(
            model_class.id.in_(entity_ids),
            model_class.general_account_id == general_account_id
        )
        result = await self.db.execute(stmt)
        entities = result.scalars().all()

        if len(entities) != len(set(entity_ids)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Uno o più ID di {model_class.__name__} non sono validi o non appartengono all'utente."
            )
        return entities

    async def create_trade(self, claims: dict, trade_data: TradeCreate) -> TradeRead:
        """Crea un nuovo trade per l'utente, calcolando e salvando l'R-Multiple corretto."""
        trading_account_id, general_account_id = await self._validate_and_get_trading_account(claims, trade_data.trading_account_id)

        # Recupera il trading account per ottenere il bilancio iniziale per i calcoli
        trading_account = await self.trading_account_repo.get_by_id(trading_account_id)
        if not trading_account:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Trading Account non trovato per il calcolo delle metriche.")

        playbook_name = trade_data.playbook or trade_data.setup
        psychology_names = trade_data.psychology_states or []
        if trade_data.emotional_state and trade_data.emotional_state not in psychology_names:
            psychology_names.append(trade_data.emotional_state)

        trade_dict = trade_data.model_dump(exclude={
            'tags', 'mistakes', 'playbook', 'news_impacts', 'psychology_states',
            'setup', 'emotional_state'
        })

        if 'symbol' in trade_dict:
            trade_dict['symbol_snapshot'] = trade_dict.pop('symbol')

        # Calcola l'R-Multiple corretto da salvare nel DB
        advanced_metrics = calculate_advanced_trade_metrics(
            trade_data=trade_dict,
            initial_balance=Decimal(trading_account.initial_balance or '0.0')
        )
        trade_dict['r_multiple'] = advanced_metrics.get("realized_r_multiple")

        db_trade = Trade(**trade_dict)

        if playbook_name:
            db_trade.playbook = await self.playbook_repo.upsert_by_title(general_account_id, title=playbook_name)

        db_trade.tags = await self._get_or_create_related_entities(general_account_id, trade_data.tags, self.tag_repo, "upsert_by_name", "name")
        db_trade.mistakes = await self._get_or_create_related_entities(general_account_id, trade_data.mistakes, self.mistake_repo, "upsert_by_name", "name")
        db_trade.news_impacts = await self._get_or_create_related_entities(general_account_id, trade_data.news_impacts, self.news_impact_repo, "upsert_by_title", "title")
        db_trade.psychology_states = await self._get_or_create_related_entities(general_account_id, psychology_names, self.psychology_state_repo, "upsert_by_state", "state")

        self.db.add(db_trade)
        await self.db.commit()
        await self.db.refresh(db_trade, attribute_names=['tags', 'mistakes', 'playbook', 'news_impacts', 'psychology_states', 'asset'])

        return TradeRead.from_orm(db_trade)

    async def get_trade(self, claims: dict, trade_id: UUID) -> Optional[TradeRead]:
        """Recupera un singolo trade, verificando l'appartenenza e arricchendolo con dati calcolati."""
        # Utilizza il nuovo metodo del repository per garantire che tutti i dati siano caricati
        trade = await self.repo.get_trade_for_details_view(trade_id)
        if not trade:
            return None

        trading_account_id, _ = await self._validate_and_get_trading_account(claims, trade.trading_account_id)

        trading_account = await self.trading_account_repo.get_by_id(trading_account_id)
        if not trading_account:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Dettagli del conto di trading non trovati.")

        trade_data_dict = {
            "entry_price": trade.entry_price, "exit_price": trade.exit_price,
            "stop_loss_price": trade.stop_loss_price, "p_l": trade.p_l,
            "direction": trade.direction.value if trade.direction else None
        }

        advanced_metrics = calculate_advanced_trade_metrics(
            trade_data=trade_data_dict,
            initial_balance=Decimal(trading_account.initial_balance or '0.0')
        )

        trade_read = TradeRead.from_orm(trade)
        trade_read.trade_risk = advanced_metrics.get("trade_risk")
        trade_read.net_roi = advanced_metrics.get("net_roi")
        trade_read.r_multiple = advanced_metrics.get("realized_r_multiple")

        return trade_read

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
        """Aggiorna un trade esistente e ricalcola le metriche se necessario."""
        db_trade = await self.repo.get_trade_by_id_simple(trade_id)
        if not db_trade:
            return None

        trading_account_id, general_account_id = await self._validate_and_get_trading_account(claims, db_trade.trading_account_id)

        update_dict = update_data.model_dump(exclude_unset=True, exclude={'tag_ids', 'mistake_ids', 'playbook_id', 'news_impacts', 'psychology_state_ids'})
        for key, value in update_dict.items():
            setattr(db_trade, key, value)

        recalculation_fields = ['p_l', 'entry_price', 'stop_loss_price', 'exit_price']
        if any(field in update_dict for field in recalculation_fields):
            trading_account = await self.trading_account_repo.get_by_id(trading_account_id)
            if not trading_account:
                raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Dettagli del conto di trading non trovati per ricalcolo.")

            trade_data_for_calc = {
                "entry_price": db_trade.entry_price, "exit_price": db_trade.exit_price,
                "stop_loss_price": db_trade.stop_loss_price, "p_l": db_trade.p_l,
                "direction": db_trade.direction.value if db_trade.direction else None
            }
            advanced_metrics = calculate_advanced_trade_metrics(
                trade_data=trade_data_for_calc,
                initial_balance=Decimal(trading_account.initial_balance or '0.0')
            )
            db_trade.r_multiple = advanced_metrics.get("realized_r_multiple")

        if "playbook_id" in update_data.model_fields_set:
            if update_data.playbook_id is None:
                db_trade.playbook_id = None
            else:
                playbook = await self.playbook_repo.get_by_id(update_data.playbook_id, general_account_id)
                if not playbook:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playbook not found")
                db_trade.playbook_id = playbook.id

        if update_data.tag_ids is not None:
            db_trade.tags = await self._get_related_entities(general_account_id, Tag, update_data.tag_ids)
        if update_data.mistake_ids is not None:
            db_trade.mistakes = await self._get_related_entities(general_account_id, Mistake, update_data.mistake_ids)
        if update_data.news_impact_ids is not None:
            db_trade.news_impacts = await self._get_related_entities(general_account_id, NewsImpact, update_data.news_impact_ids)
        if update_data.psychology_state_ids is not None:
            db_trade.psychology_states = await self._get_related_entities(general_account_id, PsychologyState, update_data.psychology_state_ids)

        await self.db.commit()
        await self.db.refresh(db_trade, attribute_names=['tags', 'mistakes', 'playbook', 'news_impacts', 'psychology_states', 'asset'])

        return TradeRead.from_orm(db_trade)

    async def delete_trade(self, claims: dict, trade_id: UUID) -> bool:
        """Elimina un trade, verificando l'appartenenza."""
        db_trade = await self.repo.get_trade_by_id_simple(trade_id)
        if not db_trade:
            return False

        await self._validate_and_get_trading_account(claims, db_trade.trading_account_id)

        await self.repo.delete_trade(db_trade)
        return True