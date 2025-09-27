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
            # Make header detection case-insensitive
            if 'symbol' in line_lower and 'pnl' in line_lower and 'boughttimestamp' in line_lower:
                header_row_index = i
                break

        if header_row_index == -1:
            # If no header is found, we cannot parse the file.
            raise ValueError("Could not find a valid header row in the Tradovate performance report.")

        csv_content = "\n".join(lines[header_row_index:])
        reader = csv.DictReader(io.StringIO(csv_content))

        for row_raw in reader:
            try:
                # Normalize keys to be lowercase and stripped of whitespace for robust access
                row = {k.lower().strip().replace(' ', ''): v for k, v in row_raw.items() if k}

                # Use the fill IDs for a reliable deduplication key
                buy_fill_id = row.get('buyfillid')
                sell_fill_id = row.get('sellfillid')

                if not buy_fill_id or not sell_fill_id:
                    # If either fill ID is missing, we cannot reliably identify the trade.
                    continue

                dedupe_key_source = f"{buy_fill_id}{sell_fill_id}"

                # Determine direction and assign timestamps and prices accordingly
                bought_ts = self._parse_timestamp(row.get('boughttimestamp'))
                sold_ts = self._parse_timestamp(row.get('soldtimestamp'))

                if not bought_ts or not sold_ts:
                    # If timestamps are missing, we can't process the trade
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
                    "p_l": gross_pnl, # Temporarily set Net P&L to Gross P&L
                    "volume": float(row.get('qty', 0)),
                    "dedupe_key": hashlib.sha256(dedupe_key_source.encode()).hexdigest(),
                    # These fields are not directly in the performance report but required by our model
                    "status": "closed",
                    "fees": 0,
                    "commissions": 0,
                }
                trades.append(trade_data)
            except (ValueError, TypeError) as e:
                # Skip rows that cannot be parsed, can be logged in the import_run
                print(f"Skipping row due to parsing error: {row}. Error: {e}")
                continue

        return trades

    def _parse_timestamp(self, timestamp_str: Optional[str]) -> Optional[datetime]:
        """
        Parses a timestamp string from Tradovate into a datetime object.
        Handles various potential formats.
        """
        if not timestamp_str:
            return None

        # Format from example: '09/22/2025 15:50:36'
        try:
            return datetime.strptime(timestamp_str, '%m/%d/%Y %H:%M:%S')
        except ValueError:
            # Fallback for other potential formats, e.g., with 'Z'
            try:
                return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            except ValueError:
                return None

    def _clean_price(self, price_str: Optional[str]) -> Optional[float]:
        """Cleans the price string, removing commas."""
        if price_str is None:
            return None
        return float(price_str.replace(',', ''))

    def _clean_pnl(self, pnl_str: Optional[str]) -> float:
        """
        Cleans the P&L string, removing currency symbols, commas, and parentheses for negatives.
        """
        if pnl_str is None:
            return 0.0
        pnl_str = pnl_str.strip().replace('$', '').replace(',', '')
        if pnl_str.startswith('(') and pnl_str.endswith(')'):
            return -float(pnl_str[1:-1])
        try:
            return float(pnl_str)
        except ValueError:
            return 0.0