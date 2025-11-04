# backend/app/Services/playbook_service.py
from __future__ import annotations

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.Infrastructure.db import get_db
from app.Repositories.playbook_repository import PlaybookRepository
from app.Repositories.trade_repository import TradeRepository


class PlaybookService:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db
        self.playbook_repo = PlaybookRepository(db)
        self.trade_repo = TradeRepository(db)

    async def delete_playbook_and_cleanup_trades(self, playbook_to_delete: "Playbook") -> None:
        """
        Deletes a playbook and ensures that all associated trades are cleaned up.
        It sets the playbook_id to None and clears the rules_followed list for each trade
        that was using this playbook.
        """
        playbook_id = playbook_to_delete.id

        # 1. Find all trades associated with this playbook
        trades_to_update = await self.trade_repo.list_by_playbook_id(playbook_id)

        # 2. Clean up each trade
        for trade in trades_to_update:
            trade.playbook_id = None
            trade.rules_followed = []
            self.db.add(trade)

        # 3. Delete the playbook itself
        await self.playbook_repo.delete(db_obj=playbook_to_delete)

        # The commit is handled by the repo's delete method, but an extra one here ensures
        # the trade updates are also saved if the delete logic changes.
        await self.db.commit()
