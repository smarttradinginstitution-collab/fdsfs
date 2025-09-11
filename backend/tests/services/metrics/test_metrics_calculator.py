# backend/tests/services/metrics/test_metrics_calculator.py

import pytest
from datetime import datetime
from decimal import Decimal
from app.Services.metrics.metrics_calculator import MetricsCalculator

def _get_mock_trade(entry_timestamp: str, pnl: str = "100.00") -> dict:
    """Helper to create a consistent mock trade dictionary."""
    return {
        "p_l": Decimal(pnl),
        "entry_timestamp": entry_timestamp,
        "exit_timestamp": entry_timestamp, # Keep it simple
        "created_at": entry_timestamp,
        "entry_price": Decimal("150.00"),
        "position_size": Decimal("1.0"),
        "id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
        "user_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
        "setup": "Test Setup",
        "stop_loss_price": Decimal("149.00"),
        "take_profit_price": Decimal("151.00"),
        "notes": "",
        "exit_price": Decimal("151.00"),
        "lowest_price_during_trade": Decimal("149.50"),
        "highest_price_during_trade": Decimal("151.50"),
        "symbol": "TEST",
        "direction": "Long",
        "emotional_state": "Calm",
        "mistakes": [],
        "notes_pre_trade": "",
        "notes_post_trade": "",
        "duration_minutes": 0,
        "tags": []
    }

def test_timezone_conversion_groups_by_local_date_and_hour():
    """
    Verifica che un trade notturno in UTC venga assegnato al giorno e all'ora corretti
    in un fuso orario locale.
    """
    # 23:30 UTC del 26 Ottobre 2023 -> 01:30 del 27 Ottobre in 'Europe/Rome' (CEST, UTC+2)
    utc_time = "2023-10-26T23:30:00Z"
    local_date = "2023-10-27"
    local_hour_key = "01:00" # L'ora corretta è l'una del mattino, non mezzanotte

    mock_trades = [_get_mock_trade(utc_time)]
    calculator = MetricsCalculator(trades=mock_trades, user_timezone="Europe/Rome")

    # Calcoliamo le statistiche per la verifica
    processed_stats = calculator.calculate_processed_stats()
    base_stats = calculator._calculate_base_stats()
    advanced_stats = calculator._calculate_advanced_stats(base_stats)

    # Verifica raggruppamento giornaliero
    assert local_date in processed_stats["daily_data"]
    assert "2023-10-26" not in processed_stats["daily_data"]
    assert processed_stats["daily_data"][local_date]["total_pnl"] == 100.00

    # Verifica raggruppamento orario
    assert advanced_stats["performance_by_hour"][local_hour_key] == Decimal("100.00")
    assert advanced_stats["performance_by_hour"]["00:00"] == Decimal("0")
    assert advanced_stats["performance_by_hour"]["23:00"] == Decimal("0")

    # Verifica giorno della settimana (27/10/2023 era un Venerdì)
    assert advanced_stats["performance_by_day_of_week"]["Venerdì"] == Decimal("100.00")
    assert advanced_stats["performance_by_day_of_week"]["Giovedì"] == Decimal("0")


def test_daylight_saving_time_spring_forward():
    """
    Verifica la corretta gestione del passaggio all'ora legale (spring forward).
    A New York, il 12 Marzo 2023, l'orologio salta dalle 01:59 alle 03:00.
    """
    # Trade 1: 01:30 EST (UTC-5) -> 06:30 UTC
    # Trade 2: 03:30 EDT (UTC-4) -> 07:30 UTC
    trade_before_dst = _get_mock_trade("2023-03-12T06:30:00Z", "50.00") # 01:30 local
    trade_after_dst = _get_mock_trade("2023-03-12T07:30:00Z", "150.00") # 03:30 local

    mock_trades = [trade_before_dst, trade_after_dst]
    calculator = MetricsCalculator(trades=mock_trades, user_timezone="America/New_York")

    base_stats = calculator._calculate_base_stats()
    advanced_stats = calculator._calculate_advanced_stats(base_stats)

    # Verifica che i P&L siano stati assegnati ai bucket orari corretti
    pnl_by_hour = advanced_stats["performance_by_hour"]
    assert pnl_by_hour["01:00"] == Decimal("50.00")
    assert pnl_by_hour["02:00"] == Decimal("0") # L'ora dalle 2 alle 3 non esiste in questo giorno
    assert pnl_by_hour["03:00"] == Decimal("150.00")

def test_daylight_saving_time_fall_back():
    """
    Verifica la corretta gestione del ritorno all'ora solare (fall back).
    A Roma, il 29 Ottobre 2023, l'orologio torna indietro dalle 02:59 alle 02:00.
    L'ora tra le 02:00 e le 02:59 accade due volte.
    """
    # Trade 1: 02:30 CEST (UTC+2) -> 00:30 UTC
    # Trade 2: 02:30 CET (UTC+1) -> 01:30 UTC
    trade_first_2am_hour = _get_mock_trade("2023-10-29T00:30:00Z", "70.00") # Questo è alle 2:30 CEST
    trade_second_2am_hour = _get_mock_trade("2023-10-29T01:30:00Z", "80.00") # Questo è alle 2:30 CET

    mock_trades = [trade_first_2am_hour, trade_second_2am_hour]
    calculator = MetricsCalculator(trades=mock_trades, user_timezone="Europe/Rome")

    base_stats = calculator._calculate_base_stats()
    advanced_stats = calculator._calculate_advanced_stats(base_stats)

    # Entrambi i trade dovrebbero finire nel bucket delle 02:00
    pnl_by_hour = advanced_stats["performance_by_hour"]
    assert pnl_by_hour["02:00"] == Decimal("70.00") + Decimal("80.00")
    assert pnl_by_hour["02:00"] == Decimal("150.00")
