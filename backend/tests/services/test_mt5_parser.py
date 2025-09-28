# backend/tests/services/test_mt5_parser.py
import pytest
from datetime import datetime
from app.Services.mt5_parser import Mt5Parser
from app.Models.enums import TradeDirection

@pytest.fixture
def parser():
    return Mt5Parser()

@pytest.fixture
def valid_mt5_html_report():
    return b"""
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
  <head>
    <title>1511630653: $200k FTMO Free Trial - Report Cronistorico dei Trade</title>
    <style type="text/css">.hidden { display: none; }</style>
  </head>
<body>
<div align="center">
    <table>
        <tr align="center">
            <td colspan="14"><div style="font: 14pt Tahoma"><b>Report Cronistorico dei Trade</b></div></td>
        </tr>
        <tr><td></td></tr>
        <tr align="center">
            <th colspan="14"><div style="font: 10pt Tahoma"><b>Posizioni</b></div></th>
        </tr>
        <tr align="center" bgcolor="#E5F0FC">
            <td nowrap><b>Ora</b></td>
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
            <td class="hidden">hidden_val</td>
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
            <td>buy</td>
            <td class="hidden">hidden_val</td>
            <td>216.41</td>
            <td>46159.42</td>
            <td>46139.42</td>
            <td>46219.42</td>
            <td>2025.09.22 16:31:03</td>
            <td>46129.08</td>
            <td>0.00</td>
            <td>0.00</td>
            <td colspan="2">-6 565.88</td>
        </tr>
        <tr bgcolor="#FFFFFF" align="right">
            <td>2025.09.23 15:49:35</td>
            <td>311304063</td>
            <td>XAUUSD</td>
            <td>buy</td>
            <td class="hidden">hidden_val</td>
            <td>0.01</td>
            <td>3784.83</td>
            <td>3782.99</td>
            <td></td>
            <td>2025.09.23 16:00:08</td>
            <td>3782.87</td>
            <td>-0.06</td>
            <td>0.00</td>
            <td colspan="2">-1.96</td>
        </tr>
        <tr><td></td></tr>
        <tr align="center">
            <th colspan="14"><div style="font: 10pt Tahoma"><b>Ordini</b></div></th>
        </tr>
    </table>
</div>
</body>
</html>
"""

def test_parse_valid_mt5_report(parser, valid_mt5_html_report):
    """Test parsing a valid MT5 HTML report."""
    trades = parser.parse_performance_report(valid_mt5_html_report)

    assert len(trades) == 3

    # Test first trade
    trade1 = trades[0]
    assert trade1['entry_timestamp'] == datetime(2025, 9, 22, 13, 42, 50)
    assert trade1['external_id'] == '310402409'
    assert trade1['symbol_snapshot'] == 'XAUUSD'
    assert trade1['direction'] == TradeDirection.LONG
    assert trade1['position_size'] == 2.0
    assert trade1['entry_price'] == 3726.65
    assert trade1['stop_loss_price'] == 3725.75
    assert trade1['take_profit_price'] == 3727.20
    assert trade1['exit_timestamp'] == datetime(2025, 9, 22, 13, 43, 20)
    assert trade1['exit_price'] == 3725.65
    assert trade1['commissions'] == -10.44
    assert trade1['fees'] == 0.00
    assert trade1['gross_p_l'] == -200.00
    # Net P&L = gross - commissions - fees = -200.00 - (-10.44) - 0.00
    assert trade1['p_l'] == -189.56
    assert 'dedupe_key' in trade1

    # Test second trade
    trade2 = trades[1]
    assert trade2['position_size'] == 216.41
    assert trade2['gross_p_l'] == -6565.88
    assert trade2['commissions'] == 0.00
    assert trade2['fees'] == 0.00
    assert trade2['p_l'] == -6565.88

    # Test third trade (with empty T/P)
    trade3 = trades[2]
    assert trade3['position_size'] == 0.01
    assert trade3['entry_price'] == 3784.83
    assert trade3['stop_loss_price'] == 3782.99
    assert trade3['take_profit_price'] is None
    assert trade3['gross_p_l'] == -1.96
    assert trade3['commissions'] == -0.06
    assert trade3['fees'] == 0.00
    # Net P&L = -1.96 - (-0.06) - 0.00
    assert trade3['p_l'] == -1.90

def test_parse_invalid_report_no_header(parser):
    """Test parsing an HTML file that is missing the 'Posizioni' header."""
    html_content = b"<html><body><p>This is not a valid report.</p></body></html>"
    with pytest.raises(ValueError, match="Could not find the 'Posizioni' section header"):
        parser.parse_performance_report(html_content)

def test_parse_report_with_no_trades(parser):
    """Test parsing a report that has the header but no trade rows."""
    html_content = b"""
    <html><body>
    <table>
        <tr align="center"><th colspan="14"><div><b>Posizioni</b></div></th></tr>
        <tr align="center" bgcolor="#E5F0FC"><td><b>Ora</b></td></tr>
        <tr align="center"><th colspan="14"><div><b>Ordini</b></div></th></tr>
    </table>
    </body></html>
    """
    trades = parser.parse_performance_report(html_content)
    assert len(trades) == 0