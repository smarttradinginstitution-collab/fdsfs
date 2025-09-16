# backend/tests/services/metrics/test_metrics_calculator.py

import pytest
from decimal import Decimal
from datetime import datetime
import pytz
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

@pytest.fixture
def trades_for_streaks():
    return [
        {'p_l': '10'}, {'p_l': '20'}, {'p_l': '-5'}, {'p_l': '-10'},
        {'p_l': '15'}, {'p_l': '0'}, {'p_l': '-8'},
    ]

def test_initialization(sample_trades):
    calc = MetricsCalculator(sample_trades)
    assert len(calc.all_trades) == 2
    assert 'mae_points' in calc.all_trades[0]

def test_initialization_no_trades():
    calc = MetricsCalculator([])
    assert len(calc.all_trades) == 0

def test_unknown_timezone():
    calc = MetricsCalculator([], user_timezone="Invalid/Timezone")
    assert calc.tz == pytz.utc

def test_convert_to_local_tz():
    calc = MetricsCalculator([], user_timezone="America/New_York")
    utc_dt = datetime(2023, 1, 1, 12, 0, 0, tzinfo=pytz.utc)
    local_dt = calc._convert_to_local_tz(utc_dt)
    assert local_dt.hour == 7
    assert calc._convert_to_local_tz(None) is None
    assert calc._convert_to_local_tz("2023-01-01T12:00:00Z").hour == 7

def test_filter_trades_no_filters(sample_trades):
    filtered = MetricsCalculator.filter_trades(sample_trades, {})
    assert len(filtered) == len(sample_trades)

def test_streaks(trades_for_streaks):
    calc = MetricsCalculator(trades_for_streaks)
    base_stats = calc._calculate_base_stats()
    daily_pnl = [Decimal(t['p_l']) for t in trades_for_streaks]
    streaks = calc._calculate_streaks_and_consistency(base_stats['pnl_data'], daily_pnl)
    assert streaks['max_consecutive_wins'] == 2
    assert streaks['max_consecutive_losses'] == 2

def test_vantage_score_no_trades():
    calc = MetricsCalculator([])
    score = calc.calculate_vantage_score()
    assert score['vantage_score'] == 0

def test_calculate_all_metrics_no_trades():
    calc = MetricsCalculator([])
    metrics = calc.calculate_all_metrics()
    assert metrics['trades'] == []
    assert metrics['stats']['total_pl'] == 0

def test_prepare_trades_missing_data():
    trades = [{'direction': 'Long'}]
    calc = MetricsCalculator(trades)
    assert calc.all_trades[0]['mae_points'] == 0
    assert calc.all_trades[0]['net_roi'] == 0

def test_base_stats_no_wins(sample_trades):
    losing_trades = [t for t in sample_trades if Decimal(t['p_l']) < 0]
    calc = MetricsCalculator(losing_trades)
    stats = calc._calculate_base_stats()
    assert stats['avg_win'] == 0
    assert stats['profit_factor'] == Decimal('0')

def test_advanced_stats_edge_cases():
    trades = [{'p_l': '10', 'direction': 'Long', 'entry_price': '100', 'exit_price': '110'}] # no mfe
    calc = MetricsCalculator(trades)
    base_stats = calc._calculate_base_stats()
    adv_stats = calc._calculate_advanced_stats(base_stats)
    assert adv_stats['avg_sell_efficiency'] == 0

def test_calculate_trade_summary_no_trades():
    calc = MetricsCalculator([])
    summary = calc.calculate_trade_summary()
    assert summary['stats']['net_pnl'] == 0

def test_calculate_processed_stats_no_trades():
    calc = MetricsCalculator([])
    stats = calc.calculate_processed_stats()
    assert stats['general_stats']['total_pnl'] == 0

def test_full_calculation_flow(sample_trades):
    calc = MetricsCalculator(sample_trades, user_timezone="UTC")
    all_metrics = calc.calculate_all_metrics()
    assert all_metrics is not None
    assert 'trades' in all_metrics
    assert 'stats' in all_metrics
    vantage_score = calc.calculate_vantage_score()
    assert vantage_score is not None
    assert 'vantage_score' in vantage_score
    summary = calc.calculate_trade_summary()
    assert summary is not None
    assert 'stats' in summary
    processed = calc.calculate_processed_stats()
    assert processed is not None
    assert 'general_stats' in processed
    equity = calc.calculate_equity_curve()
    assert equity is not None
    assert 'labels' in equity

