# backend/tests/services/metrics/test_trade_enricher.py
import pytest
from decimal import Decimal
from app.Services.metrics.trade_enricher import enrich_trade_with_all_metrics

@pytest.fixture
def long_trade_data():
    """Dati per un trade LONG basato sull'esempio dell'utente, con TP."""
    return {
        "entry_price": "100.0",
        "exit_price": "110.0",
        "lowest_price_during_trade": "98.0",
        "highest_price_during_trade": "115.0",
        "p_l": "200.0",
        "direction": "LONG",
        "stop_loss_price": "95.0",
        "take_profit_price": "120.0", # Aggiunto per testare le metriche pianificate
    }

@pytest.fixture
def short_trade_data():
    """Dati per un trade SHORT basato sull'esempio dell'utente, con TP."""
    return {
        "entry_price": "500.0",
        "exit_price": "480.0",
        "lowest_price_during_trade": "475.0",
        "highest_price_during_trade": "505.0",
        "p_l": "400.0",
        "direction": "SHORT",
        "stop_loss_price": "510.0",
        "take_profit_price": "470.0", # Aggiunto per testare le metriche pianificate
    }

def test_planned_metrics_calculation(long_trade_data, short_trade_data):
    """Verifica il calcolo di Planned Target e Planned R-Multiple."""
    # Test per il trade LONG
    metrics_long = enrich_trade_with_all_metrics(long_trade_data, initial_balance=Decimal("10000"))

    # Valori attesi per LONG:
    # valore_per_punto = abs(200 / (110 - 100)) = 20
    # planned_target = abs(120 - 100) * 20 = 400
    # planned_r = abs(120 - 100) / abs(100 - 95) = 20 / 5 = 4
    assert metrics_long["planned_target"] == pytest.approx(Decimal("400.0"))
    assert metrics_long["planned_r_multiple"] == pytest.approx(Decimal("4.0"))

    # Test per il trade SHORT
    metrics_short = enrich_trade_with_all_metrics(short_trade_data, initial_balance=Decimal("20000"))

    # Valori attesi per SHORT:
    # valore_per_punto = abs(400 / (480 - 500)) = 20
    # planned_target = abs(470 - 500) * 20 = 600
    # planned_r = abs(470 - 500) / abs(500 - 510) = 30 / 10 = 3
    assert metrics_short["planned_target"] == pytest.approx(Decimal("600.0"))
    assert metrics_short["planned_r_multiple"] == pytest.approx(Decimal("3.0"))

def test_mae_mfe_monetary_long_trade(long_trade_data):
    """Verifica il calcolo monetario di MAE/MFE per un trade LONG."""
    metrics = enrich_trade_with_all_metrics(long_trade_data, initial_balance=Decimal("10000"))
    assert metrics["mae_usd"] == pytest.approx(Decimal("40.0"))
    assert metrics["mfe_usd"] == pytest.approx(Decimal("300.0"))

def test_mae_mfe_monetary_short_trade(short_trade_data):
    """Verifica il calcolo monetario di MAE/MFE per un trade SHORT."""
    metrics = enrich_trade_with_all_metrics(short_trade_data, initial_balance=Decimal("20000"))
    assert metrics["mae_usd"] == pytest.approx(Decimal("100.0"))
    assert metrics["mfe_usd"] == pytest.approx(Decimal("500.0"))

def test_missing_take_profit_returns_none_for_planned_metrics(long_trade_data):
    """Se manca il take_profit, le metriche pianificate devono essere None."""
    del long_trade_data["take_profit_price"]
    metrics = enrich_trade_with_all_metrics(long_trade_data, initial_balance=Decimal("10000"))

    assert metrics["planned_target"] is None
    assert metrics["planned_r_multiple"] is None

def test_no_price_movement_returns_none_for_monetary_metrics():
    """Se non c'è movimento di prezzo, le metriche monetarie non sono calcolabili."""
    trade_data = { "entry_price": "100.0", "exit_price": "100.0", "p_l": "0.0" }
    metrics = enrich_trade_with_all_metrics(trade_data, initial_balance=Decimal("10000"))

    assert metrics["mae_usd"] is None
    assert metrics["mfe_usd"] is None
    assert metrics["trade_risk"] is None
    assert metrics["realized_r_multiple"] is None
    assert metrics["planned_target"] is None
    # planned_r_multiple potrebbe essere calcolabile se SL e TP sono presenti
    assert metrics["net_roi"] is not None

def test_planned_target_fallback_with_zero_pnl(long_trade_data):
    """Verifica che Planned Target usi position_size come fallback quando PNL è zero."""
    long_trade_data["p_l"] = "0.0"
    long_trade_data["exit_price"] = long_trade_data["entry_price"] # Simula trade aperto
    long_trade_data["position_size"] = "10" # Unità per il calcolo

    metrics = enrich_trade_with_all_metrics(long_trade_data, initial_balance=Decimal("10000"))

    # Valore atteso:
    # valore_per_punto fallback a position_size = 10
    # planned_target = abs(120 - 100) * 10 = 200
    assert metrics["planned_target"] == pytest.approx(Decimal("200.0"))