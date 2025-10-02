import pytest
from decimal import Decimal
from datetime import datetime
from uuid import uuid4
from app.Services.metrics.metrics_calculator import MetricsCalculator
from app.Models.trade import Trade

DUMMY_ACCOUNT_ID = uuid4()

def dict_to_trade(data: dict) -> Trade:
    """Converts a dictionary to a Trade model instance for testing."""
    base_trade = {
        "id": uuid4(),
        "trading_account_id": DUMMY_ACCOUNT_ID,
        "p_l": Decimal('0'),
        "entry_timestamp": datetime(2023, 1, 1),
        "exit_timestamp": datetime(2023, 1, 1, 1),
    }

    numeric_keys = {
        'p_l', 'entry_price', 'exit_price', 'stop_loss_price', 'take_profit_price',
        'lowest_price_during_trade', 'highest_price_during_trade'
    }

    processed_data = {}
    for key, value in data.items():
        if key in numeric_keys and isinstance(value, str):
            processed_data[key] = Decimal(value)
        else:
            processed_data[key] = value

    final_data = {**base_trade, **processed_data}
    return Trade(**final_data)

def test_sell_efficiency():
    long_trade_dict = {
        'p_l': '100', 'entry_price': '100', 'exit_price': '110',
        'highest_price_during_trade': '120', 'lowest_price_during_trade': '99',
        'direction': 'Long'
    }
    calc_long = MetricsCalculator([dict_to_trade(long_trade_dict)], initial_balance=10000)
    metrics = calc_long.get_all_metrics()
    assert metrics is not None

def test_total_efficiency():
    long_trade_dict = {
        'entry_price': '100', 'highest_price_during_trade': '110', 'lowest_price_during_trade': '95',
        'direction': 'Long'
    }
    calc_long = MetricsCalculator([dict_to_trade(long_trade_dict)], initial_balance=10000)
    metrics = calc_long.get_all_metrics()
    assert metrics is not None

def test_planned_rr():
    long_trade_dict = {'entry_price': '100', 'stop_loss_price': '98', 'take_profit_price': '106'}
    calc_long = MetricsCalculator([dict_to_trade(long_trade_dict)], initial_balance=10000)
    metrics = calc_long.get_all_metrics()
    assert metrics is not None

def test_realized_rr():
    long_trade_dict = {
        'p_l': '40', 'entry_price': '100', 'stop_loss_price': '98', 'position_size': 10, 'r_multiple': 2.0
    }
    calc_long = MetricsCalculator([dict_to_trade(long_trade_dict)], initial_balance=10000)
    all_metrics = calc_long.get_all_metrics()
    assert all_metrics['avg_realized_rr'] == pytest.approx(2.0)