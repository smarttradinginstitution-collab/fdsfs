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
from app.Services.trading_account_service import TradingAccountService
from app.Schemas.trade import (
    TradeCreate, TradeUpdate, TradeRead, TradeReviewUpdate, TradeWithDataRead
)
from app.Models.enums import TradeDirection
from app.Schemas.tag import TagRead
from app.Infrastructure.db import get_db
from decimal import Decimal
from app.Models.trade import Trade
from app.Models.tag import Tag
from app.Models.mistake import Mistake
from app.Models.playbook import Playbook
from app.Models.news_impact import NewsImpact
from app.Models.psychology_state import PsychologyState
from app.Models.rule_playbook import RulePlaybook
from app.Services.metrics.trade_enricher import enrich_trade_with_all_metrics
from app.Schemas.analytics import TradeFinancialSummary


class TradeService:
    # All calculation logic is now centralized in `enrich_trade_with_all_metrics`.
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

        stmt = select(model_class).where(model_class.id.in_(entity_ids))

        # FIX: Special handling for models linking to general_account_id via a group
        if model_class == Tag:
            from app.Models.tags_group import TagsGroup
            stmt = stmt.join(TagsGroup).where(TagsGroup.general_account_id == general_account_id)
        elif model_class == NewsImpact:
            from app.Models.news_impacts_group import NewsImpactsGroup
            stmt = stmt.join(NewsImpactsGroup).where(NewsImpactsGroup.general_account_id == general_account_id)
        else:
            stmt = stmt.where(model_class.general_account_id == general_account_id)

        result = await self.db.execute(stmt)
        entities = result.scalars().all()

        if len(entities) != len(set(entity_ids)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Uno o più ID di {model_class.__name__} non sono validi o non appartengono all'utente."
            )
        return entities

    async def create_trade(self, claims: dict, trade_data: TradeCreate) -> TradeRead:
        """Crea un nuovo trade per l'utente, gestendo le relazioni M2M tramite ID."""
        trading_account_id, general_account_id = await self._validate_and_get_trading_account(claims, trade_data.trading_account_id)

        trading_account = await self.trading_account_repo.get_by_id(trading_account_id)
        if not trading_account:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Trading Account non trovato.")

        # Estrai i dati di base del trade e gli ID delle relazioni
        trade_dict = trade_data.model_dump(exclude={
            'tag_ids', 'mistake_ids', 'playbook_id', 'news_impact_ids',
            'psychology_state_ids', 'rules_followed_ids'
        })

        # Arricchisci il trade con metriche calcolate
        all_metrics = enrich_trade_with_all_metrics(
            trade_data=trade_dict,
            initial_balance=Decimal(trading_account.initial_balance or '0.0')
        )
        r_multiple = all_metrics.get("realized_r_multiple")
        trade_dict['r_multiple'] = float(r_multiple) if r_multiple is not None else None

        # Recupera le entità correlate dagli ID forniti
        tags = await self._get_related_entities(general_account_id, Tag, trade_data.tag_ids)
        mistakes = await self._get_related_entities(general_account_id, Mistake, trade_data.mistake_ids)
        news_impacts = await self._get_related_entities(general_account_id, NewsImpact, trade_data.news_impact_ids)
        psychology_states = await self._get_related_entities(general_account_id, PsychologyState, trade_data.psychology_state_ids)

        # Gestione playbook (to-one)
        playbook = None
        if trade_data.playbook_id:
            playbook = await self.playbook_repo.get_by_id(trade_data.playbook_id)
            if not playbook or playbook.general_account_id != general_account_id:
                 raise HTTPException(status.HTTP_400_BAD_REQUEST, "Playbook non valido o non appartenente all'utente.")

        # Gestione regole (M2M)
        rules_followed = []
        if trade_data.rules_followed_ids:
            rules_result = await self.db.execute(
                select(RulePlaybook).where(RulePlaybook.id.in_(trade_data.rules_followed_ids))
            )
            rules_followed = rules_result.scalars().all()
            if len(rules_followed) != len(set(trade_data.rules_followed_ids)):
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "Uno o più ID di regole non sono validi.")


        # Crea l'istanza del trade includendo le relazioni
        db_trade = Trade(
            **trade_dict,
            tags=tags,
            mistakes=mistakes,
            playbook=playbook,
            news_impacts=news_impacts,
            psychology_states=psychology_states,
            rules_followed=rules_followed
        )

        self.db.add(db_trade)
        await self.db.commit()
        await self.db.refresh(db_trade, attribute_names=['tags', 'mistakes', 'playbook', 'news_impacts', 'psychology_states', 'asset', 'rules_followed'])

        # Recalculate account metrics
        trading_account_service = TradingAccountService(self.db)
        await trading_account_service.recalculate_account_metrics(trading_account_id)

        return TradeRead.model_validate(db_trade)

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
            "entry_price": trade.entry_price,
            "exit_price": trade.exit_price,
            "stop_loss_price": trade.stop_loss_price,
            "take_profit_price": trade.take_profit_price,
            "p_l": trade.p_l,
            "direction": trade.direction.value if isinstance(trade.direction, TradeDirection) else trade.direction,
            "lowest_price_during_trade": trade.lowest_price_during_trade,
            "highest_price_during_trade": trade.highest_price_during_trade,
            "position_size": trade.position_size,
        }

        all_metrics = enrich_trade_with_all_metrics(
            trade_data=trade_data_dict,
            initial_balance=Decimal(trading_account.initial_balance or '0.0')
        )

        trade_read = TradeRead.model_validate(trade)

        # Populate all calculated fields, converting Decimal to float for serialization
        # and mapping dictionary keys to the correct Pydantic model fields.
        mappings = {
            "realized_r_multiple": "r_multiple",
            "trade_risk": "trade_risk",
            "net_roi": "net_roi",
            "mae_usd": "mae_usd",
            "mfe_usd": "mfe_usd",
            "planned_target": "planned_target",
            "planned_r_multiple": "planned_r_multiple",
        }
        for metric_key, model_field in mappings.items():
            value = all_metrics.get(metric_key)
            setattr(trade_read, model_field, float(value) if value is not None else None)

        return trade_read


    async def get_trade_with_all_data(self, claims: dict, trade_id: UUID) -> Optional[TradeWithDataRead]:
        """
        Recupera un singolo trade con tutte le sue relazioni, verificando l'appartenenza
        e arricchendolo con dati calcolati.
        """
        user_id = UUID(claims["sub"])
        general_account = await self.general_account_repo.get_by_user_id(user_id)
        if not general_account:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "General Account non trovato.")

        trade = await self.repo.get_by_id_with_all_data(trade_id, general_account.id)
        if not trade:
            return None # O solleva 404 se il trade non esiste o non appartiene all'utente

        # L'arricchimento dei dati calcolati richiede il trading_account, che è già caricato
        trading_account = trade.trading_account
        if not trading_account:
             raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Dettagli del conto di trading non trovati.")

        trade_data_dict = {
            "entry_price": trade.entry_price,
            "exit_price": trade.exit_price,
            "stop_loss_price": trade.stop_loss_price,
            "take_profit_price": trade.take_profit_price,
            "p_l": trade.p_l,
            "direction": trade.direction.value if isinstance(trade.direction, TradeDirection) else trade.direction,
            "lowest_price_during_trade": trade.lowest_price_during_trade,
            "highest_price_during_trade": trade.highest_price_during_trade,
            "position_size": trade.position_size,
        }

        all_metrics = enrich_trade_with_all_metrics(
            trade_data=trade_data_dict,
            initial_balance=Decimal(trading_account.initial_balance or '0.0')
        )

        trade_read = TradeWithDataRead.model_validate(trade)

        mappings = {
            "realized_r_multiple": "r_multiple",
            "trade_risk": "trade_risk",
            "net_roi": "net_roi",
            "mae_usd": "mae_usd",
            "mfe_usd": "mfe_usd",
            "planned_target": "planned_target",
            "planned_r_multiple": "planned_r_multiple",
        }
        for metric_key, model_field in mappings.items():
            value = all_metrics.get(metric_key)
            setattr(trade_read, model_field, float(value) if value is not None else None)

        return trade_read


    async def get_recent_trades(self, claims: dict) -> List[TradeRead]:
        """
        Retrieves the 20 most recent trades for the user's general account,
        indicating whether each trade is linked to a note.
        """
        user_id = UUID(claims["sub"])
        general_account = await self.general_account_repo.get_by_user_id(user_id)
        if not general_account:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "General Account not found.")

        # The repository now returns a list of (Trade, bool) tuples
        trade_results = await self.repo.list_recent_by_general_account_id(
            general_account_id=general_account.id, limit=20
        )

        # Process the results to populate the Pydantic schema
        response_trades = []
        for trade, is_linked in trade_results:
            trade_read = TradeRead.model_validate(trade)
            trade_read.is_linked_to_note = is_linked
            response_trades.append(trade_read)

        return response_trades

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

        return [TradeRead.model_validate(trade) for trade in trades]

    async def update_trade(self, claims: dict, trade_id: UUID, update_data: TradeUpdate) -> Optional[TradeRead]:
        """Aggiorna un trade esistente e ricalcola le metriche se necessario."""
        db_trade = await self.repo.get_trade_by_id_simple(trade_id)
        if not db_trade:
            return None

        trading_account_id, general_account_id = await self._validate_and_get_trading_account(claims, db_trade.trading_account_id)

        update_dict = update_data.model_dump(exclude_unset=True, exclude={'tag_ids', 'mistake_ids', 'playbook_id', 'news_impacts', 'psychology_state_ids'})
        for key, value in update_dict.items():
            setattr(db_trade, key, value)

        # Recalculate Net P/L if gross_p_l, fees, or commissions change
        pl_recalculation_needed = any(field in update_dict for field in ['gross_p_l', 'fees', 'commissions'])
        if pl_recalculation_needed:
            gross_pnl = Decimal(str(db_trade.gross_p_l)) if db_trade.gross_p_l is not None else Decimal('0.0')
            fees = Decimal(str(db_trade.fees)) if db_trade.fees is not None else Decimal('0.0')
            commissions = Decimal(str(db_trade.commissions)) if db_trade.commissions is not None else Decimal('0.0')
            db_trade.p_l = gross_pnl - fees - commissions

        # Recalculate R-Multiple if P/L was recalculated or if other relevant fields changed
        r_multiple_recalc_fields = ['p_l', 'entry_price', 'stop_loss_price', 'exit_price']
        if pl_recalculation_needed or any(field in update_dict for field in r_multiple_recalc_fields):
            trading_account = await self.trading_account_repo.get_by_id(trading_account_id)
            if not trading_account:
                raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Dettagli del conto di trading non trovati per ricalcolo.")

            trade_data_for_calc = {
                "entry_price": db_trade.entry_price, "exit_price": db_trade.exit_price,
                "stop_loss_price": db_trade.stop_loss_price, "p_l": db_trade.p_l,
                "direction": db_trade.direction.value if isinstance(db_trade.direction, TradeDirection) else db_trade.direction
            }
            all_metrics = enrich_trade_with_all_metrics(
                trade_data=trade_data_for_calc,
                initial_balance=Decimal(trading_account.initial_balance or '0.0')
            )
            r_multiple = all_metrics.get("realized_r_multiple")
            db_trade.r_multiple = float(r_multiple) if r_multiple is not None else None

        if "playbook_id" in update_data.model_fields_set:
            if update_data.playbook_id is None:
                db_trade.playbook_id = None
            else:
                playbook = await self.playbook_repo.get_by_id(update_data.playbook_id)
                if not playbook or playbook.general_account_id != general_account_id:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playbook not found or does not belong to the user.")
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
        await self.db.refresh(db_trade, attribute_names=['tags', 'mistakes', 'playbook', 'news_impacts', 'psychology_states', 'asset', 'rules_followed'])

        # Recalculate account metrics
        trading_account_service = TradingAccountService(self.db)
        await trading_account_service.recalculate_account_metrics(trading_account_id)

        return TradeRead.model_validate(db_trade)

    async def update_review_status(self, claims: dict, trade_id: UUID, update_data: TradeReviewUpdate) -> TradeRead:
        """Aggiorna lo stato di revisione di un trade."""
        db_trade = await self.repo.get_trade_by_id_simple(trade_id)
        if not db_trade:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trade not found")

        await self._validate_and_get_trading_account(claims, db_trade.trading_account_id)

        updated_trade = await self.repo.update_review_status(db_trade, update_data.is_reviewed)

        await self.repo.commit_and_refresh(updated_trade)

        return TradeRead.model_validate(updated_trade)

    async def delete_trade(self, claims: dict, trade_id: UUID) -> bool:
        """Elimina un trade, verificando l'appartenenza."""
        db_trade = await self.repo.get_trade_by_id_simple(trade_id)
        if not db_trade:
            return False

        trading_account_id = db_trade.trading_account_id
        await self._validate_and_get_trading_account(claims, trading_account_id)

        await self.repo.delete_trade(db_trade)

        # Recalculate account metrics
        trading_account_service = TradingAccountService(self.db)
        await trading_account_service.recalculate_account_metrics(trading_account_id)

        return True

    async def get_financial_summary(self, claims: dict, trade_id: UUID) -> TradeFinancialSummary:
        """
        Recupera un riepilogo finanziario per un singolo trade,
        verificando l'appartenenza e arricchendolo con dati calcolati.
        """
        # Il metodo del repository ora carica anche il trading_account associato
        trade = await self.repo.get_trade_for_details_view(trade_id)
        if not trade:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trade not found")

        # Valida che l'utente sia il proprietario del trade
        await self._validate_and_get_trading_account(claims, trade.trading_account_id)

        # Assicurati che il trading_account sia stato caricato correttamente
        if not trade.trading_account or trade.trading_account.initial_balance is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Trading account details are missing for financial calculation."
            )

        # Prepara i dati per il calcolo del Net ROI e altre metriche avanzate
        trade_data_for_enrichment = {
            "p_l": trade.p_l,
            "entry_price": trade.entry_price,
            "exit_price": trade.exit_price,
            "stop_loss_price": trade.stop_loss_price,
            "take_profit_price": trade.take_profit_price,
            "lowest_price_during_trade": trade.lowest_price_during_trade,
            "highest_price_during_trade": trade.highest_price_during_trade,
            "position_size": trade.position_size,
            "direction": trade.direction.value if isinstance(trade.direction, TradeDirection) else trade.direction,
        }

        # Esegui i calcoli delle metriche avanzate (principalmente per Net ROI)
        all_metrics = enrich_trade_with_all_metrics(
            trade_data=trade_data_for_enrichment,
            initial_balance=Decimal(trade.trading_account.initial_balance)
        )

        # Calcola le commissioni totali sommando fees e commissions
        total_commissions = (trade.fees or Decimal('0')) + (trade.commissions or Decimal('0'))

        # Popola lo schema di risposta usando i dati diretti dal trade e quelli calcolati
        return TradeFinancialSummary(
            gross_pnl=float(trade.gross_p_l) if trade.gross_p_l is not None else None,
            total_commissions=float(total_commissions),
            net_pnl=float(trade.p_l) if trade.p_l is not None else None,
            net_roi=float(all_metrics.get("net_roi")) if all_metrics.get("net_roi") is not None else None,
        )

    async def get_trade_tags(self, claims: dict, trade_id: UUID) -> List[TagRead]:
        """Recupera i tag associati a un trade, verificando l'appartenenza."""
        db_trade = await self.repo.get_trade_for_details_view(trade_id)
        if not db_trade:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trade not found")

        await self._validate_and_get_trading_account(claims, db_trade.trading_account_id)

        return [TagRead.model_validate(tag) for tag in db_trade.tags]

    async def update_trade_tags(self, claims: dict, trade_id: UUID, tag_ids: List[UUID]) -> List[TagRead]:
        """Aggiorna i tag associati a un trade."""
        db_trade = await self.repo.get_trade_by_id_simple(trade_id)
        if not db_trade:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trade not found")

        _, general_account_id = await self._validate_and_get_trading_account(claims, db_trade.trading_account_id)

        # Recupera le istanze dei Tag e verifica che appartengano all'utente
        tags = await self._get_related_entities(general_account_id, Tag, tag_ids)

        # Aggiorna la relazione
        db_trade.tags = tags

        await self.db.commit()
        await self.db.refresh(db_trade, attribute_names=['tags'])

        return [TagRead.model_validate(tag) for tag in db_trade.tags]

    async def update_trade_labels(self, claims: dict, trade_id: UUID, label_ids: List[UUID], label_type: str) -> list:
        """
        Aggiorna le etichette associate a un trade in modo generico (mistakes, psychology, etc.).
        """
        LABEL_TYPE_MAP = {
            "mistakes": {"model": Mistake, "schema": "MistakeRead"},
            "psychology_states": {"model": PsychologyState, "schema": "PsychologyStateRead"},
            "news_impacts": {"model": NewsImpact, "schema": "NewsImpactRead"},
        }

        if label_type not in LABEL_TYPE_MAP:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid label type specified")

        config = LABEL_TYPE_MAP[label_type]
        model_class = config["model"]
        # Lo schema non viene usato qui ma potrebbe servire per la validazione del response_model

        db_trade = await self.repo.get_trade_by_id_simple(trade_id)
        if not db_trade:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trade not found")

        _, general_account_id = await self._validate_and_get_trading_account(claims, db_trade.trading_account_id)

        labels = await self._get_related_entities(general_account_id, model_class, label_ids)

        # Il nome dell'attributo sul modello Trade è il `label_type` (es. trade.mistakes)
        setattr(db_trade, label_type, labels)

        await self.db.commit()
        await self.db.refresh(db_trade, attribute_names=[label_type])

        # Restituisce la lista aggiornata di etichette
        return getattr(db_trade, label_type)

    async def update_trade_rules(self, claims: dict, trade_id: UUID, rule_ids: List[UUID]) -> List[UUID]:
        """
        Aggiorna le regole 'seguite' per un trade.
        """
        # 1. Recupera il trade e verifica che l'utente sia il proprietario
        db_trade = await self.repo.get_trade_by_id_simple(trade_id)
        if not db_trade:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trade not found")

        await self._validate_and_get_trading_account(claims, db_trade.trading_account_id)

        # 2. Recupera le istanze delle regole
        if not rule_ids:
            rules = []
        else:
            rules_result = await self.db.execute(
                select(RulePlaybook).where(RulePlaybook.id.in_(rule_ids))
            )
            rules = rules_result.scalars().all()
            if len(rules) != len(set(rule_ids)):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="One or more rule IDs are invalid.")

        # 3. Assegna le nuove regole
        db_trade.rules_followed = rules

        # 4. Commit e refresh
        await self.db.commit()
        await self.db.refresh(db_trade, attribute_names=['rules_followed'])

        # 5. Restituisce la lista degli ID delle regole aggiornate
        return [rule.id for rule in db_trade.rules_followed]