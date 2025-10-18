from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

from app.Infrastructure.db import get_db
from app.Services.discipline_service import DisciplineService
from app.Router.dependencies import get_current_general_account_id
import datetime
from app.Schemas.discipline.discipline_rule import DisciplineRuleCreate, DisciplineRuleRead, DisciplineRuleUpdate
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

@router.post("/rules", response_model=DisciplineRuleRead, status_code=status.HTTP_201_CREATED)
async def create_discipline_rule(
    rule_in: DisciplineRuleCreate,
    general_account_id: UUID = Depends(get_current_general_account_id),
    service: DisciplineService = Depends(get_discipline_service),
):
    """
    Create a new discipline rule.
    """
    rule_data = rule_in.model_dump()
    rule_data["general_account_id"] = general_account_id
    return await service.rule_repo.create(rule_data)

@router.put("/rules/{rule_id}", response_model=DisciplineRuleRead)
async def update_discipline_rule(
    rule_id: UUID,
    rule_in: DisciplineRuleUpdate,
    service: DisciplineService = Depends(get_discipline_service),
):
    """
    Update an existing discipline rule.
    """
    updated_rule = await service.rule_repo.update(rule_id, rule_in.model_dump(exclude_unset=True))
    if not updated_rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")
    return updated_rule

@router.delete("/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_discipline_rule(
    rule_id: UUID,
    service: DisciplineService = Depends(get_discipline_service),
):
    """
    Delete a discipline rule.
    """
    if not await service.rule_repo.delete(rule_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")

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