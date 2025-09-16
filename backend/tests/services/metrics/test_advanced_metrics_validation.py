# backend/tests/services/metrics/test_advanced_metrics_validation.py

import pytest
from decimal import Decimal
from app.Services.metrics.metrics_calculator import MetricsCalculator

def test_sell_efficiency():
    # Test for a winning Long trade
    long_trade = {
        'p_l': '100', 'entry_price': '100', 'exit_price': '110',
        'highest_price_during_trade': '120', 'lowest_price_during_trade': '99',
        'direction': 'Long'
    }
    # Manually calculated MFE for Long = 120 - 100 = 20
    # Manually calculated PnL in points = 110 - 100 = 10
    # Sell Efficiency = 10 / 20 = 0.5
    calc_long = MetricsCalculator([long_trade])
    stats_long = calc_long._calculate_advanced_stats(calc_long._calculate_base_stats())
    assert stats_long['avg_sell_efficiency'] == pytest.approx(50.0)

    # Test for a winning Short trade
    short_trade = {
        'p_l': '100', 'entry_price': '200', 'exit_price': '190',
        'highest_price_during_trade': '201', 'lowest_price_during_trade': '180',
        'direction': 'Short'
    }
    # Manually calculated MFE for Short = 200 - 180 = 20
    # Manually calculated PnL in points = 200 - 190 = 10
    # Sell Efficiency = 10 / 20 = 0.5
    calc_short = MetricsCalculator([short_trade])
    stats_short = calc_short._calculate_advanced_stats(calc_short._calculate_base_stats())
    assert stats_short['avg_sell_efficiency'] == pytest.approx(50.0)

def test_total_efficiency():
    # Test for a Long trade
    long_trade = {
        'entry_price': '100', 'highest_price_during_trade': '110', 'lowest_price_during_trade': '95',
        'direction': 'Long'
    }
    # MFE = 10, MAE = 5. Total Efficiency = 10 / (10 + 5) = 0.666...
    calc_long = MetricsCalculator([long_trade])
    stats_long = calc_long._calculate_advanced_stats(calc_long._calculate_base_stats())
    assert float(stats_long['avg_total_efficiency']) == pytest.approx(66.666, 0.01)

    # Test for a Short trade
    short_trade = {
        'entry_price': '200', 'highest_price_during_trade': '205', 'lowest_price_during_trade': '190',
        'direction': 'Short'
    }
    # MFE = 10, MAE = 5. Total Efficiency = 10 / (10 + 5) = 0.666...
    calc_short = MetricsCalculator([short_trade])
    stats_short = calc_short._calculate_advanced_stats(calc_short._calculate_base_stats())
    assert float(stats_short['avg_total_efficiency']) == pytest.approx(66.666, 0.01)

def test_planned_rr():
    # Test for a Long trade
    long_trade = {'entry_price': '100', 'stop_loss_price': '98', 'take_profit_price': '106'}
    # Risk = 2, Reward = 6. R:R = 3
    calc_long = MetricsCalculator([long_trade])
    stats_long = calc_long._calculate_advanced_stats(calc_long._calculate_base_stats())
    assert stats_long['avg_planned_rr'] == pytest.approx(3.0)

    # Test for a Short trade
    short_trade = {'entry_price': '200', 'stop_loss_price': '202', 'take_profit_price': '194'}
    # Risk = 2, Reward = 6. R:R = 3
    calc_short = MetricsCalculator([short_trade])
    stats_short = calc_short._calculate_advanced_stats(calc_short._calculate_base_stats())
    assert stats_short['avg_planned_rr'] == pytest.approx(3.0)

def test_realized_rr():
    # Test for a Long trade
    long_trade = {
        'p_l': '40', 'entry_price': '100', 'stop_loss_price': '98', 'position_size': '10'
    }
    # Risk = 2 points * 10 size = 20$. Realized R = 40 / 20 = 2
    calc_long = MetricsCalculator([long_trade])
    stats_long = calc_long._calculate_advanced_stats(calc_long._calculate_base_stats())
    assert stats_long['avg_realized_rr'] == pytest.approx(2.0)

    # Test for a Short trade
    short_trade = {
        'p_l': '60', 'entry_price': '200', 'stop_loss_price': '202', 'position_size': '15'
    }
    # Risk = 2 points * 15 size = 30$. Realized R = 60 / 30 = 2
    calc_short = MetricsCalculator([short_trade])
    stats_short = calc_short._calculate_advanced_stats(calc_short._calculate_base_stats())
    assert stats_short['avg_realized_rr'] == pytest.approx(2.0)
