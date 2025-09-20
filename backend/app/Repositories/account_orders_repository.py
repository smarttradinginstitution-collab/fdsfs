from typing import List, Dict, Any
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.future import select
from app.Models.account_order import AccountOrder

class AccountOrdersRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def upsert_orders(self, orders_data: List[Dict[str, Any]]) -> None:
        """
        Inserts new account orders or updates existing ones based on the primary key (id).
        """
        if not orders_data:
            return

        stmt = insert(AccountOrder).values(orders_data)

        # Define which columns to update on conflict
        update_dict = {
            c.name: c for c in stmt.excluded if c.name not in ["id", "account_id", "created_at"]
        }

        stmt = stmt.on_conflict_do_update(
            index_elements=['id'],
            set_=update_dict
        )

        await self.db.execute(stmt)
        await self.db.commit()

    async def get_orders_by_account_id(self, account_id: uuid.UUID) -> list[AccountOrder]:
        """
        Lists all orders for a given brokerage account.
        """
        stmt = select(AccountOrder).where(AccountOrder.account_id == account_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()
