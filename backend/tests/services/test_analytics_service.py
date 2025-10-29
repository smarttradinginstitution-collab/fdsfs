# backend/tests/services/test_analytics_service.py

import pytest
import numpy as np
from uuid import uuid4
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.Services.analytics_service import AnalyticsService
from app.Models import (
    GeneralAccount,
    TradingAccount,
    Playbook,
    Trade
)

# Mark all tests in this module as asyncio tests
pytestmark = pytest.mark.anyio

@pytest.fixture
async def setup_test_data(db_session: AsyncSession):
    """
    Fixture to set up realistic data in the test database.
    Creates a GeneralAccount, TradingAccount, Playbooks, and a series of Trades.
    """
    # 1. Create parent accounts
    general_account = GeneralAccount(id=uuid4(), user_id=uuid4(), label="Test General Account")
    trading_account = TradingAccount(id=uuid4(), general_account_id=general_account.id, label="Test Trading Account", broker_id=uuid4())

    db_session.add_all([general_account, trading_account])
    await db_session.flush()

    # 2. Create Playbooks (Strategies)
    playbook_a = Playbook(id=uuid4(), title="Breakout Strategy", description="A test description", general_account_id=general_account.id)
    playbook_b = Playbook(id=uuid4(), title="Mean Reversion", description="Another test description", general_account_id=general_account.id)

    db_session.add_all([playbook_a, playbook_b])
    await db_session.flush()

    # 3. Create a series of Trades
    trades_data = [
        # Giorno 1 (Lunedì): Win, Win
        {"p_l": 100, "entry_ts": datetime(2023, 10, 16, 9, 0), "exit_ts": datetime(2023, 10, 16, 10, 0), "playbook": playbook_a},
        {"p_l": 150, "entry_ts": datetime(2023, 10, 16, 11, 0), "exit_ts": datetime(2023, 10, 16, 12, 30), "playbook": playbook_b},
        # Giorno 2 (Martedì): Loss
        {"p_l": -50, "entry_ts": datetime(2023, 10, 17, 9, 0), "exit_ts": datetime(2023, 10, 17, 9, 45), "playbook": playbook_a},
        # Giorno 3 (Mercoledì): Win, Loss, Loss
        {"p_l": 200, "entry_ts": datetime(2023, 10, 18, 10, 0), "exit_ts": datetime(2023, 10, 18, 15, 0), "playbook": playbook_a},
        {"p_l": -70, "entry_ts": datetime(2023, 10, 18, 15, 0), "exit_ts": datetime(2023, 10, 18, 16, 0), "playbook": playbook_b},
        {"p_l": -80, "entry_ts": datetime(2023, 10, 18, 16, 0), "exit_ts": datetime(2023, 10, 18, 17, 0), "playbook": playbook_b},
        # Giorno 4 (Giovedì): Breakeven
        {"p_l": 0, "entry_ts": datetime(2023, 10, 19, 9, 0), "exit_ts": datetime(2023, 10, 19, 10, 0), "playbook": None},
        # Giorno 5 (Venerdì, mese diverso): Win
        {"p_l": 300, "entry_ts": datetime(2023, 11, 3, 10, 0), "exit_ts": datetime(2023, 11, 3, 14, 0), "playbook": playbook_a},
    ]

    for data in trades_data:
        trade = Trade(
            id=uuid4(),
            trading_account_id=trading_account.id,
            p_l=data["p_l"],
            entry_timestamp=data["entry_ts"],
            exit_timestamp=data["exit_ts"],
            playbook=data["playbook"]
        )
        db_session.add(trade)

    await db_session.commit()

    # Return the ID of the trading account for querying
    return trading_account.id


