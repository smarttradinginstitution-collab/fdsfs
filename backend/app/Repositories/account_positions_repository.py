from __future__ import annotations
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.Models.account_position import AccountPosition
from app.Schemas.snaptrade import AccountPositionCreate

class AccountPositionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def batch_delete_and_create_for_account(self, account_id: uuid.UUID, positions: list[AccountPositionCreate]):
        """
        Deletes all existing positions for a given account and creates new ones.
        This operation should be part of a larger transaction managed by the service.
        """
        # Delete all existing positions for this account
        await self.db.execute(
            AccountPosition.__table__.delete().where(AccountPosition.account_id == account_id)
        )

        # Create new position objects
        new_positions = [
            AccountPosition(
                account_id=account_id,
                **position.model_dump()
            ) for position in positions
        ]

        # Add them to the session
        self.db.add_all(new_positions)

    async def get_by_account_id(self, account_id: uuid.UUID) -> list[AccountPosition]:
        """
        Retrieves all positions for a given account.
        """
        stmt = select(AccountPosition).where(AccountPosition.account_id == account_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()
