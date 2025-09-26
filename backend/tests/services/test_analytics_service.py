# backend/tests/services/test_analytics_service.py

import pytest
from uuid import uuid4
from datetime import date, datetime, timedelta
from unittest.mock import AsyncMock

from app.Services.analytics_service import AnalyticsService
from app.Models.trade import Trade

pytestmark = pytest.mark.anyio

@pytest.fixture
def mock_trades():
    """Fixture per fornire una lista di trade di esempio."""
    today = datetime.now()
    return [
        Trade(id=uuid4(), trading_account_id=uuid4(), p_l=100, entry_timestamp=today - timedelta(days=2)),
        Trade(id=uuid4(), trading_account_id=uuid4(), p_l=-50, entry_timestamp=today - timedelta(days=1)),
        Trade(id=uuid4(), trading_account_id=uuid4(), p_l=150, entry_timestamp=today),
        Trade(id=uuid4(), trading_account_id=uuid4(), p_l=0, entry_timestamp=today),
    ]

async def test_get_performance_metrics(mock_trades):
    """
    Testa che le metriche di performance siano calcolate correttamente.
    """
    # Arrange
    mock_db_session = AsyncMock()
    service = AnalyticsService(db=mock_db_session)

    # Mock del repository
    service.trade_repo.get_filtered_trades = AsyncMock(return_value=mock_trades)

    # Act
    result = await service.get_performance_metrics(
        trading_account_id=uuid4(),
        start_date=date.today() - timedelta(days=3),
        end_date=date.today()
    )

    # Assert
    stats = result.stats
    assert stats.trade_count == 4
    assert stats.net_pnl == 200.0
    assert stats.winning_trades == 2
    assert stats.losing_trades == 1
    assert stats.breakeven_trades == 1
    assert stats.gross_profit == 250.0
    assert stats.gross_loss == 50.0
    assert stats.win_rate == 50.0
    assert stats.profit_factor == 5.0
    assert stats.avg_win == 125.0
    assert stats.avg_loss == 50.0

async def test_get_equity_curve(mock_trades):
    """
    Testa che la curva di equity sia calcolata correttamente.
    """
    # Arrange
    mock_db_session = AsyncMock()
    service = AnalyticsService(db=mock_db_session)
    service.trade_repo.get_filtered_trades = AsyncMock(return_value=mock_trades)

    # Act
    result = await service.get_equity_curve(
        trading_account_id=uuid4(),
        start_date=date.today() - timedelta(days=3),
        end_date=date.today()
    )

    # Assert
    assert len(result.labels) == 4
    assert len(result.data) == 4
    assert result.data == [100.0, 50.0, 200.0, 200.0] # P&L Cumulativo