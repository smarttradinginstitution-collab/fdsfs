# app/Services/metrics/trade_enricher.py
from decimal import Decimal, InvalidOperation
from typing import Dict, Any

def enrich_trade_with_all_metrics(trade_data: Dict[str, Any], initial_balance: Decimal) -> Dict[str, Any]:
    """
    Calcola tutte le metriche avanzate per un singolo trade, inclusi Rischio, ROI, R-Multiple, e MAE/MFE monetario.
    Restituisce un dizionario contenente solo le metriche calcolate.
    """
    try:
        entry = Decimal(trade_data.get('entry_price') or 0)
        exit_p = Decimal(trade_data.get('exit_price') or 0)
        sl = Decimal(trade_data.get('stop_loss_price') or 0)
        pnl = Decimal(trade_data.get('p_l') or 0)
        lowest = Decimal(trade_data.get('lowest_price_during_trade') or 0)
        highest = Decimal(trade_data.get('highest_price_during_trade') or 0)
        direction = trade_data.get('direction')
    except (InvalidOperation, TypeError):
        return {
            "trade_risk": None, "realized_r_multiple": None, "net_roi": None,
            "mae_usd": None, "mfe_usd": None
        }

    # --- Calcolo Valore per Punto ---
    price_movement = exit_p - entry
    value_per_point = Decimal(0)
    if price_movement != 0 and pnl != 0:
        value_per_point = abs(pnl / price_movement)
    else:
        # Se non possiamo calcolare il valore per punto, non possiamo calcolare le metriche monetarie.
        return {
            "trade_risk": None, "realized_r_multiple": None,
            "net_roi": (pnl / initial_balance) * 100 if initial_balance > 0 else Decimal(0),
            "mae_usd": None, "mfe_usd": None
        }

    # --- Calcolo Rischio, ROI, R-Multiple ---
    trade_risk = None
    realized_r_multiple = None

    sl_distance_points = abs(entry - sl)
    if sl_distance_points > 0:
        trade_risk = sl_distance_points * value_per_point
        if trade_risk > 0:
            realized_r_multiple = pnl / trade_risk

    net_roi = (pnl / initial_balance) * 100 if initial_balance > 0 else Decimal(0)

    # --- Calcolo MAE/MFE Monetario ---
    mae_usd = None
    mfe_usd = None
    if entry > 0 and lowest > 0 and highest > 0 and direction:
        if direction.upper() == 'LONG':
            mae_points = entry - lowest
            mfe_points = highest - entry
            mae_usd = mae_points * value_per_point
            mfe_usd = mfe_points * value_per_point
        elif direction.upper() == 'SHORT':
            mae_points = highest - entry
            mfe_points = entry - lowest
            mae_usd = mae_points * value_per_point
            mfe_usd = mfe_points * value_per_point

    return {
        "trade_risk": trade_risk,
        "realized_r_multiple": realized_r_multiple,
        "net_roi": net_roi,
        "mae_usd": mae_usd,
        "mfe_usd": mfe_usd,
    }