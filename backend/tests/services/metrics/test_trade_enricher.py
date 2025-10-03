# backend/tests/services/metrics/test_trade_enricher.py
import pytest
from decimal import Decimal
from app.Services.metrics.trade_enricher import enrich_trade_with_all_metrics

@pytest.fixture
def long_trade_data():
    """Dati per un trade LONG basato sull'esempio dell'utente."""
    return {
        "entry_price": "100.0",
        "exit_price": "110.0",
        "lowest_price_during_trade": "98.0",
        "highest_price_during_trade": "115.0",
        "p_l": "200.0",
        "direction": "LONG",
        "stop_loss_price": "95.0", # Aggiunto per calcoli di rischio
    }

@pytest.fixture
def short_trade_data():
    """Dati per un trade SHORT basato sull'esempio dell'utente."""
    return {
        "entry_price": "500.0",
        "exit_price": "480.0",
        "lowest_price_during_trade": "475.0",
        "highest_price_during_trade": "505.0",
        "p_l": "400.0",
        "direction": "SHORT",
        "stop_loss_price": "510.0", # Aggiunto per calcoli di rischio
    }

def test_mae_mfe_monetary_long_trade(long_trade_data):
    """Verifica il calcolo monetario di MAE/MFE per un trade LONG."""
    metrics = enrich_trade_with_all_metrics(long_trade_data, initial_balance=Decimal("10000"))

    # Valori attesi dall'esempio dell'utente:
    # valore_per_punto = abs(200 / (110 - 100)) = 20
    # mae = (100 - 98) * 20 = 40
    # mfe = (115 - 100) * 20 = 300
    assert metrics["mae_usd"] == pytest.approx(Decimal("40.0"))
    assert metrics["mfe_usd"] == pytest.approx(Decimal("300.0"))

def test_mae_mfe_monetary_short_trade(short_trade_data):
    """Verifica il calcolo monetario di MAE/MFE per un trade SHORT."""
    metrics = enrich_trade_with_all_metrics(short_trade_data, initial_balance=Decimal("20000"))

    # Valori attesi dall'esempio dell'utente:
    # valore_per_punto = abs(400 / (480 - 500)) = 20
    # mae = (505 - 500) * 20 = 100
    # mfe = (500 - 475) * 20 = 500
    assert metrics["mae_usd"] == pytest.approx(Decimal("100.0"))
    assert metrics["mfe_usd"] == pytest.approx(Decimal("500.0"))

def test_other_metrics_remain_correct(long_trade_data):
    """Verifica che le altre metriche (rischio, ROI) siano ancora calcolate correttamente."""
    metrics = enrich_trade_with_all_metrics(long_trade_data, initial_balance=Decimal("10000"))

    # valore_per_punto = 20
    # trade_risk = abs(100 - 95) * 20 = 100
    # realized_r_multiple = 200 / 100 = 2
    # net_roi = (200 / 10000) * 100 = 2
    assert metrics["trade_risk"] == pytest.approx(Decimal("100.0"))
    assert metrics["realized_r_multiple"] == pytest.approx(Decimal("2.0"))
    assert metrics["net_roi"] == pytest.approx(Decimal("2.0"))

def test_no_price_movement_returns_none_for_monetary_metrics():
    """Se non c'è movimento di prezzo, le metriche monetarie non sono calcolabili."""
    trade_data = {
        "entry_price": "100.0",
        "exit_price": "100.0", # Nessun movimento
        "lowest_price_during_trade": "98.0",
        "highest_price_during_trade": "102.0",
        "p_l": "0.0",
        "direction": "LONG",
        "stop_loss_price": "99.0",
    }
    metrics = enrich_trade_with_all_metrics(trade_data, initial_balance=Decimal("10000"))

    assert metrics["mae_usd"] is None
    assert metrics["mfe_usd"] is None
    assert metrics["trade_risk"] is None
    assert metrics["realized_r_multiple"] is None
    assert metrics["net_roi"] is not None # Il ROI è calcolabile anche con PNL zero

def test_missing_high_low_prices_returns_none():
    """Se mancano i prezzi high/low, MAE/MFE devono essere None."""
    trade_data = {
        "entry_price": "100.0",
        "exit_price": "110.0",
        "p_l": "200.0",
        "direction": "LONG",
        "lowest_price_during_trade": None, # Dati mancanti
        "highest_price_during_trade": None,
    }
    metrics = enrich_trade_with_all_metrics(trade_data, initial_balance=Decimal("10000"))

    assert metrics["mae_usd"] is None
    assert metrics["mfe_usd"] is None