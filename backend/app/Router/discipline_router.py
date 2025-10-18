from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

from app.Infrastructure.db import get_db
from app.Services.discipline_service import DisciplineService
from app.Router.dependencies import get_current_general_account_id
import datetime
from app.Schemas.discipline.discipline_rule import DisciplineRuleRead, DisciplineRuleBulkUpdate
from app.Schemas.discipline.daily_rule_instance import DailyRuleInstanceRead, DailyRuleInstanceUpdate
from app.Schemas.discipline.heatmap import HeatmapData

router = APIRouter(
    prefix="/api/v1/discipline",
    tags=["Discipline"],
)

# Dependency for discipline service
def get_discipline_service(db: AsyncSession = Depends(get_db)) -> DisciplineService:
    return DisciplineService(db)

@router.get("/rules", response_model=List[DisciplineRuleRead])
async def list_discipline_rules(
    general_account_id: UUID = Depends(get_current_general_account_id),
    service: DisciplineService = Depends(get_discipline_service),
):
    """
    List all discipline rules for the current user's general account.
    """
    return await service.rule_repo.list_by_general_account(general_account_id)

@router.post("/rules/bulk-update", response_model=List[DisciplineRuleRead])
async def bulk_update_discipline_rules(
    update_data: DisciplineRuleBulkUpdate,
    trading_account_id: UUID, # Needed to find today's checklist
    general_account_id: UUID = Depends(get_current_general_account_id),
    service: DisciplineService = Depends(get_discipline_service),
):
    """
    Create, update, and delete discipline rules in a single transaction
    and intelligently update the current day's checklist.
    """
    try:
        updated_rules = await service.bulk_update_rules(
            general_account_id=general_account_id,
            trading_account_id=trading_account_id,
            rules_in=update_data.rules
        )
        return updated_rules
    except Exception as e:
        # A more specific exception handling could be implemented
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/daily-checklist", response_model=List[DailyRuleInstanceRead])
async def get_daily_checklist(
    trading_account_id: UUID, # Passed as a query parameter
    general_account_id: UUID = Depends(get_current_general_account_id),
    service: DisciplineService = Depends(get_discipline_service),
):
    """
    Get the daily checklist for the user. Creates it if it doesn't exist for the day.
    """
    return await service.get_or_create_daily_checklist(general_account_id, trading_account_id)

@router.put("/daily-checklist/{instance_id}", response_model=DailyRuleInstanceRead)
async def update_daily_checklist_item(
    instance_id: UUID,
    instance_in: DailyRuleInstanceUpdate,
    service: DisciplineService = Depends(get_discipline_service),
):
    """
    Update the status of a manual rule in the daily checklist.
    """
    updated_instance = await service.update_manual_rule_status(instance_id, instance_in.status)
    if not updated_instance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instance not found or not a manual rule")
    return updated_instance

@router.get("/heatmap", response_model=List[HeatmapData])
async def get_heatmap_data(
    year: int,
    month: int,
    general_account_id: UUID = Depends(get_current_general_account_id),
    service: DisciplineService = Depends(get_discipline_service),
):
    """
    Get the heatmap data for a specific month.
    """
    if not 1 <= month <= 12:
        raise HTTPException(status_code=400, detail="Month must be between 1 and 12")

    # You might want to add validation for the year as well
    current_year = datetime.datetime.now().year
    if not 2000 <= year <= current_year + 1:
        raise HTTPException(status_code=400, detail=f"Year must be between 2000 and {current_year + 1}")

    return await service.get_heatmap_data(general_account_id, year, month)