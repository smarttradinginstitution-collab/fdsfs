
# app/Controllers/playbook_controller.py
from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.Infrastructure.db import get_db
from app.Repositories.playbook_repository import PlaybookRepository
from app.Repositories.trade_repository import TradeRepository
from app.Services.playbook_service import PlaybookService
from app.Schemas.playbook import (
    PlaybookCreate, PlaybookRead, PlaybookUpdate, PlaybookAdminRead, PlaybookStats, PlaybookAnalytics
)
from app.Schemas.playbook_block import PlaybookBlockRead, PlaybookBlockCreate, PlaybookBlockUpdate
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
        Lista tutti i playbook dell'utente autenticato, arricchiti con le statistiche.
        """
        playbook_repo = PlaybookRepository(db)
        playbooks_data = await playbook_repo.list_playbooks_with_stats(general_account_id)

        if not playbooks_data:
            return []

        response_playbooks = []
        for item in playbooks_data:
            playbook_orm = item["playbook"]
            stats_data = item["stats"]

            playbook_read = PlaybookRead.model_validate(playbook_orm)
            winning_trades = stats_data.get("winning_trades", 0)
            losing_trades = stats_data.get("losing_trades", 0)
            total_trades = stats_data.get("total_trades", 0)
            gross_profit = stats_data.get("gross_profit", 0.0)
            gross_loss = stats_data.get("gross_loss", 0.0)

            win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
            loss_rate = (losing_trades / total_trades) * 100 if total_trades > 0 else 0
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else None
            avg_winner = gross_profit / winning_trades if winning_trades > 0 else 0
            avg_loser = gross_loss / losing_trades if losing_trades > 0 else 0
            expectancy = ((win_rate / 100) * avg_winner) - ((loss_rate / 100) * avg_loser)

            playbook_read.stats = PlaybookStats(
                total_trades=total_trades,
                net_pnl=stats_data.get("total_p_l", 0.0),
                win_rate=win_rate,
                profit_factor=profit_factor,
                avg_winner=avg_winner,
                avg_loser=avg_loser,
                expectancy=expectancy
            )

            response_playbooks.append(playbook_read)

        return response_playbooks

    async def get_playbook(
        self,
        playbook_id: UUID,
        current_user: CurrentUser = Depends(get_current_user),
        general_account_id: UUID = Depends(get_current_general_account_id),
        db: AsyncSession = Depends(get_db),
    ) -> PlaybookRead:
        repo = PlaybookRepository(db)
        playbook = await repo.get_by_id_with_relations(playbook_id)

        if not playbook:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playbook not found.")

        if not current_user.is_admin and playbook.general_account_id != general_account_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access not authorized.")

        return PlaybookRead.model_validate(playbook)

    async def create_playbook(
        self,
        playbook_data: PlaybookCreate,
        general_account_id: UUID = Depends(get_current_general_account_id),
        db: AsyncSession = Depends(get_db),
    ) -> PlaybookRead:
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
        repo = PlaybookRepository(db)
        playbook_to_update = await repo.get_by_id_with_relations(playbook_id)

        if not playbook_to_update:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playbook not found.")

        if not current_user.is_admin and playbook_to_update.general_account_id != general_account_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access not authorized.")

        updated_playbook = await repo.update(db_obj=playbook_to_update, obj_in=playbook_data)
        refreshed_playbook = await repo.get_by_id_with_relations(updated_playbook.id)
        return PlaybookRead.model_validate(refreshed_playbook)

    async def delete_playbook(
        self,
        playbook_id: UUID,
        current_user: CurrentUser = Depends(get_current_user),
        general_account_id: UUID = Depends(get_current_general_account_id),
        db: AsyncSession = Depends(get_db),
        playbook_service: PlaybookService = Depends(),
    ) -> dict:
        repo = PlaybookRepository(db)
        playbook_to_delete = await repo.get_by_id(playbook_id)

        if not playbook_to_delete:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playbook not found.")

        if not current_user.is_admin and playbook_to_delete.general_account_id != general_account_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access not authorized.")

        await playbook_service.delete_playbook_and_cleanup_trades(playbook_to_delete=playbook_to_delete)
        return {"ok": True, "detail": "Playbook deleted successfully."}

    async def get_playbook_analytics(
        self,
        playbook_id: UUID,
        current_user: CurrentUser = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> PlaybookAnalytics:
        service = PlaybookAnalyticsService(db)
        analytics_data = await service.get_playbook_analytics(
            playbook_id=playbook_id,
            current_user_id=current_user.id,
            is_admin=current_user.is_admin
        )
        if not analytics_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playbook not found or access denied.")
        return analytics_data

    async def list_trades_for_playbook(
        self,
        playbook_id: UUID,
        current_user: CurrentUser = Depends(get_current_user),
        general_account_id: UUID = Depends(get_current_general_account_id),
        db: AsyncSession = Depends(get_db),
    ) -> List[TradeRead]:
        playbook_repo = PlaybookRepository(db)
        playbook = await playbook_repo.get_by_id(playbook_id)

        if not playbook:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playbook not found.")
        if not current_user.is_admin and playbook.general_account_id != general_account_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access not authorized.")

        trade_repo = TradeRepository(db)
        trades = await trade_repo.list_by_playbook_id(playbook_id)
        return [TradeRead.model_validate(trade) for trade in trades]

    # --- Methods for Blocks ---

    async def create_block(
        self,
        playbook_id: UUID,
        block_data: PlaybookBlockCreate,
        current_user: CurrentUser = Depends(get_current_user),
        general_account_id: UUID = Depends(get_current_general_account_id),
        db: AsyncSession = Depends(get_db),
    ) -> PlaybookBlockRead:
        repo = PlaybookRepository(db)
        playbook = await repo.get_by_id(playbook_id)
        if not playbook or playbook.general_account_id != general_account_id:
            raise HTTPException(status_code=404, detail="Playbook not found")

        new_block = await repo.create_block(playbook_id=playbook_id, block_in=block_data)
        return PlaybookBlockRead.model_validate(new_block)

    async def update_block(
        self,
        playbook_id: UUID,
        block_id: UUID,
        block_data: PlaybookBlockUpdate,
        current_user: CurrentUser = Depends(get_current_user),
        general_account_id: UUID = Depends(get_current_general_account_id),
        db: AsyncSession = Depends(get_db),
    ) -> PlaybookBlockRead:
        repo = PlaybookRepository(db)
        # Verify playbook ownership first
        playbook = await repo.get_by_id(playbook_id)
        if not playbook or playbook.general_account_id != general_account_id:
            raise HTTPException(status_code=404, detail="Playbook not found")

        # Now get the block and update it
        block_to_update = await repo.get_block_by_id(block_id)
        if not block_to_update or block_to_update.playbook_id != playbook_id:
            raise HTTPException(status_code=404, detail="Block not found")

        updated_block = await repo.update_block(db_obj=block_to_update, obj_in=block_data)
        return PlaybookBlockRead.model_validate(updated_block)

    async def delete_block(
        self,
        playbook_id: UUID,
        block_id: UUID,
        current_user: CurrentUser = Depends(get_current_user),
        general_account_id: UUID = Depends(get_current_general_account_id),
        db: AsyncSession = Depends(get_db),
    ) -> dict:
        repo = PlaybookRepository(db)
        # Verify playbook ownership first
        playbook = await repo.get_by_id(playbook_id)
        if not playbook or playbook.general_account_id != general_account_id:
            raise HTTPException(status_code=404, detail="Playbook not found")

        # Now get the block and delete it
        block_to_delete = await repo.get_block_by_id(block_id)
        if not block_to_delete or block_to_delete.playbook_id != playbook_id:
            raise HTTPException(status_code=404, detail="Block not found")

        await repo.delete_block(db_obj=block_to_delete)
        return {"ok": True, "detail": "Block deleted successfully."}
