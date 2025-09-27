# backend/app/Services/mt5_parser.py
import re
from datetime import datetime
from bs4 import BeautifulSoup

class Mt5Parser:
    def parse_performance_report(self, file_content: bytes):
        """
        Parses the HTML content of an MT5 performance report.
        """
        soup = BeautifulSoup(file_content, 'lxml')

        # Find the header row for "Posizioni"
        positions_header_div = soup.find('div', string='Posizioni')
        if not positions_header_div:
            raise ValueError("Could not find the 'Posizioni' section header in the report.")

        start_node = positions_header_div.find_parent('tr')
        if not start_node:
             raise ValueError("Could not find the 'Posizioni' table structure.")

        # The actual data rows start after the table headers row
        table_headers_row = start_node.find_next_sibling('tr')
        if not table_headers_row:
             raise ValueError("Could not find the 'Posizioni' table headers.")

        trades = []
        # Iterate through subsequent siblings
        for row in table_headers_row.find_next_siblings('tr'):
            # Stop if we hit the next section header, e.g., "Ordini"
            if row.find('div', string='Ordini'):
                break

            # Check if it's a valid trade row by looking for a date in the first cell
            all_cells = row.find_all('td')
            if not all_cells or not re.match(r'\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2}', all_cells[0].text.strip()):
                continue

            # Filter out hidden cells to get a consistent structure
            visible_cells = [c for c in all_cells if 'hidden' not in c.get('class', [])]
            if len(visible_cells) < 13:
                continue

            trade_data = {}
            try:
                trade_data['entry_time'] = self._parse_datetime(visible_cells[0].text.strip())
                trade_data['position_id'] = visible_cells[1].text.strip()
                trade_data['symbol'] = visible_cells[2].text.strip()
                trade_data['trade_type'] = visible_cells[3].text.strip()
                trade_data['volume'] = self._parse_float(visible_cells[4].text.strip())
                trade_data['entry_price'] = self._parse_float(visible_cells[5].text.strip())
                trade_data['stop_loss'] = self._parse_float(visible_cells[6].text.strip())
                trade_data['take_profit'] = self._parse_float(visible_cells[7].text.strip())
                trade_data['exit_time'] = self._parse_datetime(visible_cells[8].text.strip())
                trade_data['exit_price'] = self._parse_float(visible_cells[9].text.strip())
                trade_data['commission'] = self._parse_float(visible_cells[10].text.strip())
                trade_data['swap'] = self._parse_float(visible_cells[11].text.strip())
                trade_data['p_l'] = self._parse_float(visible_cells[12].text.strip())

                # Add a dedupe key
                trade_data['dedupe_key'] = f"mt5-{trade_data['position_id']}-{trade_data['exit_time']}"

                trades.append(trade_data)
            except (ValueError, IndexError) as e:
                # Log or skip malformed rows
                print(f"Skipping row due to parsing error: {e}. Row content: {row}")
                continue

        return trades

    def _parse_float(self, value_str: str):
        if not value_str or value_str.isspace():
            return None
        try:
            # Remove spaces and handle different decimal separators
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