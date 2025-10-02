# backend/tests/services/metrics/test_metrics_calculator.py

import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from uuid import uuid4
from app.Services.metrics.metrics_calculator import MetricsCalculator
from app.Models.trade import Trade

# A dummy trading_account_id to be used in tests
DUMMY_ACCOUNT_ID = uuid4()

@pytest.fixture
def sample_trades_models():
    """Provides a list of valid Trade model instances for testing."""
    return [
        Trade(
            id=uuid4(), trading_account_id=DUMMY_ACCOUNT_ID,
            p_l=Decimal('100.50'), entry_price=Decimal('150.00'), exit_price=Decimal('151.50'),
            stop_loss_price=Decimal('149.00'), take_profit_price=Decimal('152.00'),
            position_size=10, direction='Long',
            entry_timestamp=datetime(2023, 1, 1, 10, 0, 0), exit_timestamp=datetime(2023, 1, 1, 11, 0, 0),
            lowest_price_during_trade=Decimal('149.50'), highest_price_during_trade=Decimal('151.75'),
            created_at=datetime(2023, 1, 1, 9, 0, 0),
        ),
        Trade(
            id=uuid4(), trading_account_id=DUMMY_ACCOUNT_ID,
            p_l=Decimal('-50.25'), entry_price=Decimal('151.00'), exit_price=Decimal('150.25'),
            stop_loss_price=Decimal('152.00'), take_profit_price=Decimal('150.00'),
            position_size=5, direction='Short',
            entry_timestamp=datetime(2023, 1, 2, 14, 0, 0), exit_timestamp=datetime(2023, 1, 2, 15, 0, 0),
            lowest_price_during_trade=Decimal('150.10'), highest_price_during_trade=Decimal('151.50'),
            created_at=datetime(2023, 1, 2, 13, 0, 0),
        )
    ]

def create_trade_with_timestamp(pnl, days_offset):
    """Helper to create a trade with a timestamp."""
    return Trade(
        id=uuid4(),
        trading_account_id=DUMMY_ACCOUNT_ID,
        p_l=Decimal(pnl),
        entry_timestamp=datetime(2023, 1, 1) + timedelta(days=days_offset),
        exit_timestamp=datetime(2023, 1, 1) + timedelta(days=days_offset, hours=1)
    )

def test_initialization(sample_trades_models):
    calc = MetricsCalculator(sample_trades_models, initial_balance=10000)
    assert len(calc.trades) == 2
    assert calc.initial_balance == 10000

def test_initialization_no_trades():
    calc = MetricsCalculator([], initial_balance=5000)
    assert len(calc.trades) == 0
    assert calc.initial_balance == 5000

def test_calculate_all_metrics_no_trades():
    calc = MetricsCalculator([], initial_balance=1000)
    metrics = calc.get_all_metrics()
    assert metrics['trade_count'] == 0
    assert metrics['net_pnl'] == 0

def test_full_calculation_flow(sample_trades_models):
    calc = MetricsCalculator(sample_trades_models, initial_balance=25000)
    all_metrics = calc.get_all_metrics()
    assert all_metrics is not None
    assert 'net_pnl' in all_metrics
    assert all_metrics['net_pnl'] == pytest.approx(50.25)

def test_total_pl():
    trades = [create_trade_with_timestamp(pnl, i) for i, pnl in enumerate(['150.50', '-50.25', '10.00'])]
    calc = MetricsCalculator(trades, initial_balance=10000)
    assert calc.net_pnl == Decimal('110.25')

def test_trade_counts():
    trades = [create_trade_with_timestamp(pnl, i) for i, pnl in enumerate(['150.50', '-50.25', '0', '20.00'])]
    calc = MetricsCalculator(trades, initial_balance=10000)
    assert calc.trade_count == 4
    assert calc.winning_trades_count == 2
    assert calc.losing_trades_count == 1
    assert calc.breakeven_trades_count == 1

def test_avg_win_loss():
    trades = [create_trade_with_timestamp(pnl, i) for i, pnl in enumerate(['100', '200', '-50', '-30'])]
    calc = MetricsCalculator(trades, initial_balance=10000)
    metrics = calc.get_all_metrics()
    assert metrics['avg_win'] == Decimal('150')
    assert metrics['avg_loss'] == Decimal('40')

def test_profit_factor():
    trades = [create_trade_with_timestamp(pnl, i) for i, pnl in enumerate(['200', '-100'])]
    calc = MetricsCalculator(trades, initial_balance=10000)
    metrics = calc.get_all_metrics()
    assert metrics['profit_factor'] == Decimal('2.0')

def test_win_rate():
    trades = [create_trade_with_timestamp(pnl, i) for i, pnl in enumerate(['100', '-50', '20', '-10'])]
    calc = MetricsCalculator(trades, initial_balance=10000)
    metrics = calc.get_all_metrics()
    assert metrics['win_rate'] == Decimal('50.0')

def test_expectancy():
    trades = [create_trade_with_timestamp(pnl, i) for i, pnl in enumerate(['60', '-20'])]
    calc = MetricsCalculator(trades, initial_balance=10000)
    metrics = calc.get_all_metrics()
    assert metrics['expectancy'] == Decimal('20')

def test_average_hold_time():
    trades = [
        Trade(id=uuid4(), trading_account_id=DUMMY_ACCOUNT_ID, p_l=Decimal('1'), entry_timestamp=datetime(2023,1,1, 10,0,0), exit_timestamp=datetime(2023,1,1, 10,10,0)), # 10 min
        Trade(id=uuid4(), trading_account_id=DUMMY_ACCOUNT_ID, p_l=Decimal('1'), entry_timestamp=datetime(2023,1,1, 11,0,0), exit_timestamp=datetime(2023,1,1, 11,20,0)), # 20 min
    ]
    calc = MetricsCalculator(trades, initial_balance=10000)
    metrics = calc.get_all_metrics()
    assert metrics['average_hold_time'] == 15.0

def test_max_consecutive_wins_losses():
    trades = [create_trade_with_timestamp(pnl, i) for i, pnl in enumerate(['10', '20', '-5', '30', '40', '50', '-10', '-15'])]
    calc = MetricsCalculator(trades, initial_balance=10000)
    metrics = calc.get_all_metrics()
    assert metrics['max_consecutive_wins'] == 3
    assert metrics['max_consecutive_losses'] == 2