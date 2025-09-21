from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from app.Models.option_symbol import OptionSymbol
from app.Schemas.snaptrade import OptionSymbolCreate

class OptionSymbolRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def upsert_option_symbols(self, option_symbols_data: List[OptionSymbolCreate]) -> None:
        """
        Inserts new option symbols or updates existing ones based on the primary key (id).
        """
        if not option_symbols_data:
            return

        # Convert Pydantic models to dictionaries
        option_symbols_dicts = [s.model_dump() for s in option_symbols_data]

        stmt = insert(OptionSymbol).values(option_symbols_dicts)

        # Define which columns to update on conflict
        update_dict = {
            c.name: c for c in stmt.excluded if c.name not in ["id", "created_at"]
        }

        stmt = stmt.on_conflict_do_update(
            index_elements=['id'],
            set_=update_dict
        )

        await self.db.execute(stmt)
        # The commit will be handled in the service layer's transaction block
