from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.Infrastructure.db import get_db
from app.Services.trading_dna_service import TradingDnaService
from app.Schemas.trading_dna import TradingDnaReport
from app.Router.dependencies import get_current_general_account_id


class TradingDnaController:
    def __init__(self) -> None:
        pass

    async def get_trading_dna_report(
        self,
        general_account_id: UUID = Depends(get_current_general_account_id),
        db: AsyncSession = Depends(get_db),
        tag_ids: List[UUID] = Query(None),
        mistake_ids: List[UUID] = Query(None),
        psychology_state_ids: List[UUID] = Query(None),
        news_impact_ids: List[UUID] = Query(None),
    ) -> TradingDnaReport:
        """
        Generates and returns the Trading DNA report based on optional filters.
        """
        service = TradingDnaService(db, general_account_id)

        report_data = await service.generate_report(
            tag_ids=tag_ids,
            mistake_ids=mistake_ids,
            psychology_state_ids=psychology_state_ids,
            news_impact_ids=news_impact_ids,
        )

        # Use Pydantic model to validate and serialize the final report structure
        return TradingDnaReport(**report_data)