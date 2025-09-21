from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from app.Models.security import Security
from app.Schemas.security import SecurityCreate

class SecurityRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def upsert_securities(self, securities_data: List[SecurityCreate]) -> None:
        """
        Inserts new securities or updates existing ones based on the primary key (id).
        """
        if not securities_data:
            return

        # Convert Pydantic models to dictionaries
        securities_dicts = [s.model_dump() for s in securities_data]

        stmt = insert(Security).values(securities_dicts)

        # Define which columns to update on conflict
        update_dict = {
            c.name: c for c in stmt.excluded if c.name not in ["id", "created_at"]
        }

        stmt = stmt.on_conflict_do_update(
            index_elements=['id'],
            set_=update_dict
        )

        await self.db.execute(stmt)
        # The commit will be handled in the service layer
