# app/Controllers/playbook_controller.py
from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.Infrastructure.db import get_db
from app.Repositories.playbook_repository import PlaybookRepository
from app.Repositories.trade_repository import TradeRepository
from app.Schemas.playbook import (
    PlaybookCreate, PlaybookRead, PlaybookUpdate, PlaybookAdminRead, PlaybookStats, PlaybookAnalytics
)
from app.Schemas.rule_playbook import RuleMetrics
from app.Schemas.trade import TradeRead
from app.Router.dependencies import get_current_user, get_current_general_account_id, CurrentUser
from app.Services.metrics.metrics_calculator import MetricsCalculator
from app.Services.playbook_analytics_service import PlaybookAnalyticsService


class PlaybookController:
    def __init__(self) -> None:
        pass

    async def list_all_playbooks_for_admin(
        self,
        db: AsyncSession = Depends(get_db),
    ) -> List[PlaybookAdminRead]:
        """
        [Admin] Lista tutti i playbook, raggruppati per General Account.
        """
        repo = PlaybookRepository(db)
        accounts = await repo.list_all_playbooks_grouped_by_account()

        response_data = []
        for acc in accounts:
            if acc.user:  # Assicura che ci sia un utente associato
                response_data.append(
                    PlaybookAdminRead(
                        general_account_id=acc.id,
                        user_email=acc.user.email,
                        playbooks=[PlaybookRead.model_validate(p) for p in acc.playbooks],
                    )
                )
        return response_data

    async def list_my_playbooks(
        self,
        general_account_id: UUID = Depends(get_current_general_account_id),
        db: AsyncSession = Depends(get_db),
    ) -> List[PlaybookRead]:
        """
        Lista tutti i playbook dell'utente autenticato, arricchiti con le statistiche
        calcolate in modo efficiente a livello di database.
        """
        repo = PlaybookRepository(db)
        playbooks_data = await repo.list_playbooks_with_stats(general_account_id)

        response_playbooks = []
        for item in playbooks_data:
            playbook_orm = item["playbook"]
            stats_data = item["stats"]

            # Convalida il modello ORM con lo schema Pydantic
            playbook_read = PlaybookRead.model_validate(playbook_orm)

            # Arricchisci lo schema con le statistiche aggregate
            playbook_read.stats = PlaybookStats(
                total_trades=stats_data.get("total_trades", 0),
                net_pnl=stats_data.get("total_p_l", 0.0),
                win_rate=0,  # Da calcolare
                profit_factor=0,  # Da calcolare
                avg_pnl=stats_data.get("avg_p_l", 0.0),
                avg_r_multiple=stats_data.get("avg_r_multiple", 0.0)
            )

            # Calcola metriche derivate come win_rate e profit_factor
            winning_trades = stats_data.get("winning_trades", 0)
            losing_trades = stats_data.get("losing_trades", 0)
            total_trades = winning_trades + losing_trades

            if total_trades > 0:
                playbook_read.stats.win_rate = (winning_trades / total_trades) * 100

            # Nota: il calcolo del profit factor richiede la somma delle vincite e delle perdite,
            # che non abbiamo direttamente. Per semplicità, lo lasciamo a 0.
            # Per un calcolo preciso, dovremmo estendere la query.

            response_playbooks.append(playbook_read)

        return response_playbooks

    async def get_playbook(
        self,
        playbook_id: UUID,
        current_user: CurrentUser = Depends(get_current_user),
        general_account_id: UUID = Depends(get_current_general_account_id),
        db: AsyncSession = Depends(get_db),
    ) -> PlaybookRead:
        """
        Recupera un singolo playbook per ID, verificando la proprietà.
        """
        repo = PlaybookRepository(db)
        playbook = await repo.get_by_id(playbook_id)

        if not playbook:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playbook non trovato.")

        if not current_user.is_admin and playbook.general_account_id != general_account_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accesso non autorizzato.")

        return PlaybookRead.model_validate(playbook)

    async def create_playbook(
        self,
        playbook_data: PlaybookCreate,
        general_account_id: UUID = Depends(get_current_general_account_id),
        db: AsyncSession = Depends(get_db),
    ) -> PlaybookRead:
        """
        Crea un nuovo playbook per l'utente autenticato.
        """
        repo = PlaybookRepository(db)
        new_playbook = await repo.create(playbook_in=playbook_data, general_account_id=general_account_id)
        return PlaybookRead.model_validate(new_playbook)

    async def update_playbook(
        self,
        playbook_id: UUID,
        playbook_data: PlaybookUpdate,
        current_user: CurrentUser = Depends(get_current_user),
        general_account_id: UUID = Depends(get_current_general_account_id),
        db: AsyncSession = Depends(get_db),
    ) -> PlaybookRead:
        """
        Aggiorna un playbook, verificando la proprietà.
        """
        repo = PlaybookRepository(db)
        playbook_to_update = await repo.get_by_id(playbook_id)

        if not playbook_to_update:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playbook non trovato.")

        if not current_user.is_admin and playbook_to_update.general_account_id != general_account_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accesso non autorizzato.")

        updated_playbook = await repo.update(db_obj=playbook_to_update, obj_in=playbook_data)
        if not updated_playbook:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Errore durante l'aggiornamento del playbook."
            )

        return PlaybookRead.model_validate(updated_playbook)

    async def delete_playbook(
        self,
        playbook_id: UUID,
        current_user: CurrentUser = Depends(get_current_user),
        general_account_id: UUID = Depends(get_current_general_account_id),
        db: AsyncSession = Depends(get_db),
    ) -> dict:
        """
        Elimina un playbook, verificando la proprietà.
        """
        repo = PlaybookRepository(db)
        playbook_to_delete = await repo.get_by_id(playbook_id)

        if not playbook_to_delete:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playbook non trovato.")

        if not current_user.is_admin and playbook_to_delete.general_account_id != general_account_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accesso non autorizzato.")

        await repo.delete(db_obj=playbook_to_delete)

        return {"ok": True, "detail": "Playbook eliminato con successo."}

    async def get_playbook_analytics(
        self,
        playbook_id: UUID,
        current_user: CurrentUser = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> PlaybookAnalytics:
        """
        Recupera le statistiche e i dati analitici per un singolo playbook.
        """
        service = PlaybookAnalyticsService(db)
        analytics_data = await service.get_playbook_analytics(
            playbook_id=playbook_id,
            current_user_id=current_user.id,
            is_admin=current_user.is_admin
        )

        if not analytics_data:
            # La logica del servizio ritorna None se il playbook non esiste o l'utente non ha accesso
            # Potremmo distinguere i due casi, ma per ora un 404 generico è sufficiente
            # e più sicuro (non rivela l'esistenza di una risorsa).
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playbook non trovato o accesso negato.")

        return analytics_data

    async def list_trades_for_playbook(
        self,
        playbook_id: UUID,
        current_user: CurrentUser = Depends(get_current_user),
        general_account_id: UUID = Depends(get_current_general_account_id),
        db: AsyncSession = Depends(get_db),
    ) -> List[TradeRead]:
        """
        Recupera tutti i trade associati a un playbook specifico, verificando la proprietà.
        """
        playbook_repo = PlaybookRepository(db)
        playbook = await playbook_repo.get_by_id(playbook_id)

        if not playbook:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playbook non trovato.")

        if not current_user.is_admin and playbook.general_account_id != general_account_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accesso non autorizzato.")

        trade_repo = TradeRepository(db)
        trades = await trade_repo.list_by_playbook_id(playbook_id)
        return [TradeRead.model_validate(trade) for trade in trades]