from __future__ import annotations
import uuid
from app.Models.account_balance import AccountBalance
from app.Schemas.snaptrade import AccountBalanceCreate

class AccountBalanceRepository:
    @staticmethod
    def build_balances_from_schemas(account_id: uuid.UUID, balances: list[AccountBalanceCreate]) -> list[AccountBalance]:
        """
        Constructs a list of AccountBalance ORM objects from schemas.
        This method does not interact with the database.
        """
        return [
            AccountBalance(
                account_id=account_id,
                **balance.model_dump()
            ) for balance in balances
        ]
