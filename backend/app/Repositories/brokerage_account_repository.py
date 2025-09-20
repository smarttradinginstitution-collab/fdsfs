from typing import List, Dict, Any
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.future import select
from app.Models.brokerage_account import BrokerageAccount

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

    async def get_account_by_id(self, account_id: uuid.UUID) -> BrokerageAccount | None:
        """
        Gets a single brokerage account by its ID.
        """
        stmt = select(BrokerageAccount).where(BrokerageAccount.id == account_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
