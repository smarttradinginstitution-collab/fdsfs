from __future__ import annotations
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from app.Models.user_dashboard_layout import UserDashboardLayout
from app.Schemas.user_dashboard_layout import UserDashboardLayoutUpdate

class UserDashboardLayoutRepository:
    """
    Repository for handling database operations for user dashboard layouts.
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user_id(self, user_id: UUID) -> UserDashboardLayout | None:
        """
        Retrieves the dashboard layout for a specific user.
        """
        query = select(UserDashboardLayout).where(UserDashboardLayout.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def upsert(self, user_id: UUID, layout_data: UserDashboardLayoutUpdate) -> UserDashboardLayout:
        """
        Creates a new dashboard layout or updates it if it already exists for the user.
        This operation is atomic thanks to PostgreSQL's ON CONFLICT clause.
        """
        stmt = insert(UserDashboardLayout).values(
            user_id=user_id,
            layout=layout_data.layout
        ).on_conflict_do_update(
            index_elements=['user_id'],
            set_={
                'layout': layout_data.layout
            }
        ).returning(UserDashboardLayout)

        result = await self.db.execute(stmt)
        scalar_result = result.scalar_one()
        await self.db.commit()
        return scalar_result
