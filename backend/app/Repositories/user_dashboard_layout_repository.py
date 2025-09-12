from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from ..Models.user_dashboard_layout import UserDashboardLayout
from ..Schemas.user_dashboard_layout import UserDashboardLayoutCreate, UserDashboardLayoutUpdate

class UserDashboardLayoutRepository:
    """
    Repository for the user_dashboard_layouts table.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_layout_by_user_id(self, user_id: UUID) -> UserDashboardLayout | None:
        """
        Retrieves the dashboard layout for a specific user.
        """
        return await self.db.get(UserDashboardLayout, user_id)

    async def create_or_update_layout(self, user_id: UUID, layout_data: UserDashboardLayoutCreate | UserDashboardLayoutUpdate) -> UserDashboardLayout:
        """
        Creates a new dashboard layout if one does not exist for the user,
        or updates the existing one.
        """
        existing_layout = await self.get_layout_by_user_id(user_id)

        # The .dict() method is deprecated in Pydantic v2, .model_dump() is the successor.
        # Assuming a modern Pydantic version.
        update_data = layout_data.model_dump()

        if existing_layout:
            # Update existing layout
            for key, value in update_data.items():
                setattr(existing_layout, key, value)
            db_layout = existing_layout
        else:
            # Create new layout
            db_layout = UserDashboardLayout(
                user_id=user_id,
                **update_data
            )
            self.db.add(db_layout)

        await self.db.commit()
        await self.db.refresh(db_layout)
        return db_layout