def test_infinite_profit_factor(sample_trades):
    winning_trades = [t for t in sample_trades if Decimal(t['p_l']) > 0]
    calc = MetricsCalculator(winning_trades)
    stats = calc._calculate_base_stats()
    assert stats['profit_factor_label'] == "∞"
    summary = calc.calculate_trade_summary()
    assert summary['stats']['profit_factor_label'] == "∞"
    with pytest.raises(TypeError):
        calc.calculate_vantage_score()

def test_zero_risk_rr_calculation():
    trades = [{'p_l': '100', 'entry_price': '100', 'stop_loss_price': '100', 'direction': 'Long'}]
    calc = MetricsCalculator(trades)
    base_stats = calc._calculate_base_stats()
    adv_stats = calc._calculate_advanced_stats(base_stats)
    assert adv_stats['avg_realized_rr'] == 0

def test_consistency_score_edge_cases():
    calc = MetricsCalculator([])
    base_stats = calc._calculate_base_stats()
    streaks = calc._calculate_streaks_and_consistency(base_stats['pnl_data'], [])
    assert streaks['consistency_score'] == 0

    trades = [{'p_l': '100', 'entry_timestamp': datetime(2023,1,1)}]
    calc = MetricsCalculator(trades)
    base_stats = calc._calculate_base_stats()
    daily_pnl = [Decimal(t['p_l']) for t in trades]
    streaks = calc._calculate_streaks_and_consistency(base_stats['pnl_data'], daily_pnl)
    assert streaks['consistency_score'] == 0

    # Test with profit but zero std dev
    trades = [
        {'p_l': '100', 'entry_timestamp': datetime(2023,1,1)},
        {'p_l': '100', 'entry_timestamp': datetime(2023,1,2)},
        {'p_l': '-0.01', 'entry_timestamp': datetime(2023,1,3)} # Add a small loss
    ]
    calc = MetricsCalculator(trades)
    score = calc.calculate_vantage_score()
    assert score['consistency_score'] < 100 # Should be high, but not 100

def test_filter_trades_rr_filter_edge_cases():
    trades = [
        {'p_l': '100', 'entry_price': '100', 'stop_loss_price': '90', 'position_size': '1'},
        {'p_l': '10', 'entry_price': '100', 'stop_loss_price': '100', 'position_size': '1'} # zero risk
    ]
    filters = {'min_rr': 5}
    filtered = MetricsCalculator.filter_trades(trades, filters)
    assert len(filtered) == 2

def test_base_stats_no_short_trades():
    trades = [{'p_l': '100', 'direction': 'Long'}]
    calc = MetricsCalculator(trades)
    stats = calc._calculate_base_stats()
    assert stats['shorts_win_percentage'] == 0

def test_base_stats_no_long_trades():
    trades = [{'p_l': '100', 'direction': 'Short'}]
    calc = MetricsCalculator(trades)
    stats = calc._calculate_base_stats()
    assert stats['longs_win_percentage'] == 0

def test_processed_stats_multiple_setups_and_days():
    trades = [
        {'p_l': '100', 'setup': 'Setup1', 'entry_timestamp': datetime(2023, 1, 2)}, # Week 1
        {'p_l': '-50', 'setup': 'Setup2', 'entry_timestamp': datetime(2023, 1, 3)}, # Week 1
        {'p_l': '200', 'setup': 'Setup1', 'entry_timestamp': datetime(2023, 1, 4)}, # Week 1
        {'p_l': '150', 'setup': 'Setup3', 'entry_timestamp': datetime(2023, 1, 9)}, # Week 2
    ]
    calc = MetricsCalculator(trades)
    stats = calc.calculate_processed_stats()
    assert len(stats['by_strategy']) == 3
    assert len(stats['daily_data']) == 4
    assert len(stats['weekly_totals']) == 2
