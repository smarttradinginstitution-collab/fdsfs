import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional

from bs4 import BeautifulSoup
from app.Models.enums import TradeDirection

class Mt5Parser:
    """
    Parses trade data from MetaTrader 5 (MT5) HTML reports.
    """

    def parse_performance_report(self, file_content: bytes) -> List[Dict[str, Any]]:
        """
        Parses the HTML report file from MT5.

        Args:
            file_content: The content of the HTML file in bytes.

        Returns:
            A list of dictionaries, where each dictionary represents a trade
            ready to be processed by the TradeService.
        """
        trades = []
        soup = BeautifulSoup(file_content, 'html.parser')

        # Find the 'Posizioni' table
        positions_header = soup.find(lambda tag: tag.name == 'b' and 'Posizioni' in tag.text)
        if not positions_header:
            raise ValueError("Could not find the 'Posizioni' table in the MT5 report.")

        # Find the table that is an ancestor of the header
        positions_table = positions_header.find_parent('table')
        if not positions_table:
            raise ValueError("Could not find the 'Posizioni' table structure.")

        rows = positions_table.find_all('tr')

        # Find the header row to map columns by name, making it more robust
        header_row_index = -1
        header_map = {}
        for i, row in enumerate(rows):
            cols = [col.get_text(strip=True).lower() for col in row.find_all(['td', 'th'])]
            if 'posizione' in cols and 'simbolo' in cols and 'profitto' in cols:
                # Map header names to their index
                for idx, col_name in enumerate(cols):
                    # Normalize headers for consistency
                    if 'ora' in col_name:
                        if 'entry_time' not in header_map:
                             header_map['entry_time'] = idx
                        else:
                             header_map['exit_time'] = idx
                    elif 'prezzo' in col_name:
                        if 'entry_price' not in header_map:
                            header_map['entry_price'] = idx
                        else:
                            header_map['exit_price'] = idx
                    else:
                        header_map[col_name] = idx
                header_row_index = i
                break

        if header_row_index == -1:
            raise ValueError("Could not find a valid header row in the 'Posizioni' table.")

        # Process only the data rows after the header
        for row in rows[header_row_index + 1:]:
            cols = row.find_all('td')
            if len(cols) < len(header_map) - 2: # -2 for combined ora/prezzo
                # Not a valid trade row, could be a summary or empty row
                continue

            try:
                # Use the map to get data by column name
                get_col = lambda name: cols[header_map[name]].get_text(strip=True) if name in header_map else None

                position_id = get_col('posizione')
                if not position_id:
                    continue # Skip rows without a position ID

                direction_str = get_col('tipo')
                direction = TradeDirection.LONG if direction_str == 'buy' else TradeDirection.SHORT

                entry_ts = self._parse_timestamp(cols[header_map['entry_time']].get_text(strip=True))
                exit_ts = self._parse_timestamp(cols[header_map['exit_time']].get_text(strip=True))

                if not entry_ts or not exit_ts:
                    print(f"Skipping row due to missing timestamp. Position ID: {position_id}")
                    continue

                commissions = self._clean_pnl(get_col('commissioni'))
                swap = self._clean_pnl(get_col('swap'))

                trade_data = {
                    "symbol_snapshot": get_col('simbolo'),
                    "direction": direction,
                    "entry_timestamp": entry_ts,
                    "exit_timestamp": exit_ts,
                    "entry_price": self._clean_price(cols[header_map['entry_price']].get_text(strip=True)),
                    "exit_price": self._clean_price(cols[header_map['exit_price']].get_text(strip=True)),
                    "stop_loss_price": self._clean_price(get_col('s / l')),
                    "take_profit_price": self._clean_price(get_col('t / p')),
                    "gross_p_l": self._clean_pnl(get_col('profitto')),
                    "p_l": self._clean_pnl(get_col('profitto')), # Temporarily set Net P&L to Gross P&L
                    "position_size": self._clean_price(get_col('volume')),
                    "dedupe_key": hashlib.sha256(position_id.encode()).hexdigest(),
                    "status": "closed",
                    "fees": commissions + swap,
                    "commissions": commissions,
                }
                trades.append(trade_data)
            except (ValueError, TypeError, IndexError) as e:
                position_id_str = f" (Position ID: {cols[header_map.get('posizione')].get_text(strip=True) if 'posizione' in header_map else 'N/A'})"
                print(f"Skipping row due to parsing error: {e}{position_id_str}")
                continue

        return trades

    def _parse_timestamp(self, timestamp_str: Optional[str]) -> Optional[datetime]:
        """
        Parses a timestamp string from MT5 into a datetime object.
        Format from example: '2025.09.22 13:42:50'
        """
        if not timestamp_str:
            return None
        try:
            return datetime.strptime(timestamp_str, '%Y.%m.%d %H:%M:%S')
        except ValueError:
            return None

    def _clean_price(self, price_str: Optional[str]) -> Optional[float]:
        """Cleans the price string, removing spaces."""
        if not price_str:
            return None
        try:
            return float(price_str.replace(' ', '').replace(',', ''))
        except ValueError:
            return None

    def _clean_pnl(self, pnl_str: Optional[str]) -> float:
        """
        Cleans the P&L string, removing currency symbols, spaces, and handles negatives.
        """
        if not pnl_str:
            return 0.0
        pnl_str = pnl_str.strip().replace('$', '').replace(' ', '').replace(',', '')
        try:
            return float(pnl_str)
        except ValueError:
            return 0.0