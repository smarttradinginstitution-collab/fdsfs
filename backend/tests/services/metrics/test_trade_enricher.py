# backend/tests/services/metrics/test_trade_enricher.py
import pytest
from decimal import Decimal
from app.Services.metrics.trade_enricher import calculate_advanced_trade_metrics

# Fixture per i dati di un trade LONG in profitto
@pytest.fixture
def long_trade_data():
    return {
        "p_l": "300.00",
        "entry_price": "150.0",
        "exit_price": "165.0",
        "stop_loss_price": "145.0",
        "direction": "LONG",
    }

# Fixture per i dati di un trade SHORT in perdita
@pytest.fixture
def short_trade_data():
    return {
        "p_l": "-50.00",
        "entry_price": "200.0",
        "exit_price": "202.5",
        "stop_loss_price": "205.0",
        "direction": "SHORT",
    }

# Fixture per i dati del trade specifico segnalato dall'utente
@pytest.fixture
def user_reported_trade_data():
    return {
        "p_l": "1575.00",
        "entry_price": "24841.50",
        "exit_price": "24832.75",
        "stop_loss_price": "24846.00",
        "direction": "SHORT",
    }

# Test con il caso specifico segnalato dall'utente
def test_calculation_with_user_reported_data(user_reported_trade_data):
    """
    Verifica che la logica di calcolo corretta venga applicata al caso
    specifico segnalato dall'utente, producendo i risultati attesi.
    """
    initial_balance = Decimal("25000.00") # Saldo ipotetico per il calcolo ROI
    metrics = calculate_advanced_trade_metrics(user_reported_trade_data, initial_balance)

    # Valori attesi calcolati manualmente con la formula corretta:
    # valore_per_punto = abs(1575 / (24832.75 - 24841.50)) = 180
    # distanza_sl = abs(24841.50 - 24846.00) = 4.5
    # trade_risk = 180 * 4.5 = 810
    # realized_rr = 1575 / 810 = 1.9444...
    # net_roi = (1575 / 25000) * 100 = 6.3

    assert metrics["trade_risk"] == pytest.approx(Decimal("810.00"))
    assert metrics["realized_r_multiple"] == pytest.approx(Decimal("1.9444"), abs=1e-4)
    assert metrics["net_roi"] == pytest.approx(Decimal("6.3"))

# Test per un trade LONG in profitto
def test_long_trade_metrics(long_trade_data):
    initial_balance = Decimal("10000.00")
    metrics = calculate_advanced_trade_metrics(long_trade_data, initial_balance)

    assert metrics["trade_risk"] == pytest.approx(Decimal("100.00"))
    assert metrics["realized_r_multiple"] == pytest.approx(Decimal("3.0"))
    assert metrics["net_roi"] == pytest.approx(Decimal("3.0"))

# Test per un trade SHORT in perdita
def test_short_trade_metrics(short_trade_data):
    initial_balance = Decimal("10300.00")
    metrics = calculate_advanced_trade_metrics(short_trade_data, initial_balance)

    assert metrics["trade_risk"] == pytest.approx(Decimal("100.00"))
    assert metrics["realized_r_multiple"] == pytest.approx(Decimal("-0.5"))
    assert metrics["net_roi"] == pytest.approx(Decimal("-0.4854"), abs=1e-4)

# Test caso limite: nessun rischio (prezzo entrata = stop loss)
def test_zero_risk_scenario():
    trade_data = {
        "p_l": "100.00",
        "entry_price": "100.0",
        "exit_price": "101.0",
        "stop_loss_price": "100.0", # Rischio zero
        "direction": "LONG",
    }
    metrics = calculate_advanced_trade_metrics(trade_data, Decimal("10000"))

    assert metrics["trade_risk"] == Decimal("0.0")
    assert metrics["realized_r_multiple"] is None # R-multiple non è definito
    assert metrics["net_roi"] == pytest.approx(Decimal("1.0"))

# Test caso limite: nessun movimento di prezzo (uscita = entrata)
def test_zero_price_movement_scenario():
    trade_data = {
        "p_l": "-5.00", # PNL dovuto a commissioni
        "entry_price": "100.0",
        "exit_price": "100.0", # Nessun movimento
        "stop_loss_price": "99.0",
        "direction": "LONG",
    }
    metrics = calculate_advanced_trade_metrics(trade_data, Decimal("10000"))

    assert metrics["trade_risk"] == Decimal("0.0") # Rischio non calcolabile dal PNL
    assert metrics["realized_r_multiple"] is None
    assert metrics["net_roi"] == pytest.approx(Decimal("-0.05"))

# Test caso limite: saldo iniziale pari a zero
def test_zero_initial_balance():
    trade_data = {
        "p_l": "50.00",
        "entry_price": "100.0",
        "exit_price": "101.0",
        "stop_loss_price": "99.0",
        "direction": "LONG",
    }
    metrics = calculate_advanced_trade_metrics(trade_data, Decimal("0"))

    assert metrics["trade_risk"] is not None
    assert metrics["realized_r_multiple"] is not None
    assert metrics["net_roi"] == Decimal("0.0")

# Test con dati mancanti o invalidi
def test_invalid_data():
    trade_data = {"p_l": "50"} # Dati insufficienti
    metrics = calculate_advanced_trade_metrics(trade_data, Decimal("10000"))

    assert metrics["trade_risk"] == Decimal("0.0") # Valore di default
    assert metrics["realized_r_multiple"] is None
    assert metrics["net_roi"] is not None