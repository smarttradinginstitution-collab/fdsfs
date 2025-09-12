import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from ..Repositories.user_dashboard_layout_repository import UserDashboardLayoutRepository
from ..Schemas.user_dashboard_layout import UserDashboardLayoutCreate, UserDashboardLayoutRead, LayoutItemSchema

# Define a default layout for new users or users without a saved layout.
# This structure should correspond to the `i` keys used in the frontend components.
DEFAULT_LAYOUT = [
    # Complex widgets row
    {'i': 'VantageScoreWidget', 'x': 0, 'y': 0, 'w': 4, 'h': 2},
    {'i': 'RrDistributionWidget', 'x': 4, 'y': 0, 'w': 4, 'h': 2},
    {'i': 'CumulativePnlWidget', 'x': 8, 'y': 0, 'w': 4, 'h': 2},
    # Main content row
    {'i': 'CalendarHeatmap', 'x': 0, 'y': 2, 'w': 8, 'h': 3},
    {'i': 'RecentTradesTable', 'x': 8, 'y': 2, 'w': 4, 'h': 3},
]

class UserDashboardLayoutService:
    def __init__(self, db: AsyncSession):
        self.repository = UserDashboardLayoutRepository(db)

    async def get_layout(self, user_id: uuid.UUID) -> UserDashboardLayoutRead:
        """
        Gets the dashboard layout for a user.
        If the user has no saved layout, returns a default layout configuration.
        """
        db_layout = await self.repository.get_layout_by_user_id(user_id)

        if not db_layout:
            # This user does not have a saved layout. We return a default one.
            # We don't save it to the DB; it's ephemeral until the user
            # makes a change and saves it for the first time.
            return UserDashboardLayoutRead(
                user_id=user_id,
                layout_config=[LayoutItemSchema(**item) for item in DEFAULT_LAYOUT],
                created_at=datetime.utcnow(), # Ephemeral timestamp
                updated_at=datetime.utcnow()  # Ephemeral timestamp
            )

        return UserDashboardLayoutRead.from_orm(db_layout)

    async def save_layout(self, user_id: uuid.UUID, layout_data: UserDashboardLayoutCreate) -> UserDashboardLayoutRead:
        """
        Saves or updates the dashboard layout for a specific user.
        """
        saved_layout = await self.repository.create_or_update_layout(user_id, layout_data)
        return UserDashboardLayoutRead.from_orm(saved_layout)
