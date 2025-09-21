import uuid
from typing import List, Optional, Tuple
from sqlalchemy import delete, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.Models.account_activity import AccountActivity
from app.Schemas.snaptrade import AccountActivityCreate

class ActivityRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def delete_by_account_id(self, account_id: uuid.UUID) -> int:
        """
        Deletes all activities associated with a specific account_id.
        Returns the number of rows deleted.
        """
        stmt = delete(AccountActivity).where(AccountActivity.account_id == account_id)
        result = await self.db.execute(stmt)
        return result.rowcount

    async def create_activities(self, activities_data: List[AccountActivityCreate]) -> None:
        """
        Bulk creates new account activities from a list of Pydantic schemas.
        """
        if not activities_data:
            return

        activity_models = [AccountActivity(**data.model_dump()) for data in activities_data]
        self.db.add_all(activity_models)
        # The commit will be handled by the service layer's transaction block

    async def get_activities_paginated(
        self,
        account_id: uuid.UUID,
        type_filter: Optional[List[str]] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Tuple[List[AccountActivity], int]:
        """
        Retrieves a paginated list of activities for a given account,
        with an optional filter for the 'type' field.
        Also returns the total count of activities matching the filter.
        """
        # Query for the data
        stmt = select(AccountActivity).where(AccountActivity.account_id == account_id)

        # Query for the total count
        count_stmt = select(func.count()).select_from(AccountActivity).where(AccountActivity.account_id == account_id)

        if type_filter:
            stmt = stmt.where(AccountActivity.type.in_(type_filter))
            count_stmt = count_stmt.where(AccountActivity.type.in_(type_filter))

        # Get total count
        total_count_result = await self.db.execute(count_stmt)
        total = total_count_result.scalar_one_or_none() or 0

        # Get paginated data
        stmt = stmt.order_by(AccountActivity.trade_date.desc().nullslast(), AccountActivity.created_at.desc())
        stmt = stmt.limit(limit).offset(offset)

        result = await self.db.execute(stmt)
        activities = result.scalars().all()

        return activities, total
