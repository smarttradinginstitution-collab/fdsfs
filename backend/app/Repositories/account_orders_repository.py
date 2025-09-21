from __future__ import annotations
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.Models.account_order import AccountOrder
from app.Schemas.snaptrade import AccountOrderCreate

class AccountOrderRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def batch_delete_and_create_for_account(self, account_id: uuid.UUID, orders: list[AccountOrderCreate]):
        """
        Deletes all existing orders for a given account and creates new ones.
        """
        await self.db.execute(
            AccountOrder.__table__.delete().where(AccountOrder.account_id == account_id)
        )

        new_orders = [
            AccountOrder(
                account_id=account_id,
                **order.model_dump()
            ) for order in orders
        ]

        self.db.add_all(new_orders)

    async def get_by_account_id(self, account_id: uuid.UUID) -> list[AccountOrder]:
        """
        Retrieves all orders for a given account.
        """
        stmt = select(AccountOrder).where(AccountOrder.account_id == account_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()
