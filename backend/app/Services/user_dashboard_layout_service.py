from __future__ import annotations
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.Repositories.user_dashboard_layout_repository import UserDashboardLayoutRepository
from app.Schemas.user_dashboard_layout import UserDashboardLayoutUpdate, UserDashboardLayoutRead
from app.Models.user_dashboard_layout import UserDashboardLayout

# A default layout for new users or users who haven't saved a layout yet.
# This provides a consistent starting point for everyone.
# For StatCards, the `i` property MUST match a key in the `allDashboardStats` getter in the frontend's `trades.js` store.
DEFAULT_LAYOUT = [
    # Complex Widgets
    {"x": 0, "y": 0, "w": 4, "h": 4, "i": "VantageScore", "component": "VantageScore"},
    {"x": 0, "y": 4, "w": 12, "h": 6, "i": "CumulativePnlChart", "component": "CumulativePnlChart"},
    
    # StatCard Widgets
    # The `i` here is the key for the stat data.
    {"x": 4, "y": 0, "w": 2, "h": 2, "i": "winRate", "component": "StatCard"},
    {"x": 6, "y": 0, "w": 2, "h": 2, "i": "netPnl", "component": "StatCard"},
    {"x": 8, "y": 0, "w": 2, "h": 2, "i": "trades", "component": "StatCard"},
    {"x": 10, "y": 0, "w": 2, "h": 2, "i": "profitFactor", "component": "StatCard"},
]

class UserDashboardLayoutService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = UserDashboardLayoutRepository(db)

    async def get_layout_for_user(self, user_id: UUID) -> UserDashboardLayoutRead:
        """
        Retrieves a user's dashboard layout. If no layout is found in the database,
        it returns a predefined default layout. This ensures the frontend always
        has a layout to render.
        """
        layout_model = await self.repo.get_by_user_id(user_id)

        if layout_model:
            # Pydantic's from_orm will convert the SQLAlchemy model to our Read schema
            return UserDashboardLayoutRead.from_orm(layout_model)

        # If no layout is found, construct a Read schema with the default layout.
        # This object is not persisted in the database.
        return UserDashboardLayoutRead(
            user_id=user_id,
            layout=DEFAULT_LAYOUT,
            # id, created_at, and updated_at are None since this is a default, non-DB record
        )

    async def save_layout_for_user(self, user_id: UUID, layout_data: UserDashboardLayoutUpdate) -> UserDashboardLayoutRead:
        """
        Saves or updates a user's dashboard layout using an "upsert" operation.
        The repository handles the logic of creating vs. updating.
        """
        upserted_layout = await self.repo.upsert(user_id, layout_data)
        return UserDashboardLayoutRead.from_orm(upserted_layout)