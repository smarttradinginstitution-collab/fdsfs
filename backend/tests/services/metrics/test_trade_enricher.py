# backend/tests/services/metrics/test_trade_enricher.py

import pytest
from decimal import Decimal
from app.Services.metrics.trade_enricher import enrich_trade_with_advanced_metrics

@pytest.fixture
def sample_trade():
    return {
        'p_l': '100.50',
        'entry_price': '150.00',
        'exit_price': '151.50',
        'stop_loss_price': '149.00',
        'take_profit_price': '152.00',
        'position_size': '10',
        'direction': 'Long',
        'lowest_price_during_trade': '149.50',
        'highest_price_during_trade': '151.75',
    }

def test_enrich_trade_with_advanced_metrics(sample_trade):
    enriched_trade = enrich_trade_with_advanced_metrics(sample_trade)
    assert 'mae_usd' in enriched_trade
    assert 'mfe_usd' in enriched_trade
    assert 'planned_rr' in enriched_trade
    assert 'realized_rr' in enriched_trade
    assert enriched_trade['mae_usd'] < 0
    assert enriched_trade['mfe_usd'] > 0

def test_enrich_trade_short_direction(sample_trade):
    sample_trade['direction'] = 'Short'
    sample_trade['p_l'] = '-50.25'
    sample_trade['exit_price'] = '150.25'
    enriched_trade = enrich_trade_with_advanced_metrics(sample_trade)
    assert enriched_trade['mae_usd'] < 0
    assert enriched_trade['mfe_usd'] > 0

def test_enrich_trade_no_risk():
    trade = {'p_l': '100'}
    enriched_trade = enrich_trade_with_advanced_metrics(trade)
    assert enriched_trade['planned_rr'] == 0
    assert enriched_trade['realized_rr'] == 0

def test_enrich_trade_no_trade():
    assert enrich_trade_with_advanced_metrics(None) is None

def test_enrich_trade_zero_pnl_in_points():
    trade = {'p_l': '100', 'entry_price': '100', 'exit_price': '100', 'direction': 'Long'}
    enriched = enrich_trade_with_advanced_metrics(trade)
    assert 'mae_usd' in enriched
