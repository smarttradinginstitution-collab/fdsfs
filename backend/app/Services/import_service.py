# backend/app/Services/import_service.py
import uuid
import hashlib
from typing import List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert

from app.Models.import_run import ImportRun
from app.Models.trade import Trade
from app.Models.enums import ImportSourceType
from app.Services.tradovate_parser import TradovateParser


class ImportService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.parser = TradovateParser()

    async def create_initial_import_run(
        self, user_id: uuid.UUID, trading_account_id: uuid.UUID, file_name: str
    ) -> ImportRun:
        """
        Creates an initial record for an import run with 'queued' status.
        """
        new_run = ImportRun(
            user_id=user_id,
            trading_account_id=trading_account_id,
            source_type="csv",
            file_name=file_name,
            status="queued",
        )
        self.db.add(new_run)
        await self.db.commit()
        await self.db.refresh(new_run)
        return new_run

    async def process_tradovate_import(
        self, import_run_id: uuid.UUID, file_content: bytes
    ):
        """
        The main background task for processing a Tradovate CSV file.
        """
        # 1. Update status to 'parsing'
        import_run = await self.get_import_run(import_run_id)
        if not import_run:
            return  # Or log an error

        import_run.status = "parsing"
        file_hash = hashlib.sha256(file_content).hexdigest()
        import_run.file_sha256 = file_hash
        await self.db.commit()

        # 2. Parse the file
        try:
            parsed_trades = self.parser.parse_performance_report(file_content)
            import_run.total_rows = len(parsed_trades)
            import_run.status = "applying"
            await self.db.commit()
        except Exception as e:
            import_run.status = "failed"
            import_run.error_message = f"Failed to parse file: {e}"
            await self.db.commit()
            return

        # 3. Apply trades to the database
        inserted_count = 0
        updated_count = 0

        for trade_data in parsed_trades:
            trade_data["trading_account_id"] = import_run.trading_account_id
            trade_data["import_run_id"] = import_run.id

            # Database-agnostic "read-then-write" for UPSERT logic
            dedupe_key = trade_data.get("dedupe_key")

            # Find existing trade by dedupe_key
            result = await self.db.execute(
                select(Trade).where(Trade.dedupe_key == dedupe_key)
            )
            existing_trade = result.scalars().first()

            if existing_trade:
                # Update existing trade
                for key, value in trade_data.items():
                    setattr(existing_trade, key, value)
                updated_count += 1
            else:
                # Create new trade
                new_trade = Trade(**trade_data)
                self.db.add(new_trade)
                inserted_count += 1

        await self.db.flush() # Flush to ensure all operations are pending before commit

        # 4. Finalize the import run
        import_run.status = "applied"
        import_run.inserted_count = inserted_count
        import_run.updated_count = updated_count
        import_run.skipped_count = import_run.total_rows - (inserted_count + updated_count)
        import_run.finished_at = func.now()

        await self.db.commit()

    async def get_import_run(self, import_run_id: uuid.UUID) -> ImportRun | None:
        """Fetches an ImportRun by its ID."""
        result = await self.db.execute(
            select(ImportRun).where(ImportRun.id == import_run_id)
        )
        return result.scalars().first()