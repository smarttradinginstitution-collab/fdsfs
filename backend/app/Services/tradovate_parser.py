# backend/app/Services/tradovate_parser.py
import csv
import io
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.Models.enums import TradeDirection

class TradovateParser:
    """
    Parses trade data from Tradovate CSV files.
    Specifically tailored for the 'Performance' report.
    """

    def parse_performance_report(self, file_content: bytes) -> List[Dict[str, Any]]:
        """
        Parses the "Performance (4).csv" file from Tradovate.

        Args:
            file_content: The content of the CSV file in bytes.

        Returns:
            A list of dictionaries, where each dictionary represents a trade
            ready to be processed by the TradeService.
        """
        trades = []
        content_as_string = file_content.decode('utf-8')

        lines = content_as_string.strip().splitlines()
        header_row_index = -1
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if 'symbol' in line_lower and 'pnl' in line_lower and 'boughttimestamp' in line_lower:
                header_row_index = i
                break

        if header_row_index == -1:
            raise ValueError("Could not find a valid header row in the Tradovate performance report.")

        # --- DIAGNOSTIC LOG ---
        print("--- PARSER DIAGNOSTICS START ---")
        print(f"Header found at line {header_row_index}: {lines[header_row_index]}")
        # --- END DIAGNOSTIC LOG ---

        csv_content = "\n".join(lines[header_row_index:])
        reader = csv.DictReader(io.StringIO(csv_content))

        # --- DIAGNOSTIC LOG ---
        print(f"CSV Headers after DictReader: {reader.fieldnames}")
        # --- END DIAGNOSTIC LOG ---

        for i, row_raw in enumerate(reader):
            # --- DIAGNOSTIC LOG for first 5 rows ---
            if i < 5:
                print(f"\n--- Processing Row {i+1} ---")
                print(f"Raw Row Data: {row_raw}")
            # --- END DIAGNOSTIC LOG ---

            try:
                # Normalize keys to be lowercase and stripped of whitespace for robust access
                row = {k.lower().strip().replace(' ', ''): v for k, v in row_raw.items() if k}

                if i < 5:
                    print(f"Normalized Row Keys: {list(row.keys())}")

                # Use the cleaned key 'tradeid'
                trade_id = row.get('tradeid')
                if not trade_id:
                    print(f"DEBUG: Skipping row {i+1} because 'tradeid' is missing or empty. Found keys: {list(row.keys())}")
                    continue

                bought_ts_str = row.get('boughttimestamp')
                sold_ts_str = row.get('soldtimestamp')
                bought_ts = self._parse_timestamp(bought_ts_str)
                sold_ts = self._parse_timestamp(sold_ts_str)

                if not bought_ts or not sold_ts:
                    print(f"DEBUG: Skipping row {i+1} due to invalid or missing timestamps. Bought: '{bought_ts_str}', Sold: '{sold_ts_str}'")
                    continue

                direction = TradeDirection.LONG if bought_ts < sold_ts else TradeDirection.SHORT
                entry_ts, exit_ts = (bought_ts, sold_ts) if direction == TradeDirection.LONG else (sold_ts, bought_ts)
                entry_price_str, exit_price_str = (row.get('buyprice'), row.get('sellprice')) if direction == TradeDirection.LONG else (row.get('sellprice'), row.get('buyprice'))
                gross_pnl = self._clean_pnl(row.get('pnl', '0'))

                trade_data = {
                    "symbol_snapshot": row.get('symbol'),
                    "direction": direction,
                    "entry_timestamp": entry_ts,
                    "exit_timestamp": exit_ts,
                    "entry_price": self._clean_price(entry_price_str),
                    "exit_price": self._clean_price(exit_price_str),
                    "gross_p_l": gross_pnl,
                    "p_l": gross_pnl,
                    "position_size": float(row.get('qty', 0)),
                    "dedupe_key": hashlib.sha256(trade_id.encode()).hexdigest(),
                    "status": "closed",
                    "fees": 0,
                    "commissions": 0,
                }
                trades.append(trade_data)
            except (ValueError, TypeError) as e:
                print(f"Skipping row {i+1} due to a parsing error: {row}. Error: {e}")
                continue

        print("--- PARSER DIAGNOSTICS END ---")
        return trades

    def _parse_timestamp(self, timestamp_str: Optional[str]) -> Optional[datetime]:
        if not timestamp_str:
            return None
        try:
            return datetime.strptime(timestamp_str, '%m/%d/%Y %H:%M:%S')
        except ValueError:
            try:
                return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            except ValueError:
                return None

    def _clean_price(self, price_str: Optional[str]) -> Optional[float]:
        if price_str is None:
            return None
        return float(price_str.replace(',', ''))

    def _clean_pnl(self, pnl_str: Optional[str]) -> float:
        if pnl_str is None:
            return 0.0
        pnl_str = pnl_str.strip().replace('$', '').replace(',', '')
        if pnl_str.startswith('(') and pnl_str.endswith(')'):
            return -float(pnl_str[1:-1])
        try:
            return float(pnl_str)
        except ValueError:
            return 0.0