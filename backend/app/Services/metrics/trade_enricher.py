# app/Services/metrics/trade_enricher.py
from decimal import Decimal, InvalidOperation

def calculate_advanced_trade_metrics(trade_data: dict, initial_balance: Decimal) -> dict:
    """
    Calcola metriche avanzate per un singolo trade (Trade Risk, Realized RR, Net ROI)
    utilizzando la logica di calcolo fornita.

    Args:
        trade_data (dict): Un dizionario contenente i dati del trade.
                           Campi richiesti: 'entry_price', 'exit_price', 'stop_loss_price',
                           'p_l', 'direction'.
        initial_balance (Decimal): Il saldo iniziale del conto di trading per il calcolo del ROI.

    Returns:
        dict: Un dizionario contenente le metriche calcolate.
    """
    try:
        entry = Decimal(trade_data.get('entry_price') or 0)
        exit_p = Decimal(trade_data.get('exit_price') or 0)
        sl = Decimal(trade_data.get('stop_loss_price') or 0)
        pnl = Decimal(trade_data.get('p_l') or 0)
    except (InvalidOperation, TypeError) as e:
        # Se i dati non sono validi, restituisce metriche nulle
        return {
            "trade_risk": None,
            "realized_r_multiple": None,
            "net_roi": None
        }

    # --- Controlli di sicurezza per evitare divisioni per zero o logica errata ---
    if entry == exit_p or entry == sl or pnl is None:
        return {
            "trade_risk": Decimal('0.0'),
            "realized_r_multiple": None, # Non calcolabile se il rischio è zero
            "net_roi": (pnl / initial_balance) * 100 if initial_balance != 0 else Decimal('0.0')
        }

    # --- 1. Calcolo del Rischio Monetario (Trade Risk) ---
    # Calcoliamo il "valore monetario" di un singolo punto di movimento del prezzo
    # Usiamo il PNL diviso per la distanza in punti tra entrata e uscita
    price_movement = exit_p - entry
    if price_movement == 0:
        # Se non c'è movimento di prezzo, il rischio non può essere derivato dal PNL.
        # Potrebbe essere un trade a commissione zero, ma per sicurezza lo impostiamo a 0.
        trade_risk = Decimal('0.0')
    else:
        value_per_point = abs(pnl / price_movement)

        # Distanza in punti dello stop loss dall'entrata
        sl_distance_points = abs(entry - sl)

        # Rischio monetario totale per il trade
        trade_risk = sl_distance_points * value_per_point


    # --- 2. Calcolo del Realized R-Multiple ---
    if trade_risk != 0:
        realized_r_multiple = pnl / trade_risk
    else:
        # Se il rischio è zero, l'R-multiple non è definito.
        # Potrebbe essere infinito se c'è un PNL, ma None è più sicuro.
        realized_r_multiple = None

    # --- 3. Calcolo del Net ROI (Return on Investment) ---
    if initial_balance != 0:
        net_roi = (pnl / initial_balance) * 100
    else:
        net_roi = Decimal('0.0')


    # --- Creazione del dizionario con i risultati ---
    metriche = {
        "trade_risk": trade_risk,
        "realized_r_multiple": realized_r_multiple,
        "net_roi": net_roi
    }

    return metriche