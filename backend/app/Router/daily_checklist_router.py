from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

from app.Infrastructure.db import get_db
from app.Services.discipline_settings_service import DisciplineSettingsService
from app.Router.dependencies import get_current_general_account_id
from app.Schemas.discipline.daily_rule_instance import DailyRuleInstanceRead, DailyRuleInstanceUpdate

router = APIRouter(
    prefix="/api/v1/daily-checklist",
    tags=["Daily Checklist"],
)

# Dependency for discipline settings service
def get_discipline_settings_service(db: AsyncSession = Depends(get_db)) -> DisciplineSettingsService:
    return DisciplineSettingsService(db)

@router.get("", response_model=dict)
async def get_daily_checklist(
    trading_account_id: UUID,
    general_account_id: UUID = Depends(get_current_general_account_id),
    service: DisciplineSettingsService = Depends(get_discipline_settings_service),
):
    return await service.get_or_create_daily_checklist(general_account_id, trading_account_id)

@router.put("/{instance_id}", response_model=DailyRuleInstanceRead)
async def update_daily_checklist_item(
    instance_id: UUID,
    instance_in: DailyRuleInstanceUpdate,
    service: DisciplineSettingsService = Depends(get_discipline_settings_service),
):
    updated_instance = await service.update_manual_rule_status(instance_id, instance_in.status)
    if not updated_instance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instance not found")
    return updated_instance