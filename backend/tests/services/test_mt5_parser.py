import pytest
from datetime import datetime
from app.Services.mt5_parser import Mt5Parser
from app.Models.enums import TradeDirection

@pytest.fixture
def parser():
    return Mt5Parser()

@pytest.fixture
def valid_html_report_content():
    return b"""
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
  <head><title>Test Report</title></head>
<body>
<div align="center">
    <table cellspacing="1" cellpadding="3" border="0">
        <tr align="center">
            <th colspan="14"><div style="font: 10pt Tahoma"><b>Posizioni</b></div></th>
        </tr>
        <tr align="center" bgcolor="#E5F0FC">
            <td nowrap style="height: 30px"><b>Ora</b></td>
            <td nowrap><b>Posizione</b></td>
            <td nowrap><b>Simbolo</b></td>
            <td nowrap><b>Tipo</b></td>
            <td nowrap><b>Volume </b></td>
            <td nowrap><b>Prezzo</b></td>
            <td nowrap><b>S / L</b></td>
            <td nowrap><b>T / P</b></td>
            <td nowrap><b>Ora</b></td>
            <td nowrap><b>Prezzo</b></td>
            <td nowrap><b>Commissioni</b></td>
            <td nowrap><b>Swap </b></td>
            <td nowrap colspan="2"><b>Profitto</b></td>
        </tr>
        <tr bgcolor="#FFFFFF" align="right">
            <td>2025.09.22 13:42:50</td>
            <td>310402409</td>
            <td>XAUUSD</td>
            <td>buy</td>
            <td>2</td>
            <td>3726.65</td>
            <td>3725.75</td>
            <td>3727.20</td>
            <td>2025.09.22 13:43:20</td>
            <td>3725.65</td>
            <td>-10.44</td>
            <td>0.00</td>
            <td colspan="2">-200.00</td>
        </tr>
        <tr bgcolor="#F7F7F7" align="right">
            <td>2025.09.22 16:31:00</td>
            <td>310542945</td>
            <td>US30.cash</td>
            <td>sell</td>
            <td>216.41</td>
            <td>46159.42</td>
            <td>46139.42</td>
            <td>46219.42</td>
            <td>2025.09.22 16:31:03</td>
            <td>46129.08</td>
            <td>0.00</td>
            <td>-5.50</td>
            <td colspan="2">-6 565.88</td>
        </tr>
    </table>
</div>
</body>
</html>
"""

def test_parse_valid_html_report(parser, valid_html_report_content):
    result = parser.parse_performance_report(valid_html_report_content)

    assert len(result) == 2

    # Test the long trade
    long_trade = result[0]
    assert long_trade['symbol_snapshot'] == 'XAUUSD'
    assert long_trade['direction'] == TradeDirection.LONG
    assert long_trade['entry_timestamp'] == datetime(2025, 9, 22, 13, 42, 50)
    assert long_trade['exit_timestamp'] == datetime(2025, 9, 22, 13, 43, 20)
    assert long_trade['entry_price'] == 3726.65
    assert long_trade['exit_price'] == 3725.65
    assert long_trade['gross_p_l'] == -200.00
    assert long_trade['position_size'] == 2.0
    assert long_trade['commissions'] == -10.44
    assert long_trade['fees'] == -10.44 # fees = commissions + swap
    assert 'dedupe_key' in long_trade

    # Test the short trade
    short_trade = result[1]
    assert short_trade['symbol_snapshot'] == 'US30.cash'
    assert short_trade['direction'] == TradeDirection.SHORT
    assert short_trade['entry_timestamp'] == datetime(2025, 9, 22, 16, 31, 0)
    assert short_trade['exit_timestamp'] == datetime(2025, 9, 22, 16, 31, 3)
    assert short_trade['entry_price'] == 46159.42
    assert short_trade['exit_price'] == 46129.08
    assert short_trade['gross_p_l'] == -6565.88
    assert short_trade['position_size'] == 216.41
    assert short_trade['commissions'] == 0.00
    assert short_trade['fees'] == -5.50
    assert 'dedupe_key' in short_trade

def test_parser_handles_missing_positions_table(parser):
    html_content = b"<html><body><p>No tables here</p></body></html>"
    with pytest.raises(ValueError, match="Could not find the 'Posizioni' table"):
        parser.parse_performance_report(html_content)

def test_parser_skips_malformed_rows(parser):
    html_content = b"""
    <html><body>
    <table>
        <tr><th><b>Posizioni</b></th></tr>
        <tr><td><b>Ora</b></td><td><b>Posizione</b></td><td><b>Simbolo</b></td><td><b>Tipo</b></td><td><b>Volume</b></td><td><b>Prezzo</b></td><td><b>Ora</b></td><td><b>Prezzo</b></td><td><b>Commissioni</b></td><td><b>Swap</b></td><td><b>Profitto</b></td></tr>
        <tr><td>2025.09.22 13:42:50</td><td>310402409</td><td>XAUUSD</td><td>buy</td><td>2</td><td>3726.65</td><td>2025.09.22 13:43:20</td><td>3725.65</td><td>-10.44</td><td>0.00</td><td>-200.00</td></tr>
        <tr><td>invalid-date</td><td>310542945</td><td>US30.cash</td><td>sell</td><td>216.41</td><td>46159.42</td><td>2025.09.22 16:31:03</td><td>46129.08</td><td>0.00</td><td>-5.50</td><td>-6 565.88</td></tr>
        <tr><td>2025.09.23 10:00:00</td><td>310542946</td><td>EURUSD</td><td>buy</td><td>1</td><td>1.1200</td><td>2025.09.23 10:05:00</td><td>1.1250</td><td>-1.00</td><td>0.00</td><td>50.00</td></tr>
    </table>
    </body></html>
    """
    result = parser.parse_performance_report(html_content)
    assert len(result) == 2
    assert result[0]['symbol_snapshot'] == 'XAUUSD'
    assert result[1]['symbol_snapshot'] == 'EURUSD'


def test_clean_price(parser):
    assert parser._clean_price("1 234.56") == 1234.56
    assert parser._clean_price("500.00") == 500.0
    assert parser._clean_price(" -50.25 ") == -50.25
    assert parser._clean_price("") is None
    assert parser._clean_price(None) is None

def test_clean_pnl(parser):
    assert parser._clean_pnl("-6 565.88") == -6565.88
    assert parser._clean_pnl("100.00") == 100.0
    assert parser._clean_pnl(" -10.44 ") == -10.44
    assert parser._clean_pnl("0.00") == 0.0
    assert parser._clean_pnl(None) == 0.0

def test_parse_timestamp(parser):
    assert parser._parse_timestamp("2025.09.22 13:42:50") == datetime(2025, 9, 22, 13, 42, 50)
    assert parser._parse_timestamp("not-a-date") is None
    assert parser._parse_timestamp(None) is None