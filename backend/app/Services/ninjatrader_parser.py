# backend/app/Services/ninjatrader_parser.py
import csv
import io
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.Models.enums import TradeDirection

class NinjaTraderParser:
    def parse_csv(self, file_content: bytes) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        trades = []
        parsing_errors = []
        content_as_string = file_content.decode('utf-8')
        content_as_string = content_as_string.replace('\r\n', '\n')
        lines = content_as_string.strip().split('\n')
        header_row_index = -1
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if 'trade number' in line_lower and 'instrument' in line_lower and 'market pos.' in line_lower:
                header_row_index = i
                break
        if header_row_index == -1:
            raise ValueError("Could not find a valid header row in the NinjaTrader report.")
        csv_content = "\n".join(lines[header_row_index:])
        reader = csv.DictReader(io.StringIO(csv_content), delimiter=';')
        for i, row_raw in enumerate(reader):
            try:
                row = {k.lower().strip().replace(' ', '').replace('.', ''): v for k, v in row_raw.items() if k}
                trade_number = row.get('tradenumber')
                instrument = row.get('instrument')
                direction_str = row.get('marketpos')
                entry_time_str = row.get('entrytime')
                dedupe_key_source = f"ninjatrader-{trade_number}-{instrument}-{entry_time_str}"
                direction = TradeDirection.LONG if direction_str and 'long' in direction_str.lower() else TradeDirection.SHORT
                profit = self._clean_currency(row.get('profit', '0'))
                commission = self._clean_currency(row.get('commission', '0'))
                clearing_fee = self._clean_currency(row.get('clearingfee', '0'))
                exchange_fee = self._clean_currency(row.get('exchangefee', '0'))
                ip_fee = self._clean_currency(row.get('ipfee', '0'))
                nfa_fee = self._clean_currency(row.get('nfafee', '0'))
                total_fees = clearing_fee + exchange_fee + ip_fee + nfa_fee
                total_commissions = commission
                gross_pnl = profit + total_fees + total_commissions
                trade_data = {
                    "symbol_snapshot": instrument,
                    "direction": direction,
                    "entry_timestamp": self._parse_timestamp(entry_time_str),
                    "exit_timestamp": self._parse_timestamp(row.get('exittime')),
                    "entry_price": self._clean_decimal(row.get('entryprice')),
                    "exit_price": self._clean_decimal(row.get('exitprice')),
                    "gross_p_l": gross_pnl,
                    "p_l": profit,
                    "position_size": self._clean_integer(row.get('qty')),
                    "dedupe_key": hashlib.sha256(dedupe_key_source.encode()).hexdigest(),
                    "status": "closed",
                    "fees": total_fees,
                    "commissions": total_commissions,
                }
                if not all([trade_data['entry_timestamp'], trade_data['exit_timestamp'], trade_data['symbol_snapshot']]):
                    raise ValueError("Missing essential data (timestamps or symbol).")
                trades.append(trade_data)
            except (ValueError, TypeError) as e:
                parsing_errors.append({
                    "line": i + header_row_index + 2,
                    "error": str(e),
                    "data": {k: v for k, v in row_raw.items() if v}
                })
                continue
        return trades, parsing_errors
    def _parse_timestamp(self, timestamp_str: Optional[str]) -> Optional[datetime]:
        if not timestamp_str or timestamp_str.isspace():
            return None
        try:
            return datetime.strptime(timestamp_str, '%d/%m/%Y %H:%M:%S')
        except ValueError:
            return None
    def _clean_decimal(self, value_str: Optional[str]) -> Optional[float]:
        if value_str is None or value_str.isspace():
            return None
        try:
            return float(value_str.replace('.', '').replace(',', '.'))
        except (ValueError, TypeError):
            return None
    def _clean_integer(self, value_str: Optional[str]) -> Optional[int]:
        if value_str is None or value_str.isspace():
            return None
        try:
            return int(value_str)
        except(ValueError, TypeError):
            return None
    def _clean_currency(self, value_str: Optional[str]) -> float:
        if value_str is None or value_str.isspace():
            return 0.0
        try:
            return float(value_str.split(' ')[0].replace('.', '').replace(',', '.'))
        except (ValueError, TypeError):
            return 0.0