async def test_get_performance_metrics_integration(db_session: AsyncSession, setup_test_data: uuid4):
    """
    Testa che le metriche di performance avanzate siano calcolate correttamente
    in un ambiente di integrazione con database.
    """
    # Arrange
    trading_account_id = setup_test_data
    service = AnalyticsService(db=db_session)

    # Act
    result = await service.get_performance_metrics(
        trading_account_ids=[trading_account_id],
        start_date=date(2023, 1, 1),
        end_date=date(2023, 12, 31)
    )
    stats = result.stats

    # Assert - Valori attesi calcolati manualmente sulla base dei dati di test
    assert stats.trade_count == 8
    assert stats.net_pnl == pytest.approx(550.0)
    assert stats.winning_trades == 4
    assert stats.losing_trades == 3
    assert stats.breakeven_trades == 1
    assert stats.win_rate == pytest.approx(50.0)
    assert stats.profit_factor == pytest.approx(3.75)
    assert stats.max_consecutive_wins == 2
    assert stats.max_consecutive_losses == 2
    assert stats.average_hold_time == pytest.approx(915 / 8)
    assert stats.expectancy == pytest.approx(68.75)
    assert stats.max_drawdown_abs == pytest.approx(150.0)

    pnl_list = [100, 150, -50, 200, -70, -80, 0, 300]
    pnl_std = np.std(pnl_list)
    avg_pnl = sum(pnl_list) / len(pnl_list)
    assert stats.sharpe_ratio == pytest.approx(avg_pnl / pnl_std)

async def test_get_processed_stats_integration(db_session: AsyncSession, setup_test_data: uuid4):
    """
    Testa che le statistiche aggregate (per strategia, giorno, etc.) siano corrette
    in un ambiente di integrazione con database.
    """
    # Arrange
    trading_account_id = setup_test_data
    service = AnalyticsService(db=db_session)

    # Act
    result = await service.get_processed_stats(
        trading_account_ids=[trading_account_id],
        start_date=date(2023, 1, 1),
        end_date=date(2023, 12, 31)
    )

    # --- Assert By Strategy ---
    by_strategy = result.by_strategy
    assert "Breakout Strategy" in by_strategy
    assert "Mean Reversion" in by_strategy
    assert by_strategy["Breakout Strategy"].total_pnl == pytest.approx(550.0)
    assert by_strategy["Breakout Strategy"].win_rate == pytest.approx(75.0)
    assert by_strategy["Mean Reversion"].total_pnl == pytest.approx(0.0)
    assert by_strategy["Mean Reversion"].win_rate == pytest.approx(100 / 3)

    # --- Assert By Day of Week ---
    by_day = result.by_day_of_week
    assert by_day["Monday"].total_pnl == pytest.approx(250)
    assert by_day["Tuesday"].total_pnl == pytest.approx(-50)
    assert by_day["Wednesday"].total_pnl == pytest.approx(50)
    assert by_day["Friday"].total_pnl == pytest.approx(300)

    # --- Assert Win/Loss Days ---
    win_loss_days = result.win_loss_days
    assert win_loss_days.winningDays == 3
    assert win_loss_days.losingDays == 1
    assert win_loss_days.breakEvenDays == 1

    # --- Assert Monthly Totals ---
    monthly = result.monthly_totals
    assert monthly["2023-10"] == pytest.approx(250.0)
    assert monthly["2023-11"] == pytest.approx(300.0)

async def test_get_vantage_score_integration(db_session: AsyncSession, setup_test_data: uuid4):
    """
    Test that the Vantage Score is calculated correctly in an integration environment.
    """
    # Arrange
    trading_account_id = setup_test_data
    service = AnalyticsService(db=db_session)

    # Act
    result = await service.get_vantage_score(
        trading_account_ids=[trading_account_id],
        start_date=date(2023, 1, 1),
        end_date=date(2023, 12, 31)
    )

    # Assert
    assert isinstance(result.vantage_score, int)
    assert 0 <= result.vantage_score <= 100
    assert isinstance(result.win_rate_score, int)
    assert isinstance(result.profit_factor_score, int)
    assert isinstance(result.avg_win_loss_score, int)
    assert isinstance(result.recovery_factor_score, int)
    assert isinstance(result.max_drawdown_score, int)
    assert isinstance(result.consistency_score, int)