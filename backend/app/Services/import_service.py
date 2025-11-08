# backend/app/Services/import_service.py
import uuid
import hashlib
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
        self, import_run_id: uuid.UUID, file_contents: List[bytes]
    ):
        """
        Processa una lista di file CSV di Tradovate.
        """
        import_run = await self.get_import_run(import_run_id)
        if not import_run:
            return

        await self.update_import_run_status(import_run_id, "parsing")

        trading_account = await self.trading_account_repo.get_by_id(import_run.trading_account_id)
        initial_balance = Decimal(trading_account.initial_balance if trading_account else '0.0')

        parser = TradovateParser()
        all_parsed_trades = []
        for content in file_contents:
            # Calcola l'hash per ogni file se necessario, o per il batch
            # Per semplicità, qui omettiamo l'hash individuale
            all_parsed_trades.extend(parser.parse_performance_report(content))

        import_run.total_rows = len(all_parsed_trades)
        await self.update_import_run_status(import_run_id, "applying")
        await self.db.commit() # Salva total_rows

        inserted_count = 0
        updated_count = 0

        for trade_data in all_parsed_trades:
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
        import_run.skipped_count = (import_run.total_rows or 0) - (inserted_count + updated_count)
        import_run.finished_at = func.now()

        await self.db.commit()

    async def process_mt5_import(
        self, import_run_id: uuid.UUID, file_content: bytes
    ):
        """
        Processa un singolo file HTML di MT5.
        """
        import_run = await self.get_import_run(import_run_id)
        if not import_run:
            return

        await self.update_import_run_status(import_run_id, "parsing", file_content=file_content)

        trading_account = await self.trading_account_repo.get_by_id(import_run.trading_account_id)
        initial_balance = Decimal(trading_account.initial_balance if trading_account else '0.0')

        parser = Mt5Parser()
        parsed_trades = parser.parse_performance_report(file_content)

        import_run.total_rows = len(parsed_trades)
        await self.update_import_run_status(import_run_id, "applying")
        await self.db.commit()

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
        import_run.skipped_count = (import_run.total_rows or 0) - (inserted_count + updated_count)
        import_run.finished_at = func.now()

        await self.db.commit()

    async def get_import_run(self, import_run_id: uuid.UUID) -> ImportRun | None:
        """Recupera una ImportRun dal suo ID."""
        result = await self.db.execute(
            select(ImportRun).where(ImportRun.id == import_run_id)
        )
        return result.scalars().first()

    async def update_import_run_status(
        self, import_run_id: uuid.UUID, new_status: str, error_message: str | None = None, file_content: bytes | None = None
    ):
        """Aggiorna lo stato di una ImportRun e opzionalmente il messaggio di errore e l'hash del file."""
        import_run = await self.get_import_run(import_run_id)
        if import_run:
            import_run.status = new_status
            if error_message:
                import_run.error_message = error_message
            if file_content:
                import_run.file_sha256 = hashlib.sha256(file_content).hexdigest()
            if new_status in ["applied", "failed"]:
                import_run.finished_at = func.now()

            await self.db.commit()