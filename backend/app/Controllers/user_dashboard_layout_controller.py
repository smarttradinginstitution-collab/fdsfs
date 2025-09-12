from __future__ import annotations
from uuid import UUID
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.Infrastructure.db import get_db
from app.Services.user_dashboard_layout_service import UserDashboardLayoutService
from app.Schemas.user_dashboard_layout import UserDashboardLayoutRead, UserDashboardLayoutUpdate

# Using a router is a good practice to keep the API modular.
# This router can be included in the main FastAPI app.
router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard Layout"],
)

@router.get("/layout", response_model=UserDashboardLayoutRead)
async def get_user_layout(
    user_id: UUID = Query(..., description="The ID of the user whose layout is being retrieved"),
    db: AsyncSession = Depends(get_db)
) -> UserDashboardLayoutRead:
    """
    Retrieves the dashboard layout for a specific user.

    - If the user has a saved layout, it is returned.
    - If the user has no saved layout, a default layout is returned.
    """
    try:
        service = UserDashboardLayoutService(db)
        layout = await service.get_layout_for_user(user_id)
        return layout
    except Exception as e:
        # A generic error handler to catch unexpected issues during service execution.
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/layout", response_model=UserDashboardLayoutRead)
async def update_user_layout(
    payload: UserDashboardLayoutUpdate,
    user_id: UUID = Query(..., description="The ID of the user whose layout is being saved"),
    db: AsyncSession = Depends(get_db)
) -> UserDashboardLayoutRead:
    """
    Saves or updates the dashboard layout for a specific user.

    This endpoint performs an "upsert":
    - If no layout exists for the user, a new one is created.
    - If a layout already exists, it is updated with the new configuration.
    """
    try:
        service = UserDashboardLayoutService(db)
        layout = await service.save_layout_for_user(user_id, payload)
        return layout
    except Exception as e:
        # Catching potential exceptions, e.g., database errors during upsert.
        raise HTTPException(status_code=500, detail=str(e))
