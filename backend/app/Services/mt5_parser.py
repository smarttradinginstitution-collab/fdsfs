# backend/app/Services/mt5_parser.py
import re
from datetime import datetime
from bs4 import BeautifulSoup

from app.Models.enums import TradeDirection

class Mt5Parser:
    def parse_performance_report(self, file_content: bytes):
        """
        Parses the HTML content of an MT5 performance report.
        """
        soup = BeautifulSoup(file_content, 'lxml')

        positions_header_div = soup.find('div', string='Posizioni')
        if not positions_header_div:
            raise ValueError("Could not find the 'Posizioni' section header in the report.")

        start_node = positions_header_div.find_parent('tr')
        if not start_node:
             raise ValueError("Could not find the 'Posizioni' table structure.")

        table_headers_row = start_node.find_next_sibling('tr')
        if not table_headers_row:
             raise ValueError("Could not find the 'Posizioni' table headers.")

        trades = []
        for row in table_headers_row.find_next_siblings('tr'):
            if row.find('div', string='Ordini'):
                break

            all_cells = row.find_all('td')
            if not all_cells or not re.match(r'\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2}', all_cells[0].text.strip()):
                continue

            visible_cells = [c for c in all_cells if 'hidden' not in c.get('class', [])]
            if len(visible_cells) < 13:
                continue

            trade_data = {}
            try:
                # Correct field names to match the Trade model and Tradovate parser
                trade_data['entry_timestamp'] = self._parse_datetime(visible_cells[0].text.strip())
                trade_data['external_id'] = visible_cells[1].text.strip()
                trade_data['symbol_snapshot'] = visible_cells[2].text.strip()

                # Map trade type string to TradeDirection enum
                trade_type_str = visible_cells[3].text.strip().lower()
                if trade_type_str == 'buy':
                    trade_data['direction'] = TradeDirection.LONG
                elif trade_type_str == 'sell':
                    trade_data['direction'] = TradeDirection.SHORT
                else:
                    # If direction is unknown, skip the trade
                    continue

                trade_data['position_size'] = self._parse_float(visible_cells[4].text.strip())
                trade_data['entry_price'] = self._parse_float(visible_cells[5].text.strip())
                trade_data['stop_loss_price'] = self._parse_float(visible_cells[6].text.strip())
                trade_data['take_profit_price'] = self._parse_float(visible_cells[7].text.strip())
                trade_data['exit_timestamp'] = self._parse_datetime(visible_cells[8].text.strip())
                trade_data['exit_price'] = self._parse_float(visible_cells[9].text.strip())

                commissions = self._parse_float(visible_cells[10].text.strip())
                swap = self._parse_float(visible_cells[11].text.strip())
                gross_pl = self._parse_float(visible_cells[12].text.strip())

                trade_data['commissions'] = commissions
                # Swap is a type of fee
                trade_data['fees'] = swap
                trade_data['gross_p_l'] = gross_pl

                # Calculate Net P&L (p_l) based on gross, commissions, and fees (swap)
                net_pl = (gross_pl or 0) - (commissions or 0) - (swap or 0)
                trade_data['p_l'] = net_pl

                # Use a consistent and robust deduplication key
                exit_ts_str = trade_data['exit_timestamp'].isoformat() if trade_data['exit_timestamp'] else ''
                trade_data['dedupe_key'] = f"mt5-{trade_data['external_id']}-{exit_ts_str}"

                trades.append(trade_data)
            except (ValueError, IndexError) as e:
                print(f"Skipping row due to parsing error: {e}. Row content: {row}")
                continue

        return trades

    def _parse_float(self, value_str: str):
        if not value_str or value_str.isspace():
            return None
        try:
            cleaned_str = value_str.replace(' ', '').replace(',', '.')
            return float(cleaned_str)
        except (ValueError, TypeError):
            return None

    def _parse_datetime(self, value_str: str):
        if not value_str or value_str.isspace():
            return None
        try:
            return datetime.strptime(value_str, '%Y.%m.%d %H:%M:%S')
        except (ValueError, TypeError):
            return None