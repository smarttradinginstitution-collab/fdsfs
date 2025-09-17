# app/Services/user_dashboard_layout_service.py
from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.Repositories.user_dashboard_layout_repository import UserDashboardLayoutRepository
from app.Schemas.user_dashboard_layout import UserDashboardLayoutUpdate, UserDashboardLayoutRead


class UserDashboardLayoutService:
    """Service layer for dashboard layout business logic."""

    def __init__(self, db: AsyncSession):
        self.repo = UserDashboardLayoutRepository(db)

    async def get_layout(self, user_id: UUID) -> Optional[UserDashboardLayoutRead]:
        """
        Retrieves the dashboard layout for a specific user.
        If the layout is in the old list format or an invalid format,
        it's treated as invalid to force a reset.
        """
        layout_model = await self.repo.get_by_user_id(user_id)
        if layout_model:
            if isinstance(layout_model.layout, dict):
                try:
                    # Attempt to validate the layout against the Pydantic schema
                    return UserDashboardLayoutRead.model_validate(layout_model)
                except ValidationError:
                    # If validation fails, the layout is malformed.
                    # Return None to trigger a reset to the default layout on the client.
                    return None
            else:
                # It's the old list format, also treat as not found.
                return None
        return None

    async def save_layout(
        self, user_id: UUID, payload: UserDashboardLayoutUpdate
    ) -> UserDashboardLayoutRead:
        """
        Saves or updates a user's dashboard layout.
        """
        upserted_layout = await self.repo.upsert(user_id, payload)
        return UserDashboardLayoutRead.model_validate(upserted_layout)
