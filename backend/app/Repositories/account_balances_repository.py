from typing import List, Dict, Any
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.future import select
from app.Models.account_balance import AccountBalance

class AccountBalancesRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def upsert_balances(self, balances_data: List[Dict[str, Any]]) -> None:
        """
        Inserts new account balances or updates existing ones based on the unique constraint
        (account_id, currency_code).
        """
        if not balances_data:
            return

        stmt = insert(AccountBalance).values(balances_data)

        # Define which columns to update on conflict
        update_dict = {
            c.name: c for c in stmt.excluded if c.name not in ["id", "account_id", "currency_code", "created_at"]
        }

        stmt = stmt.on_conflict_do_update(
            index_elements=['account_id', 'currency_code'],
            set_=update_dict
        )

        await self.db.execute(stmt)
        await self.db.commit()

    async def get_balances_by_account_id(self, account_id: uuid.UUID) -> list[AccountBalance]:
        """
        Lists all balances for a given brokerage account.
        """
        stmt = select(AccountBalance).where(AccountBalance.account_id == account_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()
