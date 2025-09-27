# backend/tests/services/test_tradovate_parser.py
import pytest
from app.Services.tradovate_parser import TradovateParser
from app.Models.enums import TradeDirection

@pytest.fixture
def parser():
    return TradovateParser()

def test_parse_valid_performance_report(parser):
    csv_content = """
Random metadata line 1
Random metadata line 2
symbol,_priceFormat,_priceFormatType,_tickSize,buyFillId,sellFillId,qty,buyPrice,sellPrice,pnl,boughtTimestamp,soldTimestamp,duration
NQZ5,-2,0,0.25,1,2,1,24861.0,24878.0,$340.00,09/22/2025 15:50:36,09/22/2025 15:54:58,4min 21sec
NQZ5,-2,0,0.25,4,3,1,24946.0,24933.75,$(245.00),09/23/2025 16:01:30,09/23/2025 15:58:43,2min 46sec
    """.strip().encode('utf-8')

    result = parser.parse_performance_report(csv_content)

    assert len(result) == 2

    # Test the long trade
    long_trade = result[0]
    assert long_trade['symbol_snapshot'] == 'NQZ5'
    assert long_trade['direction'] == TradeDirection.LONG
    assert long_trade['entry_price'] == 24861.0
    assert long_trade['exit_price'] == 24878.0
    assert long_trade['p_l'] == 340.0
    assert long_trade['position_size'] == 1.0
    assert 'dedupe_key' in long_trade

    # Test the short trade
    short_trade = result[1]
    assert short_trade['symbol_snapshot'] == 'NQZ5'
    assert short_trade['direction'] == TradeDirection.SHORT
    assert short_trade['entry_price'] == 24933.75
    assert short_trade['exit_price'] == 24946.0
    assert short_trade['p_l'] == -245.0
    assert short_trade['position_size'] == 1.0
    assert 'dedupe_key' in short_trade

def test_parser_handles_missing_header(parser):
    csv_content = b"this,is,just,some,random,csv,without,a,header"
    with pytest.raises(ValueError, match="Could not find a valid header row"):
        parser.parse_performance_report(csv_content)

def test_parser_skips_malformed_rows(parser):
    # Added buyfillid and sellfillid to the header and rows
    csv_content = """
symbol,pnl,boughtTimestamp,soldTimestamp,buyPrice,sellPrice,qty,buyfillid,sellfillid
VALID,100,09/22/2025 15:50:36,09/22/2025 15:54:58,10,20,1,1,2
INVALID_DATE,200,not-a-date,09/22/2025 15:54:58,10,20,1,3,4
VALID2,300,09/23/2025 15:50:36,09/23/2025 15:54:58,10,20,1,5,6
    """.strip().encode('utf-8')

    result = parser.parse_performance_report(csv_content)
    assert len(result) == 2
    assert result[0]['symbol_snapshot'] == 'VALID'
    assert result[1]['symbol_snapshot'] == 'VALID2'

def test_clean_pnl(parser):
    assert parser._clean_pnl("$1,234.56") == 1234.56
    assert parser._clean_pnl("$(500.00)") == -500.0
    assert parser._clean_pnl("-$50.25") == -50.25 # Although not in example, good to handle
    assert parser._clean_pnl("0") == 0.0
    assert parser._clean_pnl(None) == 0.0