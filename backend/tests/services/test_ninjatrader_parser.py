# backend/tests/services/test_ninjatrader_parser.py
import pytest
from datetime import datetime
from app.Services.ninjatrader_parser import NinjaTraderParser
from app.Models.enums import TradeDirection

@pytest.fixture
def ninja_trader_parser():
    """Returns an instance of NinjaTraderParser."""
    return NinjaTraderParser()

# Sample valid CSV content from NinjaTrader 8
VALID_CSV_CONTENT = """NinjaTrader Grid 2025-11-03 05-05 .csv
Trade number;Instrument;Account;Strategy;Market pos.;Qty;Entry price;Exit price;Entry time;Exit time;Entry name;Exit name;Profit;Cum. net profit;Commission;Clearing Fee;Exchange Fee;IP Fee;NFA Fee;MAE;MFE;ETD;Bars
1;MNQ DEC25;PA-APEX-226793-16!Apex!Apex;;Long;2;26068,00;26082,50;28/10/2025 14:30:26;28/10/2025 14:31:14;;Close;58,00 $;58,00 $;1,00 $;0,50 $;0,50 $;0,20 $;0,10 $;25,00 $;63,00 $;5,00 $;0
2;NQ DEC25;PA-APEX-226793-16!Apex!Apex;;Short;1;26091,75;26085,00;31/10/2025 15:13:28;31/10/2025 15:14:44;;Close;135,00 $;193,00 $;2,00 $;0,00 $;0,00 $;0,00 $;0,00 $;125,00 $;185,00 $;1,00 $;0
""".encode('utf-8')

# CSV content with one malformed row (bad date) and one valid row
INVALID_ROW_CSV_CONTENT = """NinjaTrader Grid 2025-11-03 05-05 .csv
Trade number;Instrument;Account;Strategy;Market pos.;Qty;Entry price;Exit price;Entry time;Exit time;Entry name;Exit name;Profit;Cum. net profit;Commission;Clearing Fee;Exchange Fee;IP Fee;NFA Fee;MAE;MFE;ETD;Bars
1;MNQ DEC25;PA-APEX-226793-16!Apex!Apex;;Long;2;26068,00;26082,50;28/10/2025 14:30:26;28/10/2025 14:31:14;;Close;58,00 $;58,00 $;1,00 $;0,50 $;0,50 $;0,20 $;0,10 $;25,00 $;63,00 $;5,00 $;0
2;NQ DEC25;PA-APEX-226793-16!Apex!Apex;;Short;1;26091,75;26085,00;INVALID-DATE;31/10/2025 15:14:44;;Close;135,00 $;193,00 $;2,00 $;0,00 $;0,00 $;0,00 $;0,00 $;125,00 $;185,00 $;1,00 $;0
""".encode('utf-8')

# CSV content with no valid header
NO_HEADER_CSV_CONTENT = """Some random line
Another random line
""".encode('utf-8')

def test_parse_csv_with_valid_data(ninja_trader_parser):
    """
    Tests that the parser correctly processes a valid NinjaTrader CSV file.
    """
    trades, errors = ninja_trader_parser.parse_csv(VALID_CSV_CONTENT)

    assert len(trades) == 2
    assert len(errors) == 0

    # --- Assertions for the first trade (Long) ---
    trade1 = trades[0]
    assert trade1['symbol_snapshot'] == 'MNQ DEC25'
    assert trade1['direction'] == TradeDirection.LONG
    assert trade1['entry_timestamp'] == datetime(2025, 10, 28, 14, 30, 26)
    assert trade1['exit_timestamp'] == datetime(2025, 10, 28, 14, 31, 14)
    assert trade1['entry_price'] == 26068.00
    assert trade1['exit_price'] == 26082.50
    assert trade1['position_size'] == 2
    assert trade1['p_l'] == 58.00
    assert trade1['commissions'] == 1.00
    assert trade1['fees'] == pytest.approx(0.50 + 0.50 + 0.20 + 0.10)
    assert trade1['gross_p_l'] == pytest.approx(58.00 + 1.00 + 1.30)
    assert 'dedupe_key' in trade1

    # --- Assertions for the second trade (Short) ---
    trade2 = trades[1]
    assert trade2['symbol_snapshot'] == 'NQ DEC25'
    assert trade2['direction'] == TradeDirection.SHORT
    assert trade2['entry_timestamp'] == datetime(2025, 10, 31, 15, 13, 28)
    assert trade2['exit_timestamp'] == datetime(2025, 10, 31, 15, 14, 44)
    assert trade2['entry_price'] == 26091.75
    assert trade2['exit_price'] == 26085.00
    assert trade2['position_size'] == 1
    assert trade2['p_l'] == 135.00
    assert trade2['commissions'] == 2.00
    assert trade2['fees'] == 0.0
    assert trade2['gross_p_l'] == 137.00
    assert 'dedupe_key' in trade2

def test_parse_csv_skips_invalid_rows(ninja_trader_parser):
    """
    Tests that the parser skips rows with formatting errors but still processes valid rows.
    """
    trades, errors = ninja_trader_parser.parse_csv(INVALID_ROW_CSV_CONTENT)

    # It should skip the row with the "INVALID-DATE" and parse the valid one.
    assert len(trades) == 1
    assert trades[0]['symbol_snapshot'] == 'MNQ DEC25'

    # It should report one error.
    assert len(errors) == 1
    error = errors[0]
    assert error['line'] == 4
    assert "INVALID-DATE" in error['data']['Entry time']

def test_parse_csv_with_no_header(ninja_trader_parser):
    """
    Tests that the parser raises a ValueError if a valid header row cannot be found.
    """
    with pytest.raises(ValueError, match="Could not find a valid header row"):
        ninja_trader_parser.parse_csv(NO_HEADER_CSV_CONTENT)
