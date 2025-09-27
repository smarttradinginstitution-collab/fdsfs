# backend/tests/services/test_analytics_service.py

import pytest
import numpy as np
from decimal import Decimal
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
    Creates a GeneralAccount, TradingAccount, Playbooks, and a series of Trades
    with gross P&L, fees, and commissions.
    """
    # 1. Create parent accounts
    general_account = GeneralAccount(id=uuid4(), user_id=uuid4(), label="Test General Account")
    trading_account = TradingAccount(id=uuid4(), general_account_id=general_account.id, label="Test Trading Account", broker_id=uuid4())

    db_session.add_all([general_account, trading_account])
    await db_session.flush()

    # 2. Create Playbooks (Strategies)
    playbook_a = Playbook(id=uuid4(), title="Breakout Strategy", general_account_id=general_account.id)
    playbook_b = Playbook(id=uuid4(), title="Mean Reversion", general_account_id=general_account.id)

    db_session.add_all([playbook_a, playbook_b])
    await db_session.flush()

    # 3. Create a series of Trades with costs
    trades_data = [
        # Giorno 1 (Lunedì): Win, Win -> Net Win, Win
        {"gross_p_l": 100, "fees": 5, "commissions": 2.5, "entry_ts": datetime(2023, 10, 16, 9, 0), "exit_ts": datetime(2023, 10, 16, 10, 0), "playbooks": [playbook_a]},
        {"gross_p_l": 150, "fees": 5, "commissions": 2.5, "entry_ts": datetime(2023, 10, 16, 11, 0), "exit_ts": datetime(2023, 10, 16, 12, 30), "playbooks": [playbook_b]},
        # Giorno 2 (Martedì): Loss -> Net Loss
        {"gross_p_l": -50, "fees": 5, "commissions": 2.5, "entry_ts": datetime(2023, 10, 17, 9, 0), "exit_ts": datetime(2023, 10, 17, 9, 45), "playbooks": [playbook_a]},
        # Giorno 3 (Mercoledì): Win, Loss, Loss -> Net Win, Loss, Loss
        {"gross_p_l": 200, "fees": 5, "commissions": 2.5, "entry_ts": datetime(2023, 10, 18, 10, 0), "exit_ts": datetime(2023, 10, 18, 15, 0), "playbooks": [playbook_a]},
        {"gross_p_l": -70, "fees": 5, "commissions": 2.5, "entry_ts": datetime(2023, 10, 18, 15, 0), "exit_ts": datetime(2023, 10, 18, 16, 0), "playbooks": [playbook_b]},
        {"gross_p_l": -80, "fees": 5, "commissions": 2.5, "entry_ts": datetime(2023, 10, 18, 16, 0), "exit_ts": datetime(2023, 10, 18, 17, 0), "playbooks": [playbook_b]},
        # Giorno 4 (Giovedì): Breakeven -> Net Loss
        {"gross_p_l": 0, "fees": 5, "commissions": 2.5, "entry_ts": datetime(2023, 10, 19, 9, 0), "exit_ts": datetime(2023, 10, 19, 10, 0), "playbooks": []},
        # Giorno 5 (Venerdì, mese diverso): Win -> Net Win
        {"gross_p_l": 300, "fees": 5, "commissions": 2.5, "entry_ts": datetime(2023, 11, 3, 10, 0), "exit_ts": datetime(2023, 11, 3, 14, 0), "playbooks": [playbook_a]},
    ]

    for data in trades_data:
        net_pnl = data["gross_p_l"] - data["fees"] - data["commissions"]
        trade = Trade(
            id=uuid4(),
            trading_account_id=trading_account.id,
            p_l=net_pnl, # For compatibility, but calculator should not use it
            gross_p_l=data["gross_p_l"],
            fees=data["fees"],
            commissions=data["commissions"],
            entry_timestamp=data["entry_ts"],
            exit_timestamp=data["exit_ts"],
            playbooks=data["playbooks"]
        )
        db_session.add(trade)

    await db_session.commit()

    # Return the ID of the trading account for querying
    return trading_account.id


async def test_get_performance_metrics_integration(db_session: AsyncSession, setup_test_data: uuid4):
    """
    Testa che le metriche di performance avanzate siano calcolate correttamente
    usando il nuovo MetricsCalculator che considera i costi.
    """
    # Arrange
    trading_account_id = setup_test_data
    service = AnalyticsService(db=db_session)

    # Act
    result = await service.get_performance_metrics(
        trading_account_id=trading_account_id,
        start_date=date(2023, 1, 1),
        end_date=date(2023, 12, 31)
    )
    stats = result.stats

    # Assert - Valori attesi ricalcolati sulla base del P&L Netto
    assert stats.trade_count == 8
    assert stats.net_pnl == pytest.approx(490.0)
    assert stats.winning_trades == 4
    assert stats.losing_trades == 4
    assert stats.breakeven_trades == 0
    assert stats.win_rate == pytest.approx(50.0)
    assert stats.profit_factor == pytest.approx(720 / 230)
    assert stats.max_consecutive_wins == 2
    assert stats.max_consecutive_losses == 3
    assert stats.expectancy == pytest.approx(61.25)
    assert stats.max_drawdown_abs == pytest.approx(172.5)

    # Il calcolo dello Sharpe ratio nel calculator è basato sui ritorni giornalieri, non per trade.
    # Per questo test di integrazione, verifichiamo che il valore sia un float,
    # lasciando il test di unità del calcolatore a validare la formula esatta.
    assert isinstance(stats.sharpe_ratio, float)

async def test_get_processed_stats_integration(db_session: AsyncSession, setup_test_data: uuid4):
    """
    Testa che le statistiche aggregate (per strategia, giorno, etc.) siano corrette
    usando il nuovo MetricsCalculator.
    """
    # Arrange
    trading_account_id = setup_test_data
    service = AnalyticsService(db=db_session)

    # Act
    result = await service.get_processed_stats(
        trading_account_id=trading_account_id,
        start_date=date(2023, 1, 1),
        end_date=date(2023, 12, 31)
    )

    # --- Assert By Strategy (Net P&L) ---
    by_strategy = result.by_strategy
    assert "Breakout Strategy" in by_strategy
    assert "Mean Reversion" in by_strategy
    assert by_strategy["Breakout Strategy"].total_pnl == pytest.approx(520.0)
    assert by_strategy["Breakout Strategy"].win_rate == pytest.approx(75.0)
    assert by_strategy["Mean Reversion"].total_pnl == pytest.approx(-22.5)
    assert by_strategy["Mean Reversion"].win_rate == pytest.approx(100 / 3)

    # --- Assert By Day of Week (Net P&L) ---
    by_day = result.by_day_of_week
    assert by_day["Lunedì"].total_pnl == pytest.approx(235)
    assert by_day["Martedì"].total_pnl == pytest.approx(-57.5)
    assert by_day["Mercoledì"].total_pnl == pytest.approx(27.5)
    assert by_day["Giovedì"].total_pnl == pytest.approx(-7.5)
    assert by_day["Venerdì"].total_pnl == pytest.approx(292.5)

    # --- Assert Win/Loss Days (basato su P&L giornaliero netto) ---
    win_loss_days = result.win_loss_days
    assert win_loss_days.winningDays == 3
    assert win_loss_days.losingDays == 2
    assert win_loss_days.breakEvenDays == 0

    # --- Assert Monthly Totals (Net P&L) ---
    monthly = result.monthly_totals
    assert monthly["2023-10"] == pytest.approx(197.5)
    assert monthly["2023-11"] == pytest.approx(292.5)