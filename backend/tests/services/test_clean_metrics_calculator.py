import pytest
from decimal import Decimal
from datetime import datetime
from app.Services.metrics.metrics_calculator import MetricsCalculator
from app.Schemas.stats import PerformanceMetricsResponse

import uuid

# Sample trade data for testing
USER_ID = uuid.uuid4()
SAMPLE_TRADES = [
    {
        'id': uuid.uuid4(), 'user_id': USER_ID, 'created_at': datetime(2023, 1, 1, 9, 0),
        'p_l': '150.00', 'direction': 'Long', 'entry_price': '100.00', 'exit_price': '101.50',
        'stop_loss_price': '99.00', 'take_profit_price': '103.00', 'position_size': '100',
        'entry_timestamp': datetime(2023, 1, 1, 9, 30), 'exit_timestamp': datetime(2023, 1, 1, 10, 30),
        'lowest_price_during_trade': '99.50', 'highest_price_during_trade': '102.00', 'setup': 'Breakout',
        'tags': []
    },
    {
        'id': uuid.uuid4(), 'user_id': USER_ID, 'created_at': datetime(2023, 1, 2, 10, 0),
        'p_l': '-50.00', 'direction': 'Short', 'entry_price': '102.00', 'exit_price': '102.50',
        'stop_loss_price': '103.00', 'take_profit_price': '101.00', 'position_size': '100',
        'entry_timestamp': datetime(2023, 1, 2, 11, 0), 'exit_timestamp': datetime(2023, 1, 2, 11, 45),
        'lowest_price_during_trade': '101.80', 'highest_price_during_trade': '103.20', 'setup': 'Reversal',
        'tags': []
    },
    {
        'id': uuid.uuid4(), 'user_id': USER_ID, 'created_at': datetime(2023, 1, 3, 13, 0),
        'p_l': '200.00', 'direction': 'Long', 'entry_price': '105.00', 'exit_price': '107.00',
        'stop_loss_price': '104.00', 'take_profit_price': '108.00', 'position_size': '100',
        'entry_timestamp': datetime(2023, 1, 3, 14, 0), 'exit_timestamp': datetime(2023, 1, 3, 15, 0),
        'lowest_price_during_trade': '104.80', 'highest_price_during_trade': '107.50', 'setup': 'Breakout',
        'tags': []
    }
]

@pytest.fixture
def metrics_calculator():
    """Returns a MetricsCalculator instance initialized with sample trades."""
    return MetricsCalculator(trades=SAMPLE_TRADES, user_timezone="UTC")

def test_calculate_all_metrics_returns_pydantic_model(metrics_calculator):
    """
    Tests that calculate_all_metrics returns a valid PerformanceMetricsResponse object.
    """
    # Act
    result = metrics_calculator.calculate_all_metrics()

    # Assert
    assert isinstance(result, PerformanceMetricsResponse), "The result should be an instance of PerformanceMetricsResponse"

def test_pydantic_model_has_float_values(metrics_calculator):
    """
    Tests that the numeric fields in the returned Pydantic model are floats,
    not Decimals, ensuring correct JSON serialization.
    """
    # Act
    result = metrics_calculator.calculate_all_metrics()
    stats = result.stats

    # Assert
    # Check a few key fields to confirm they are floats
    assert isinstance(stats.total_pl, float), f"total_pl should be float, but is {type(stats.total_pl)}"
    assert isinstance(stats.avg_win, float), f"avg_win should be float, but is {type(stats.avg_win)}"
    assert isinstance(stats.expectancy, float), f"expectancy should be float, but is {type(stats.expectancy)}"
    assert isinstance(stats.sharpe_ratio, float), f"sharpe_ratio should be float, but is {type(stats.sharpe_ratio)}"

def test_total_pnl_calculation(metrics_calculator):
    """
    Tests that the total P&L is calculated correctly.
    """
    # Act
    result = metrics_calculator.calculate_all_metrics()

    # Assert
    # Expected P&L = 150 - 50 + 200 = 300
    assert result.stats.total_pl == pytest.approx(300.0)

def test_trade_count_calculation(metrics_calculator):
    """
    Tests that the trade count is correct.
    """
    # Act
    result = metrics_calculator.calculate_all_metrics()

    # Assert
    assert result.stats.trade_count == 3
    assert result.stats.winning_trades_count == 2
    assert result.stats.losing_trades_count == 1
