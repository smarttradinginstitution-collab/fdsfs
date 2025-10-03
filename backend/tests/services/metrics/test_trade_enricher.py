# backend/tests/services/metrics/test_trade_enricher.py
import pytest
from decimal import Decimal
from app.Services.metrics.trade_enricher import enrich_trade_with_all_metrics

# Fixture per i dati di un trade LONG in profitto, ora con dati MAE/MFE
@pytest.fixture
def long_trade_data():
    return {
        "p_l": "300.00",
        "entry_price": "150.0",
        "exit_price": "165.0",
        "stop_loss_price": "145.0",
        "direction": "LONG",
        "lowest_price_during_trade": "149.50",
        "highest_price_during_trade": "152.00",
        "position_size": "1", # Aggiunto per un calcolo del valore per punto più realistico
    }

# Fixture per i dati di un trade SHORT in perdita, ora con dati MAE/MFE
@pytest.fixture
def short_trade_data():
    return {
        "p_l": "-50.00",
        "entry_price": "200.0",
        "exit_price": "202.5",
        "stop_loss_price": "205.0",
        "direction": "SHORT",
        "lowest_price_during_trade": "198.0",
        "highest_price_during_trade": "203.0",
        "position_size": "1",
    }

# Test per un trade LONG, ora include verifica MAE/MFE
def test_long_trade_metrics(long_trade_data):
    initial_balance = Decimal("10000.00")
    metrics = enrich_trade_with_all_metrics(long_trade_data, initial_balance)

    # Valori attesi calcolati manualmente
    # valore_per_punto = abs(300 / (165 - 150)) = 20
    # mae_points = 150 - 149.5 = 0.5 -> mae_usd = -abs(0.5 * 20) = -10
    # mfe_points = 152 - 150 = 2 -> mfe_usd = 2 * 20 = 40
    assert metrics["trade_risk"] == pytest.approx(Decimal("100.0")) # 5 punti * 20
    assert metrics["realized_r_multiple"] == pytest.approx(Decimal("3.0"))
    assert metrics["net_roi"] == pytest.approx(Decimal("3.0"))
    assert metrics["mae_usd"] == pytest.approx(Decimal("-10.0"))
    assert metrics["mfe_usd"] == pytest.approx(Decimal("40.0"))

# Test per un trade SHORT, ora include verifica MAE/MFE
def test_short_trade_metrics(short_trade_data):
    initial_balance = Decimal("10300.00")
    metrics = enrich_trade_with_all_metrics(short_trade_data, initial_balance)

    # Valori attesi calcolati manualmente
    # valore_per_punto = abs(-50 / (202.5 - 200)) = 20
    # mae_points = 203 - 200 = 3 -> mae_usd = -abs(3 * 20) = -60
    # mfe_points = 200 - 198 = 2 -> mfe_usd = 2 * 20 = 40
    assert metrics["trade_risk"] == pytest.approx(Decimal("100.0")) # 5 punti * 20
    assert metrics["realized_r_multiple"] == pytest.approx(Decimal("-0.5"))
    assert metrics["net_roi"] == pytest.approx(Decimal("-0.4854"), abs=1e-4)
    assert metrics["mae_usd"] == pytest.approx(Decimal("-60.0"))
    assert metrics["mfe_usd"] == pytest.approx(Decimal("40.0"))

# Test caso limite: nessun dato per MAE/MFE
def test_no_mae_mfe_data():
    trade_data = {
        "p_l": "100.00",
        "entry_price": "100.0",
        "exit_price": "101.0",
        "stop_loss_price": "99.0",
        "direction": "LONG",
        "lowest_price_during_trade": None, # Dati mancanti
        "highest_price_during_trade": None,
    }
    metrics = enrich_trade_with_all_metrics(trade_data, Decimal("10000"))

    assert metrics["mae_usd"] is None # Il valore di default corretto è None
    assert metrics["mfe_usd"] is None

# Test con dati invalidi per prevenire crash
def test_invalid_data():
    trade_data = {"p_l": "50"} # Dati insufficienti
    metrics = enrich_trade_with_all_metrics(trade_data, Decimal("10000"))

    assert "trade_risk" in metrics
    assert "realized_r_multiple" in metrics
    assert "net_roi" in metrics
    assert "mae_usd" in metrics
    assert "mfe_usd" in metrics
    assert metrics["mae_usd"] is None # La gestione errori dovrebbe restituire None
    assert metrics["mfe_usd"] is None