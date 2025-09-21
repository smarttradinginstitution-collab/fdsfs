from __future__ import annotations
import uuid
from app.Models.account_order import AccountOrder
from app.Schemas.snaptrade import AccountOrderCreate

class AccountOrderRepository:
    @staticmethod
    def build_orders_from_schemas(account_id: uuid.UUID, orders: list[AccountOrderCreate]) -> list[AccountOrder]:
        """
        Constructs a list of AccountOrder ORM objects from schemas.
        This method does not interact with the database.
        """
        return [
            AccountOrder(
                account_id=account_id,
                **order.model_dump()
            ) for order in orders
        ]
