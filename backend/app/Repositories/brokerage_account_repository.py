from typing import List, Dict, Any
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.Models.brokerage_account import BrokerageAccount
from app.Schemas.brokerage_account import BrokerageAccountUpdate

class BrokerageAccountRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def upsert_accounts(self, accounts_data: List[Dict[str, Any]]) -> None:
        """
        Inserts new accounts or updates existing ones based on the primary key.
        """
        if not accounts_data:
            return

        stmt = insert(BrokerageAccount).values(accounts_data)

        # Define which columns to update on conflict
        update_dict = {
            c.name: c for c in stmt.excluded if c.name not in ["id", "user_id", "connection_id", "created_at"]
        }

        stmt = stmt.on_conflict_do_update(
            index_elements=['id'],
            set_=update_dict
        )

        await self.db.execute(stmt)
        await self.db.commit()

    async def get_accounts(self, user_id: uuid.UUID, connection_id: uuid.UUID | None = None) -> list[BrokerageAccount]:
        """
        Lists all brokerage accounts for a given user, optionally filtered by connection_id.
        """
        stmt = select(BrokerageAccount).where(BrokerageAccount.user_id == user_id)

        if connection_id:
            stmt = stmt.where(BrokerageAccount.connection_id == connection_id)

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_by_id(self, account_id: uuid.UUID) -> BrokerageAccount | None:
        """
        Retrieves a single brokerage account by its ID, eagerly loading related holdings.
        """
        stmt = (
            select(BrokerageAccount)
            .where(BrokerageAccount.id == account_id)
            .options(
                selectinload(BrokerageAccount.positions),
                selectinload(BrokerageAccount.balances),
                selectinload(BrokerageAccount.orders)
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def update_account_details(self, account_id: uuid.UUID, update_data: "BrokerageAccountUpdate") -> None:
        """
        Updates specific details of a brokerage account.
        """
        from sqlalchemy import update
        from app.Models.brokerage_account import BrokerageAccount

        # Create a dictionary with the data to update, excluding unset values
        update_values = update_data.model_dump(exclude_unset=True)

        if not update_values:
            return # Nothing to update

        stmt = (
            update(BrokerageAccount)
            .where(BrokerageAccount.id == account_id)
            .values(**update_values)
        )
        await self.db.execute(stmt)
        # The commit will be handled in the service layer

    async def update_sync_timestamp(self, account_id: uuid.UUID, field_name: str) -> None:
        """
        Updates a specific timestamp field on the brokerage account to the current time.
        """
        from sqlalchemy import update
        from datetime import datetime, timezone

        stmt = (
            update(BrokerageAccount)
            .where(BrokerageAccount.id == account_id)
            .values({field_name: datetime.now(timezone.utc)})
        )
        await self.db.execute(stmt)
        # The commit will be handled in the service layer
