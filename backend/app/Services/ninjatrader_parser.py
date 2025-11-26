# backend/app/Services/ninjatrader_parser.py
import csv
import io
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.Models.enums import TradeDirection

class NinjaTraderParser:
    """
    Parses trade data from NinjaTrader CSV files.
    """

    def parse_performance_report(self, file_content: bytes) -> List[Dict[str, Any]]:
        """
        Parses the CSV file from NinjaTrader.

        Args:
            file_content: The content of the CSV file in bytes.

        Returns:
            A list of dictionaries, where each dictionary represents a trade
            ready to be processed by the TradeService.
        """
        trades = []
        # NinjaTrader exports usually use a specific encoding, but utf-8 is a safe bet for modern systems.
        # If it fails, we might need 'utf-8-sig' or 'latin1'.
        content_as_string = file_content.decode('utf-8-sig')

        # NinjaTrader CSVs often use semi-colon ';' as delimiter based on the user provided example
        delimiter = ';'

        # Simple heuristic to detect if it's comma or semicolon if needed,
        # but the requirement says "accetta file csv e un file di esempio è cosi: ... ; ... ;"

        f = io.StringIO(content_as_string)
        reader = csv.DictReader(f, delimiter=delimiter)

        for row in reader:
            try:
                # Normalize keys: strip whitespace
                # The keys in DictReader will come from the header line.
                # Example headers: 'Trade number', 'Instrument', 'Account', 'Market pos.', 'Qty', ...

                # We map the CSV columns to our internal fields

                # Market Position
                market_pos = row.get('Market pos.', '').strip().lower()
                if market_pos == 'long':
                    direction = TradeDirection.LONG
                elif market_pos == 'short':
                    direction = TradeDirection.SHORT
                else:
                    # Skip if direction is unknown or flat/empty
                    continue

                # Timestamps
                entry_time_str = row.get('Entry time', '').strip()
                exit_time_str = row.get('Exit time', '').strip()

                entry_ts = self._parse_timestamp(entry_time_str)
                exit_ts = self._parse_timestamp(exit_time_str)

                if not entry_ts:
                    # Without entry time we can't really place the trade
                    continue

                # Prices
                entry_price = self._clean_price(row.get('Entry price'))
                exit_price = self._clean_price(row.get('Exit price'))

                # Quantity
                qty_str = row.get('Qty', '0').strip()
                position_size = float(qty_str) if qty_str else 0.0

                # Financials
                # 'Profit' column usually represents the P&L of the trade (Gross)
                # 'Commission' is the cost.
                gross_pnl = self._clean_money(row.get('Profit'))
                commission = self._clean_money(row.get('Commission'))

                # Net P&L = Gross P&L + Commission (Note: Commission is usually a positive number representing cost,
                # but in P&L math: Net = Gross - Cost.
                # Let's check the example.
                # Row 1: Profit 58,00 $. Commission 0,00 $. Cum Net Profit 58,00 $.
                # Let's look for a row with commission.
                # The example has 0 commissions for all rows provided...
                # Wait, let's re-read carefully.
                # "Commission" column has "0,00 $" in all example rows.
                # However, typically: Net = Gross - Commission.
                # I will calculate Net P&L = Gross Pnl - Commission.

                net_pnl = gross_pnl - commission

                # Deduplication Key
                # We need a unique identifier.
                # Combination of: Account, Instrument, Trade Number, Entry Time.
                trade_number = row.get('Trade number', '').strip()
                instrument = row.get('Instrument', '').strip()
                account = row.get('Account', '').strip()

                dedupe_source = f"{account}|{instrument}|{trade_number}|{entry_time_str}"
                dedupe_key = hashlib.sha256(dedupe_source.encode()).hexdigest()

                trade_data = {
                    "symbol_snapshot": instrument,
                    "direction": direction,
                    "entry_timestamp": entry_ts,
                    "exit_timestamp": exit_ts,
                    "entry_price": entry_price,
                    "exit_price": exit_price,
                    "gross_p_l": gross_pnl,
                    "p_l": net_pnl,
                    "position_size": position_size,
                    "commissions": commission,
                    "fees": 0.0, # User instructed to only use "Commission" column.
                    "dedupe_key": dedupe_key,
                    "status": "closed", # Assumed closed as it has exit time
                }
                trades.append(trade_data)

            except (ValueError, TypeError) as e:
                print(f"Skipping row due to parsing error: {row}. Error: {e}")
                continue

        return trades

    def _parse_timestamp(self, timestamp_str: str) -> Optional[datetime]:
        """
        Parses timestamps like '28/10/2025 14:30' or '28/10/2025 14:31'.
        """
        if not timestamp_str:
            return None

        # Example: 28/10/2025 14:30
        formats = [
            '%d/%m/%Y %H:%M',
            '%d/%m/%Y %H:%M:%S',
        ]

        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue

        return None

    def _clean_price(self, price_str: Optional[str]) -> Optional[float]:
        """
        Cleans price strings. Example: '26082,5' -> 26082.5
        """
        if not price_str:
            return None
        # Replace decimal comma with dot
        cleaned = price_str.replace(',', '.')
        try:
            return float(cleaned)
        except ValueError:
            return None

    def _clean_money(self, money_str: Optional[str]) -> float:
        """
        Cleans money strings. Example: '58,00 $' -> 58.00
        """
        if not money_str:
            return 0.0

        # Remove '$' and whitespace
        cleaned = money_str.replace('$', '').strip()
        # Replace decimal comma with dot
        cleaned = cleaned.replace(',', '.')
        # Remove thousands separator if any (assuming dot is NOT thousands separator here because of the comma decimal)
        # But wait, in European format "1.000,00" -> remove dot, replace comma.
        # In the example: "26082,5" -> Price. "58,00" -> Money.
        # It seems it's just "comma as decimal".
        # There are no thousands separators in the example.

        try:
            return float(cleaned)
        except ValueError:
            return 0.0
