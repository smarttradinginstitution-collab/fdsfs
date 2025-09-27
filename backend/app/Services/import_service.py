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
from app.Services.mt5_parser import Mt5Parser
from app.Services.trade_service import TradeService


class ImportService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.trade_service = TradeService(db_session)

    async def create_initial_import_run(
        self, user_id: uuid.UUID, trading_account_id: uuid.UUID, file_name: str, source_type: ImportSourceType
    ) -> ImportRun:
        """
        Creates an initial record for an import run with 'queued' status.
        """
        new_run = ImportRun(
            user_id=user_id,
            trading_account_id=trading_account_id,
            source_type=source_type,
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
        tradovate_parser = TradovateParser()
        await self._process_import(import_run_id, file_content, tradovate_parser, "Failed to parse Tradovate file")

    async def process_mt5_import(
        self, import_run_id: uuid.UUID, file_content: bytes
    ):
        """
        The main background task for processing an MT5 HTML file.
        """
        mt5_parser = Mt5Parser()
        await self._process_import(import_run_id, file_content, mt5_parser, "Failed to parse MT5 file")

    async def _process_import(
        self, import_run_id: uuid.UUID, file_content: bytes, parser, error_message_prefix: str
    ):
        """
        A generic method to process an import file using a given parser.
        """
        # 1. Update status to 'parsing'
        import_run = await self.get_import_run(import_run_id)
        if not import_run:
            return

        import_run.status = "parsing"
        file_hash = hashlib.sha256(file_content).hexdigest()
        import_run.file_sha256 = file_hash
        await self.db.commit()

        # 2. Parse the file
        try:
            parsed_trades = parser.parse_performance_report(file_content)
            import_run.total_rows = len(parsed_trades)
            import_run.status = "applying"
            await self.db.commit()
        except Exception as e:
            import_run.status = "failed"
            import_run.error_message = f"{error_message_prefix}: {e}"
            await self.db.commit()
            return

        # 3. Apply trades to the database
        inserted_count = 0
        updated_count = 0

        for trade_data in parsed_trades:
            trade_data["trading_account_id"] = import_run.trading_account_id
            trade_data["import_run_id"] = import_run.id

            # Calculate R-multiple before saving
            trade_data['r_multiple'] = self.trade_service._calculate_r_multiple(
                pnl=trade_data.get('p_l'),
                entry_price=trade_data.get('entry_price'),
                stop_loss_price=trade_data.get('stop_loss_price'),
                volume=trade_data.get('volume')
            )

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

        await self.db.flush()

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