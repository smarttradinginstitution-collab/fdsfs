from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

from app.Infrastructure.db import get_db
from app.Services.rule_statistics_service import RuleStatisticsService
from app.Router.dependencies import get_current_general_account_id

router = APIRouter(
    prefix="/api/v1/rules-with-statistics",
    tags=["Rule Statistics"],
)

def get_rule_statistics_service(db: AsyncSession = Depends(get_db)) -> RuleStatisticsService:
    return RuleStatisticsService(db)

@router.get("", response_model=List[dict])
async def get_rules_with_statistics(
    trading_account_id: UUID,
    general_account_id: UUID = Depends(get_current_general_account_id),
    service: RuleStatisticsService = Depends(get_rule_statistics_service),
):
    return await service.get_rules_with_statistics(general_account_id, trading_account_id)