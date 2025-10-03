# app/Services/metrics/trade_enricher.py
from decimal import Decimal, InvalidOperation
from typing import Dict, Any, Optional

def _to_decimal_or_none(value: Any) -> Optional[Decimal]:
    """Converte un valore in Decimal, restituendo None se il valore è nullo, vuoto o non valido."""
    if value is None or value == '':
        return None
    try:
        return Decimal(value)
    except InvalidOperation:
        return None

def enrich_trade_with_all_metrics(trade_data: Dict[str, Any], initial_balance: Decimal) -> Dict[str, Any]:
    """
    Calcola tutte le metriche avanzate per un singolo trade, inclusi Rischio, ROI, R-Multiple,
    MAE/MFE monetario, Planned Target e Planned R-Multiple.
    Restituisce un dizionario contenente solo le metriche calcolate.
    """
    try:
        # Sanitize all numeric inputs to prevent crashes on empty strings
        entry = _sanitize_decimal(trade_data.get('entry_price'))
        exit_p = _sanitize_decimal(trade_data.get('exit_price'))
        sl = _sanitize_decimal(trade_data.get('stop_loss_price'))
        tp = _sanitize_decimal(trade_data.get('take_profit_price'))
        pnl = _sanitize_decimal(trade_data.get('p_l'))
        lowest = _sanitize_decimal(trade_data.get('lowest_price_during_trade'))
        highest = _sanitize_decimal(trade_data.get('highest_price_during_trade'))
        position_size = _sanitize_decimal(trade_data.get('position_size'))
        if position_size == 0:
            position_size = Decimal('1') # Default to 1 if size is 0 or not provided
        
        direction = trade_data.get('direction')

    except (InvalidOperation, TypeError):
        return {
            "trade_risk": None, "realized_r_multiple": None, "net_roi": None,
            "mae_usd": None, "mfe_usd": None, "planned_target": None, "planned_r_multiple": None
        }

    # --- Parsing sicuro dei dati di input ---
    entry = _to_decimal_or_none(trade_data.get('entry_price'))
    exit_p = _to_decimal_or_none(trade_data.get('exit_price'))
    sl = _to_decimal_or_none(trade_data.get('stop_loss_price'))
    tp = _to_decimal_or_none(trade_data.get('take_profit_price'))
    pnl = _to_decimal_or_none(trade_data.get('p_l'))
    lowest = _to_decimal_or_none(trade_data.get('lowest_price_during_trade'))
    highest = _to_decimal_or_none(trade_data.get('highest_price_during_trade'))
    position_size = _to_decimal_or_none(trade_data.get('position_size'))
    direction = trade_data.get('direction')

    # --- 1. Calcolo del Planned R-Multiple (Opzione A: basato solo sui prezzi) ---
    if entry and sl and tp:
        sl_distance_points = abs(entry - sl)
        tp_distance_points = abs(tp - entry)
        if sl_distance_points > 0:
            metrics["planned_r_multiple"] = tp_distance_points / sl_distance_points

    # --- 2. Calcolo del Valore Monetario per Punto (necessario per le altre metriche) ---
    value_per_point = None
    if pnl is not None and exit_p and entry and (exit_p - entry) != 0:
        value_per_point = abs(pnl / (exit_p - entry))
    elif position_size:
        value_per_point = position_size

    can_calculate_monetary = value_per_point > 0

    # --- Calcoli di base ---
    net_roi = (pnl / initial_balance) * 100 if initial_balance > 0 else Decimal(0)
    sl_distance_points = abs(entry - sl) if entry > 0 and sl > 0 else Decimal(0)
    tp_distance_points = abs(tp - entry) if entry > 0 and tp > 0 else Decimal(0)

    # --- Calcolo Metriche Pianificate ---
    planned_target = None
    if can_calculate_monetary and tp_distance_points > 0:
        planned_target = tp_distance_points * value_per_point

    planned_r_multiple = None
    if sl_distance_points > 0 and tp_distance_points > 0:
        planned_r_multiple = tp_distance_points / sl_distance_points

    # --- Calcolo Metriche Realizzate ---
    trade_risk = None
    if can_calculate_monetary and sl_distance_points > 0:
        trade_risk = sl_distance_points * value_per_point

    realized_r_multiple = None
    if trade_risk is not None and trade_risk > 0 and pnl != 0:
        realized_r_multiple = pnl / trade_risk

    # --- Calcolo MAE/MFE Monetario ---
    mae_usd = None
    mfe_usd = None
    if can_calculate_monetary and entry > 0 and lowest > 0 and highest > 0 and direction:
        if direction.upper() == 'LONG':
            mae_points = entry - lowest
            mfe_points = highest - entry
        else:  # SHORT
            mae_points = highest - entry
            mfe_points = entry - lowest

        mae_usd = mae_points * value_per_point
        mfe_usd = mfe_points * value_per_point

    # --- 4. Calcolo Net ROI (indipendente dal resto) ---
    if pnl is not None and initial_balance > 0:
        metrics["net_roi"] = (pnl / initial_balance) * 100

    return metrics