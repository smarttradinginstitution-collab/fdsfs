# backend/tests/services/metrics/test_metrics_calculator_coverage.py

import pytest
from decimal import Decimal
from datetime import datetime
from app.Services.metrics.metrics_calculator import MetricsCalculator

@pytest.fixture
def sample_trades():
    return [
        {
            'p_l': '100.50', 'entry_price': '150.00', 'exit_price': '151.50', 'stop_loss_price': '149.00',
            'take_profit_price': '152.00', 'position_size': '10', 'direction': 'Long',
            'entry_timestamp': datetime(2023, 1, 1, 10, 0, 0), 'exit_timestamp': datetime(2023, 1, 1, 11, 0, 0),
            'lowest_price_during_trade': '149.50', 'highest_price_during_trade': '151.75', 'setup': 'Breakout',
            'created_at': datetime(2023, 1, 1, 9, 0, 0),
        },
        {
            'p_l': '-50.25', 'entry_price': '151.00', 'exit_price': '150.25', 'stop_loss_price': '152.00',
            'take_profit_price': '150.00', 'position_size': '5', 'direction': 'Short',
            'entry_timestamp': datetime(2023, 1, 2, 14, 0, 0), 'exit_timestamp': datetime(2023, 1, 2, 15, 0, 0),
            'lowest_price_during_trade': '150.10', 'highest_price_during_trade': '151.50', 'setup': 'Reversal',
            'created_at': datetime(2023, 1, 2, 13, 0, 0),
        }
    ]

def test_filter_trades_no_trades():
    filtered = MetricsCalculator.filter_trades([], {'min_duration': 10})
    assert len(filtered) == 0

def test_filter_trades_no_timestamps():
    trades = [{'p_l': '10'}]
    filtered = MetricsCalculator.filter_trades(trades, {'min_duration': 10})
    assert len(filtered) == 1 # Should not be filtered

def test_base_stats_only_wins():
    trades = [{'p_l': '100'}]
    calc = MetricsCalculator(trades)
    stats = calc._calculate_base_stats()
    assert stats['avg_loss'] == 0
    assert stats['average_win_loss_ratio'] == float('inf')
    assert stats['profit_factor_label'] == "∞"

def test_advanced_stats_no_drawdown():
    trades = [{'p_l': '10', 'entry_timestamp': datetime(2023,1,1)}, {'p_l': '20', 'entry_timestamp': datetime(2023,1,2)}]
    calc = MetricsCalculator(trades)
    base_stats = calc._calculate_base_stats()
    adv_stats = calc._calculate_advanced_stats(base_stats)
    assert adv_stats['max_drawdown_abs'] == 0
    assert adv_stats['recovery_factor'] == float('inf')

def test_vantage_score_scoring_branches():
    # Test different branches of the scoring logic
    trades = [
        {'p_l': '100', 'entry_price': '100', 'stop_loss_price': '90', 'position_size': '1', 'direction': 'Long', 'entry_timestamp': datetime(2023,1,1)},
        {'p_l': '-1', 'entry_price': '100', 'stop_loss_price': '110', 'position_size': '1', 'direction': 'Short', 'entry_timestamp': datetime(2023,1,1)}
    ]
    calc = MetricsCalculator(trades)
    score = calc.calculate_vantage_score()
    assert score['profit_factor_score'] == 100
    assert score['avg_win_loss_score'] == 100

    trades = [
        {'p_l': '-10', 'entry_price': '100', 'stop_loss_price': '110', 'position_size': '1', 'direction': 'Short', 'entry_timestamp': datetime(2023,1,1)},
        {'p_l': '1', 'entry_price': '100', 'stop_loss_price': '90', 'position_size': '1', 'direction': 'Long', 'entry_timestamp': datetime(2023,1,1)}
    ]
    calc = MetricsCalculator(trades)
    score = calc.calculate_vantage_score()
    assert score['profit_factor_score'] == 0
    assert score['avg_win_loss_score'] == 0

def test_prepare_trades_no_direction():
    trades = [{'p_l': '10', 'entry_price': '100', 'lowest_price_during_trade': '90', 'highest_price_during_trade': '110'}]
    calc = MetricsCalculator(trades)
    assert 'mae_points' in calc.all_trades[0]
    assert calc.all_trades[0]['mae_points'] == 0

def test_calculate_processed_stats_edge_cases():
    trades = [{'p_l': '10', 'setup': 'Test'}]
    calc = MetricsCalculator(trades)
    stats = calc.calculate_processed_stats()
    assert stats['by_strategy']['Test']['win_rate'] == 100
    assert stats['max_abs_pnl_by_strategy'] == 10.0

def test_filter_trades_rr_filter():
    trades = [
        {'p_l': '100', 'entry_price': '100', 'stop_loss_price': '90', 'position_size': '1'},
        {'p_l': '10', 'entry_price': '100', 'stop_loss_price': '99', 'position_size': '1'}
    ]
    # R-multiple for trade 1 is 10, for trade 2 is 10
    filters = {'min_rr': 11}
    filtered = MetricsCalculator.filter_trades(trades, filters)
    assert len(filtered) == 0
    filters = {'max_rr': 9}
    filtered = MetricsCalculator.filter_trades(trades, filters)
    assert len(filtered) == 0

def test_base_stats_only_long_trades(sample_trades):
    long_trades = [t for t in sample_trades if t['direction'] == 'Long']
    calc = MetricsCalculator(long_trades)
    stats = calc._calculate_base_stats()
    assert stats['short_trades_analysis']['total'] == 0
    assert stats['shorts_win_percentage'] == 0

def test_filter_trades_rr_filter_with_risk():
    trades = [
        {'p_l': '100', 'entry_price': '100', 'stop_loss_price': '90', 'position_size': '1', 'direction': 'Long'},
        {'p_l': '10', 'entry_price': '100', 'stop_loss_price': '99', 'position_size': '1', 'direction': 'Long'}
    ]
    # R-multiple for trade 1 is 10, for trade 2 is 10
    filters = {'min_rr': 5, 'max_rr': 15}
    filtered = MetricsCalculator.filter_trades(trades, filters)
    assert len(filtered) == 2

def test_base_stats_long_and_short(sample_trades):
    calc = MetricsCalculator(sample_trades)
    stats = calc._calculate_base_stats()
    assert stats['long_trades_analysis']['total'] > 0
    assert stats['short_trades_analysis']['total'] > 0

def test_processed_stats_multiple_days():
    trades = [
        {'p_l': '100', 'setup': 'A', 'entry_timestamp': datetime(2023,1,1)},
        {'p_l': '50', 'setup': 'B', 'entry_timestamp': datetime(2023,1,2)},
        {'p_l': '200', 'setup': 'A', 'entry_timestamp': datetime(2023,1,8)}, # New week
    ]
    calc = MetricsCalculator(trades)
    stats = calc.calculate_processed_stats()
    assert len(stats['daily_data']) == 3
    assert len(stats['by_strategy']) == 2
    assert len(stats['weekly_totals']) == 2
