from __future__ import annotations
import uuid
from app.Models.account_position import AccountPosition
from app.Schemas.snaptrade import AccountPositionCreate

class AccountPositionRepository:
    @staticmethod
    def build_positions_from_schemas(account_id: uuid.UUID, positions: list[AccountPositionCreate]) -> list[AccountPosition]:
        """
        Constructs a list of AccountPosition ORM objects from schemas.
        This method does not interact with the database.
        """
        return [
            AccountPosition(
                account_id=account_id,
                **position.model_dump()
            ) for position in positions
        ]
