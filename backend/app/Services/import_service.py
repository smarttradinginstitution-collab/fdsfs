# backend/app/Services/import_service.py
import uuid
import hashlib
from typing import List, Dict, Any, Tuple
from decimal import Decimal
from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from app.Models.import_run import ImportRun
from app.Models.trade import Trade
from app.Services.tradovate_parser import TradovateParser
from app.Services.mt5_parser import Mt5Parser
from app.Services.ninjatrader_parser import NinjaTraderParser
from app.Services.metrics.trade_enricher import enrich_trade_with_all_metrics
from app.Repositories.trading_account_repository import TradingAccountRepository
from app.Models.enums import TradeStatus


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
        grouping_tolerance: int = None,
    ) -> Tuple[ImportRun, bool]:
        """
        Garantisce l'idempotenza. Cerca una run di importazione con lo stesso hash del file
        per lo stesso account che sia già stata completata o sia in corso.

        Se la trova (in stato queued, parsing, applying, applied), la restituisce.
        Altrimenti, ne crea una nuova.

        Returns:
            A tuple containing the ImportRun object and a boolean indicating if it was newly created.
        """
        # Cerca una run esistente (completata o in corso)
        stmt = select(ImportRun).where(
            ImportRun.file_sha256 == file_hash,
            ImportRun.trading_account_id == trading_account_id,
            ImportRun.status.in_(["queued", "parsing", "applying", "applied"])
        )
        result = await self.db.execute(stmt)
        existing_run = result.scalars().first()

        if existing_run:
            # If we are reusing a run, we should probably update the grouping_tolerance if provided?
            # But the user might be retrying with different settings.
            # For strict idempotency of the *run record*, we return it.
            # But if the user changed the setting, we might want to update it.
            if grouping_tolerance is not None and existing_run.grouping_tolerance != grouping_tolerance:
                 existing_run.grouping_tolerance = grouping_tolerance
                 await self.db.commit()

            return existing_run, False

        # Se non esiste, crea una nuova run
        new_run = ImportRun(
            user_id=user_id,
            trading_account_id=trading_account_id,
            source_type=source_type,
            file_name=file_name,
            file_sha256=file_hash,  # Salva l'hash subito
            status="queued",
            grouping_tolerance=grouping_tolerance,
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

    async def process_ninjatrader_import(
        self, import_run_id: uuid.UUID, file_content: bytes
    ):
        """
        Elabora in background un file CSV di NinjaTrader.
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

            parser = NinjaTraderParser()
            parsed_trades = parser.parse_performance_report(file_content)

            import_run.total_rows = len(parsed_trades)
            import_run.status = "applying"
            await self.db.commit()

        except Exception as e:
            import_run.status = "failed"
            import_run.error_message = f"[NinjaTraderParser] {type(e).__name__}: {e}"
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

    def _group_trades(self, parsed_trades: List[Dict], tolerance_seconds: int) -> List[Dict]:
        """
        Groups trades based on symbol, direction, and time proximity.
        """
        if not parsed_trades:
            return []

        # Sort by entry timestamp to ensure chronological order for chaining
        sorted_trades = sorted(parsed_trades, key=lambda x: x['entry_timestamp'])

        grouped_trades = []

        # We need to keep track of processed trades to avoid duplicates if we were modifying in place,
        # but here we build a new list.

        # Helper to check if trade belongs to group
        def belongs_to_group(trade, group):
            last_trade = group[-1]
            if trade['symbol_snapshot'] != last_trade['symbol_snapshot']:
                return False
            if trade['direction'] != last_trade['direction']:
                return False

            # Check time difference between current trade entry and last trade entry
            # User said "entro un certo lasso di tempo".
            # Usually for chaining: current.entry - last.entry <= tolerance
            delta = trade['entry_timestamp'] - last_trade['entry_timestamp']
            return delta.total_seconds() <= tolerance_seconds

        current_group = []

        for trade in sorted_trades:
            if not current_group:
                current_group.append(trade)
                continue

            if belongs_to_group(trade, current_group):
                current_group.append(trade)
            else:
                # Flush current group
                grouped_trades.append(current_group)
                # Start new group
                current_group = [trade]

        # Flush last group
        if current_group:
            grouped_trades.append(current_group)

        # Now construct the result list with Parent trades where applicable
        final_list = []

        for group in grouped_trades:
            if len(group) == 1:
                final_list.append(group[0])
            else:
                # Create Parent Trade
                parent = self._create_parent_trade_dict(group)
                # The group items are now children.
                # Since we are not yet in DB, we need to handle this.
                # We will return the Parent, and attach children to it.
                # But _apply_trades_to_db iterates and inserts.
                # Strategy: Insert Parent, then Insert Children with parent_id.
                # So we return a structure like: {'is_parent': True, 'data': parent_data, 'children': group}
                # Or we can just flatten the list but mark them.
                # Better: return the Parent object dict, with a special key '_children_data'
                parent['_children_data'] = group
                final_list.append(parent)

        return final_list

    def _create_parent_trade_dict(self, group: List[Dict]) -> Dict:
        """
        Aggregates a list of trades into a single parent trade dictionary.
        """
        first = group[0]
        last = group[-1]

        total_qty = sum(t.get('position_size', 0) or 0 for t in group)
        total_pl = sum(t.get('p_l', 0) or 0 for t in group)
        total_gross_pl = sum(t.get('gross_p_l', 0) or 0 for t in group)
        total_commissions = sum(t.get('commissions', 0) or 0 for t in group)
        total_fees = sum(t.get('fees', 0) or 0 for t in group)

        # Weighted Average Entry Price
        # WAEP = Sum(Price * Qty) / Sum(Qty)
        total_entry_val = sum((t.get('entry_price', 0) or 0) * (t.get('position_size', 0) or 0) for t in group)
        avg_entry_price = total_entry_val / total_qty if total_qty else 0

        # Weighted Average Exit Price
        total_exit_val = sum((t.get('exit_price', 0) or 0) * (t.get('position_size', 0) or 0) for t in group)
        avg_exit_price = total_exit_val / total_qty if total_qty else 0

        # Dedupe key for parent: combine keys or create new hash
        # To ensure uniqueness, we can hash the combined dedupe keys of children
        children_keys = "".join([t.get('dedupe_key', '') for t in group])
        parent_dedupe = hashlib.sha256(children_keys.encode()).hexdigest()

        parent = {
            "symbol_snapshot": first['symbol_snapshot'],
            "direction": first['direction'],
            "entry_timestamp": first['entry_timestamp'], # First entry
            "exit_timestamp": max(t['exit_timestamp'] for t in group if t['exit_timestamp']), # Latest exit
            "entry_price": avg_entry_price,
            "exit_price": avg_exit_price,
            "gross_p_l": total_gross_pl,
            "p_l": total_pl,
            "position_size": total_qty,
            "commissions": total_commissions,
            "fees": total_fees,
            "dedupe_key": f"parent-{parent_dedupe}",
            "status": TradeStatus.closed, # Assuming closed if imported
            "external_id": f"GROUP-{len(group)}", # Placeholder
            "trading_account_id": first.get('trading_account_id'), # Will be set/overwritten later
            "import_run_id": first.get('import_run_id'),
        }
        return parent

    async def _apply_trades_to_db(self, import_run: ImportRun, parsed_trades: List[Dict], initial_balance: Decimal) -> Tuple[int, int]:
        """
        Metodo helper per inserire/aggiornare i trade nel database.
        """

        # Apply grouping if needed
        # We only group if tolerance is set and > 0.
        # Check source type if needed, but the plan said "Update _apply_trades_to_db to call this grouping logic... specifically for MT5".
        # Since Tradovate/Ninja don't pass tolerance yet (based on my changes only to MT5), this check implicitly handles it.
        # But for safety, check source_type too or rely on tolerance.

        trades_to_process = parsed_trades
        if import_run.source_type == "html" and import_run.grouping_tolerance and import_run.grouping_tolerance > 0:
             trades_to_process = self._group_trades(parsed_trades, import_run.grouping_tolerance)

        inserted_count = 0
        updated_count = 0

        for trade_data in trades_to_process:
            # Check for children
            children_data = trade_data.pop('_children_data', None)

            trade_data["trading_account_id"] = import_run.trading_account_id
            trade_data["import_run_id"] = import_run.id

            all_metrics = enrich_trade_with_all_metrics(
                trade_data=trade_data,
                initial_balance=initial_balance
            )
            r_multiple = all_metrics.get("realized_r_multiple")
            trade_data['r_multiple'] = float(r_multiple) if r_multiple is not None else None

            dedupe_key = trade_data.get("dedupe_key")
            result = await self.db.execute(
                select(Trade).where(
                    Trade.dedupe_key == dedupe_key,
                    Trade.trading_account_id == import_run.trading_account_id,
                )
            )
            existing_trade = result.scalars().first()

            parent_trade_obj = None

            if existing_trade:
                # Se il trade esiste già, lo skippiamo.
                # Se è un parent group già esistente, potremmo voler controllare i figli, ma per ora skippiamo.
                parent_trade_obj = existing_trade
                # We do not count existing as inserted.
            else:
                new_trade = Trade(**trade_data)
                self.db.add(new_trade)
                await self.db.flush() # Flush to get ID
                parent_trade_obj = new_trade
                inserted_count += 1

            # If we have children, process them
            if children_data:
                for child_data in children_data:
                    child_data["trading_account_id"] = import_run.trading_account_id
                    child_data["import_run_id"] = import_run.id
                    child_data["parent_trade_id"] = parent_trade_obj.id # Link to parent

                    # Enrich child metrics? Usually yes.
                    child_metrics = enrich_trade_with_all_metrics(
                        trade_data=child_data,
                        initial_balance=initial_balance
                    )
                    child_r = child_metrics.get("realized_r_multiple")
                    child_data['r_multiple'] = float(child_r) if child_r is not None else None

                    child_dedupe = child_data.get("dedupe_key")

                    # Check existence of child
                    child_res = await self.db.execute(
                        select(Trade).where(
                            Trade.dedupe_key == child_dedupe,
                            Trade.trading_account_id == import_run.trading_account_id
                        )
                    )
                    existing_child = child_res.scalars().first()

                    if existing_child:
                        # If child exists, maybe update its parent_id if missing?
                        if existing_child.parent_trade_id != parent_trade_obj.id:
                            existing_child.parent_trade_id = parent_trade_obj.id
                            # Not counting as insert, maybe update?
                    else:
                        new_child = Trade(**child_data)
                        self.db.add(new_child)
                        inserted_count += 1

        await self.db.flush()
        return inserted_count, updated_count

    async def get_import_run(self, import_run_id: uuid.UUID) -> ImportRun | None:
        """Recupera una ImportRun dal suo ID."""
        result = await self.db.execute(
            select(ImportRun).where(ImportRun.id == import_run_id)
        )
        return result.scalars().first()
