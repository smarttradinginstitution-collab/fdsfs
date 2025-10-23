# app/Services/metrics/trade_enricher.py
from decimal import Decimal, InvalidOperation
from typing import Dict, Any, Optional

def _to_decimal_or_none(value: Any) -> Optional[Decimal]:
    """Converte un valore in Decimal, restituendo None se il valore è nullo, vuoto o non valido."""
    if value is None or value == '':
        return None
    try:
        return Decimal(value)
    except (InvalidOperation, TypeError):
        return None

def enrich_trade_with_all_metrics(trade_data: Dict[str, Any], initial_balance: Decimal) -> Dict[str, Any]:
    """
    Calcola tutte le metriche avanzate per un singolo trade, inclusi i Vettori SOA.
    """
    # --- Inizializzazione di tutte le metriche a None ---
    metrics = {
        "trade_risk": None, "realized_r_multiple": None, "net_roi": None,
        "mae_usd": None, "mfe_usd": None, "planned_target": None, "planned_r_multiple": None,
        # Vettori SOA
        "SN": None, "EP": None, "RRv": None, "ES": None, "RER": None
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
    elif position_size and position_size > 0:
        value_per_point = position_size

    # --- 3. Calcolo di tutte le altre metriche (se possibile) ---
    if value_per_point:
        # Planned Target (Opzione B)
        if tp and entry:
            metrics["planned_target"] = abs(tp - entry) * value_per_point

        # Trade Risk
        if sl and entry:
            metrics["trade_risk"] = abs(entry - sl) * value_per_point

        # Realized R-Multiple
        if metrics["trade_risk"] and metrics["trade_risk"] > 0 and pnl is not None:
            metrics["realized_r_multiple"] = pnl / metrics["trade_risk"]

        # MAE/MFE Monetario
        if entry and lowest and highest and direction:
            if direction.upper() == 'LONG':
                mae_points = entry - lowest
                mfe_points = highest - entry
            else: # SHORT
                mae_points = highest - entry
                mfe_points = entry - lowest
            metrics["mae_usd"] = mae_points * value_per_point
            metrics["mfe_usd"] = mfe_points * value_per_point

    # --- 4. Calcolo Net ROI (indipendente dal resto) ---
    if pnl is not None and initial_balance > 0:
        metrics["net_roi"] = (pnl / initial_balance) * 100

    # --- 5. Calcolo dei Vettori SOA ---
    trade_risk = metrics.get("trade_risk")
    mae_usd = metrics.get("mae_usd")
    mfe_usd = metrics.get("mfe_usd")
    realized_r = metrics.get("realized_r_multiple")
    planned_r = metrics.get("planned_r_multiple")

    # SN: stress_normalizzato
    if mae_usd is not None and trade_risk and trade_risk > 0:
        metrics["SN"] = mae_usd / trade_risk

    # EP: efficienza_profitto (solo per trade in profitto)
    if pnl is not None and pnl > 0:
        if mfe_usd is not None and mfe_usd > 0:
            metrics["EP"] = pnl / mfe_usd
        else:
            metrics["EP"] = Decimal(0) # Profitto senza MFE positivo, efficienza 0
    elif pnl is not None and pnl <= 0:
        metrics["EP"] = Decimal(0)

    # RRv: rapporto_reversal & ES: efficienza_stop (solo per trade in perdita)
    if pnl is not None and pnl < 0:
        if trade_risk and trade_risk > 0:
            if mfe_usd is not None:
                metrics["RRv"] = mfe_usd / trade_risk
            if mae_usd is not None:
                metrics["ES"] = mae_usd / trade_risk
        else: # Perdita senza rischio definito, vettori a 0
            metrics["RRv"] = Decimal(0)
            metrics["ES"] = Decimal(0)
    elif pnl is not None and pnl >= 0:
        metrics["RRv"] = Decimal(0)
        metrics["ES"] = Decimal(0)


    # RER: rapporto_esecuzione_rr
    if realized_r is not None and planned_r and planned_r > 0:
        metrics["RER"] = realized_r / planned_r
    elif realized_r is not None and (planned_r is None or planned_r <= 0):
        metrics["RER"] = None # Non calcolabile se il piano non era valido

    return metrics