# backend/app/Services/import_service.py
import uuid
import hashlib
from typing import List, Dict, Any, Tuple
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from app.Models.import_run import ImportRun
from app.Models.trade import Trade
from app.Services.tradovate_parser import TradovateParser
from app.Services.mt5_parser import Mt5Parser
from app.Services.metrics.trade_enricher import enrich_trade_with_all_metrics
from app.Repositories.trading_account_repository import TradingAccountRepository


class ImportService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.trading_account_repo = TradingAccountRepository(db_session)

    async def get_or_create_import_run(
        self,
        user_id: uuid.UUID,
        trading_account_id: uuid.UUID,
        file_name: str,
        file_hash: str,
        source_type: str,
    ) -> Tuple[ImportRun, bool]:
        """
        Garantisce l'idempotenza. Cerca una run di importazione completata con lo stesso hash
        del file per lo stesso account. Se la trova, la restituisce. Altrimenti, ne crea una nuova.

        Returns:
            A tuple containing the ImportRun object and a boolean indicating if it was newly created.
        """
        # Cerca una run esistente e completata con successo
        stmt = select(ImportRun).where(
            ImportRun.file_sha256 == file_hash,
            ImportRun.trading_account_id == trading_account_id,
            ImportRun.status == "applied"
        )
        result = await self.db.execute(stmt)
        existing_run = result.scalars().first()

        if existing_run:
            return existing_run, False  # Restituisce la run esistente, non ne crea una nuova

        # Se non esiste, crea una nuova run
        new_run = ImportRun(
            user_id=user_id,
            trading_account_id=trading_account_id,
            source_type=source_type,
            file_name=file_name,
            file_sha256=file_hash,  # Salva l'hash subito
            status="queued",
        )
        self.db.add(new_run)
        await self.db.commit()
        await self.db.refresh(new_run)
        return new_run, True  # Restituisce la nuova run

    async def process_tradovate_import(
        self, import_run_id: uuid.UUID, file_content: bytes
    ):
        """
        Elabora in background un file CSV di Tradovate.
        """
        import_run = await self.get_import_run(import_run_id)
        if not import_run:
            print(f"ERRORE: ImportRun con ID {import_run_id} non trovata.")
            return

        # 1. Aggiorna lo stato a 'parsing'
        import_run.status = "parsing"
        await self.db.commit()

        try:
            # Recupera le informazioni necessarie
            trading_account = await self.trading_account_repo.get_by_id(import_run.trading_account_id)
            initial_balance = Decimal(trading_account.initial_balance if trading_account else '0.0')

            # 2. Esegue il parsing del file
            parser = TradovateParser()
            parsed_trades = parser.parse_performance_report(file_content)

            # 3. Aggiorna lo stato a 'applying'
            import_run.total_rows = len(parsed_trades)
            import_run.status = "applying"
            await self.db.commit()

        except Exception as e:
            import_run.status = "failed"
            import_run.error_message = f"[TradovateParser] {type(e).__name__}: {e}"
            import_run.finished_at = func.now()
            await self.db.commit()
            return

        # 4. Applica i trade al database
        inserted_count, updated_count = await self._apply_trades_to_db(import_run, parsed_trades, initial_balance)

        # 5. Finalizza la run di importazione
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
        Elabora in background un file HTML di MT5.
        """
        import_run = await self.get_import_run(import_run_id)
        if not import_run:
            print(f"ERRORE: ImportRun con ID {import_run_id} non trovata.")
            return

        import_run.status = "parsing"
        await self.db.commit()

        try:
            trading_account = await self.trading_account_repo.get_by_id(import_run.trading_account_id)
            initial_balance = Decimal(trading_account.initial_balance if trading_account else '0.0')

            parser = Mt5Parser()
            parsed_trades = parser.parse_performance_report(file_content)

            import_run.total_rows = len(parsed_trades)
            import_run.status = "applying"
            await self.db.commit()

        except Exception as e:
            import_run.status = "failed"
            import_run.error_message = f"[Mt5Parser] {type(e).__name__}: {e}"
            import_run.finished_at = func.now()
            await self.db.commit()
            return

        inserted_count, updated_count = await self._apply_trades_to_db(import_run, parsed_trades, initial_balance)

        import_run.status = "applied"
        import_run.inserted_count = inserted_count
        import_run.updated_count = updated_count
        import_run.skipped_count = (import_run.total_rows or 0) - (inserted_count + updated_count)
        import_run.finished_at = func.now()
        await self.db.commit()

    async def _apply_trades_to_db(self, import_run: ImportRun, parsed_trades: List[Dict], initial_balance: Decimal) -> Tuple[int, int]:
        """
        Metodo helper per inserire/aggiornare i trade nel database.
        """
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
        return inserted_count, updated_count

    async def get_import_run(self, import_run_id: uuid.UUID) -> ImportRun | None:
        """Recupera una ImportRun dal suo ID."""
        result = await self.db.execute(
            select(ImportRun).where(ImportRun.id == import_run_id)
        )
        return result.scalars().first()
