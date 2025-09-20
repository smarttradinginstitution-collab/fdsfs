from typing import List, Dict, Any
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.future import select
from app.Models.account_position import AccountPosition

class AccountPositionsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def upsert_positions(self, positions_data: List[Dict[str, Any]]) -> None:
        """
        Inserts new account positions or updates existing ones based on the unique constraint
        (account_id, symbol).
        """
        if not positions_data:
            return

        stmt = insert(AccountPosition).values(positions_data)

        # Define which columns to update on conflict
        update_dict = {
            c.name: c for c in stmt.excluded if c.name not in ["id", "account_id", "symbol", "created_at"]
        }

        stmt = stmt.on_conflict_do_update(
            index_elements=['account_id', 'symbol'],
            set_=update_dict
        )

        await self.db.execute(stmt)
        await self.db.commit()

    async def get_positions_by_account_id(self, account_id: uuid.UUID) -> list[AccountPosition]:
        """
        Lists all positions for a given brokerage account.
        """
        stmt = select(AccountPosition).where(AccountPosition.account_id == account_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()
