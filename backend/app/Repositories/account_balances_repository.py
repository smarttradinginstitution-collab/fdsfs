from __future__ import annotations
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.Models.account_balance import AccountBalance
from app.Schemas.snaptrade import AccountBalanceCreate

class AccountBalanceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def batch_delete_and_create_for_account(self, account_id: uuid.UUID, balances: list[AccountBalanceCreate]):
        """
        Deletes all existing balances for a given account and creates new ones.
        """
        await self.db.execute(
            AccountBalance.__table__.delete().where(AccountBalance.account_id == account_id)
        )

        new_balances = [
            AccountBalance(
                account_id=account_id,
                **balance.model_dump()
            ) for balance in balances
        ]

        self.db.add_all(new_balances)

    async def get_by_account_id(self, account_id: uuid.UUID) -> list[AccountBalance]:
        """
        Retrieves all balances for a given account.
        """
        stmt = select(AccountBalance).where(AccountBalance.account_id == account_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()
