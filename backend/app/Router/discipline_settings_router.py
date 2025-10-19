from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

from app.Infrastructure.db import get_db
from app.Services.discipline_settings_service import DisciplineSettingsService
from app.Router.dependencies import get_current_general_account_id
from app.Schemas.discipline_settings_schema import DisciplineSettingsSchema, DisciplineSettingsUpdate

router = APIRouter(
    prefix="/api/v1/discipline-settings",
    tags=["Discipline Settings"],
)

# Dependency for discipline settings service
def get_discipline_settings_service(db: AsyncSession = Depends(get_db)) -> DisciplineSettingsService:
    return DisciplineSettingsService(db)

@router.get("", response_model=DisciplineSettingsSchema)
async def get_discipline_settings(
    general_account_id: UUID = Depends(get_current_general_account_id),
    service: DisciplineSettingsService = Depends(get_discipline_settings_service),
):
    """
    Get discipline settings for the current user's general account.
    """
    settings = await service.get_settings_by_general_account(general_account_id)
    if not settings:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Settings not found")
    return settings

@router.post("", response_model=DisciplineSettingsSchema)
async def create_or_update_discipline_settings(
    settings_in: DisciplineSettingsUpdate,
    general_account_id: UUID = Depends(get_current_general_account_id),
    service: DisciplineSettingsService = Depends(get_discipline_settings_service),
):
    """
    Create or update discipline settings for the current user's general account.
    """
    return await service.create_or_update_settings(general_account_id, settings_in)