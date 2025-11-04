# backend/app/Services/import_service.py
import uuid
import hashlib
import json
from typing import List, Dict, Any
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert

from app.Models.import_run import ImportRun
from app.Models.trade import Trade
from app.Models.enums import ImportSourceType
from app.Services.tradovate_parser import TradovateParser
from app.Services.mt5_parser import Mt5Parser
from app.Services.ninjatrader_parser import NinjaTraderParser
from app.Services.trade_service import TradeService
from app.Services.metrics.trade_enricher import enrich_trade_with_all_metrics
from app.Repositories.trading_account_repository import TradingAccountRepository


class ImportService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.trade_service = TradeService(db_session)
        self.trading_account_repo = TradingAccountRepository(db_session)

    async def create_initial_import_run(
        self, user_id: uuid.UUID, trading_account_id: uuid.UUID, file_name: str, source_type: str = "csv"
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
        # 1. Update status to 'parsing'
        import_run = await self.get_import_run(import_run_id)
        if not import_run:
            return  # Or log an error

        trading_account = await self.trading_account_repo.get_by_id(import_run.trading_account_id)
        initial_balance = Decimal(trading_account.initial_balance if trading_account else '0.0')

        import_run.status = "parsing"
        file_hash = hashlib.sha256(file_content).hexdigest()
        import_run.file_sha256 = file_hash
        await self.db.commit()

        # 2. Parse the file
        try:
            parser = TradovateParser()
            parsed_trades = parser.parse_performance_report(file_content)
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

            # Calculate R-multiple before saving
            all_metrics = enrich_trade_with_all_metrics(
                trade_data=trade_data,
                initial_balance=initial_balance
            )
            r_multiple = all_metrics.get("realized_r_multiple")
            trade_data['r_multiple'] = float(r_multiple) if r_multiple is not None else None

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

    async def process_mt5_import(
        self, import_run_id: uuid.UUID, file_content: bytes
    ):
        """
        The main background task for processing an MT5 HTML file.
        """
        import_run = await self.get_import_run(import_run_id)
        if not import_run:
            return

        trading_account = await self.trading_account_repo.get_by_id(import_run.trading_account_id)
        initial_balance = Decimal(trading_account.initial_balance if trading_account else '0.0')

        import_run.status = "parsing"
        file_hash = hashlib.sha256(file_content).hexdigest()
        import_run.file_sha256 = file_hash
        await self.db.commit()

        try:
            parser = Mt5Parser()
            parsed_trades = parser.parse_performance_report(file_content)
            import_run.total_rows = len(parsed_trades)
            import_run.status = "applying"
            await self.db.commit()
        except Exception as e:
            import_run.status = "failed"
            import_run.error_message = f"Failed to parse MT5 file: {e}"
            await self.db.commit()
            return

        inserted_count = 0
        updated_count = 0

        for trade_data in parsed_trades:
            trade_data["trading_account_id"] = import_run.trading_account_id
            trade_data["import_run_id"] = import_run.id

            all_metrics = enrich_trade_with_all_metrics(
                trade_data=trade_data,
                initial_balance=initial_balance
            )
            r_multiple = all_metrics.get("realized_r_multiple")
            trade_data['r_multiple'] = float(r_multiple) if r_multiple is not None else None

            dedupe_key = trade_data.get("dedupe_key")
            result = await self.db.execute(select(Trade).where(Trade.dedupe_key == dedupe_key))
            existing_trade = result.scalars().first()

            if existing_trade:
                for key, value in trade_data.items():
                    setattr(existing_trade, key, value)
                updated_count += 1
            else:
                new_trade = Trade(**trade_data)
                self.db.add(new_trade)
                inserted_count += 1

        await self.db.flush()

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

    async def process_ninjatrader_import(
        self, import_run_id: uuid.UUID, file_content: bytes
    ):
        """
        The main background task for processing a NinjaTrader 8 CSV file.
        """
        import_run = await self.get_import_run(import_run_id)
        if not import_run:
            return

        trading_account = await self.trading_account_repo.get_by_id(import_run.trading_account_id)
        initial_balance = Decimal(trading_account.initial_balance if trading_account else '0.0')

        import_run.status = "parsing"
        file_hash = hashlib.sha256(file_content).hexdigest()
        import_run.file_sha256 = file_hash
        await self.db.commit()

        try:
            parser = NinjaTraderParser()
            parsed_trades, parsing_errors = parser.parse_csv(file_content)

            import_run.total_rows = len(parsed_trades) + len(parsing_errors)
            import_run.skipped_count = len(parsing_errors)
            if parsing_errors:
                import_run.error_message = json.dumps(parsing_errors)

            import_run.status = "applying"
            await self.db.commit()

        except Exception as e:
            import_run.status = "failed"
            import_run.error_message = f"Failed to parse NinjaTrader file: {e}"
            await self.db.commit()
            return

        inserted_count = 0
        updated_count = 0

        for trade_data in parsed_trades:
            trade_data["trading_account_id"] = import_run.trading_account_id
            trade_data["import_run_id"] = import_run.id

            all_metrics = enrich_trade_with_all_metrics(
                trade_data=trade_data,
                initial_balance=initial_balance
            )
            r_multiple = all_metrics.get("realized_r_multiple")
            trade_data['r_multiple'] = float(r_multiple) if r_multiple is not None else None

            dedupe_key = trade_data.get("dedupe_key")
            result = await self.db.execute(select(Trade).where(Trade.dedupe_key == dedupe_key))
            existing_trade = result.scalars().first()

            if existing_trade:
                for key, value in trade_data.items():
                    setattr(existing_trade, key, value)
                updated_count += 1
            else:
                new_trade = Trade(**trade_data)
                self.db.add(new_trade)
                inserted_count += 1

        await self.db.flush()

        import_run.status = "applied"
        import_run.inserted_count = inserted_count
        import_run.updated_count = updated_count
        import_run.finished_at = func.now()

        await self.db.commit()