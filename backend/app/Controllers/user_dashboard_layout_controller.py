from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from ..Infrastructure.db import get_db
from ..Services.user_dashboard_layout_service import UserDashboardLayoutService
from ..Schemas.user_dashboard_layout import UserDashboardLayoutRead, UserDashboardLayoutUpdate
from ..Router.auth import get_current_claims

router = APIRouter(
    prefix="/users/me/dashboard-layout",
    tags=["Dashboard Layout"],
    responses={404: {"description": "Not found"}},
)

@router.get("", response_model=UserDashboardLayoutRead)
async def get_my_layout(
    db: AsyncSession = Depends(get_db),
    claims: dict = Depends(get_current_claims)
):
    """
    Get the dashboard layout for the currently authenticated user.
    If no layout exists, a default layout is returned.
    """
    user_id_str = claims.get("sub")
    if not user_id_str:
        raise HTTPException(status_code=401, detail="Invalid token claims")

    user_id = UUID(user_id_str)
    service = UserDashboardLayoutService(db)
    layout = await service.get_layout(user_id)
    return layout

@router.put("", response_model=UserDashboardLayoutRead)
async def save_my_layout(
    layout_data: UserDashboardLayoutUpdate,
    db: AsyncSession = Depends(get_db),
    claims: dict = Depends(get_current_claims)
):
    """
    Create or update the dashboard layout for the currently authenticated user.
    """
    user_id_str = claims.get("sub")
    if not user_id_str:
        raise HTTPException(status_code=401, detail="Invalid token claims")

    user_id = UUID(user_id_str)
    service = UserDashboardLayoutService(db)
    saved_layout = await service.save_layout(user_id, layout_data)
    return saved_layout
