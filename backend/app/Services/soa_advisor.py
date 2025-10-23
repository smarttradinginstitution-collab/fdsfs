# app/Services/soa_advisor.py
from typing import Dict, Any, Optional

def generate_sl_advice(avg_user_stress_ratio: Optional[float], sl_opt_p95: Optional[float]) -> Optional[str]:
    """Generates advice based on Stop Loss optimization.

    Compares the user's average stress ratio (a proxy for SL) with the
    optimal p95 level calculated from winning trades.

    Args:
        avg_user_stress_ratio (Optional[float]): The user's average stress
            ratio (mae_usd / trade_risk).
        sl_opt_p95 (Optional[float]): The 95th percentile of the stress ratio
            from winning trades, representing an optimal SL.

    Returns:
        Optional[str]: A formatted string with actionable advice, or a message
        indicating insufficient data if inputs are invalid.
    """
    if avg_user_stress_ratio is None or sl_opt_p95 is None or avg_user_stress_ratio <= 0 or sl_opt_p95 <= 0:
        return "Nessun trade vincente nel periodo selezionato per calcolare l'ottimizzazione dello Stop Loss."

    diff_percentage = ((sl_opt_p95 - avg_user_stress_ratio) / avg_user_stress_ratio) * 100

    if diff_percentage > 15:
        return (
            f"**Stop Loss Troppo Stretto:** Il tuo SL medio ({avg_user_stress_ratio:.2f} R) è "
            f"significativamente più stretto dello SL ottimale suggerito ({sl_opt_p95:.2f} R), "
            f"calcolato sul 95% dei tuoi trade vincenti. Stai probabilmente tagliando vincite "
            f"a causa del rumore. **Azione:** Considera di testare uno SL più ampio "
            f"(es. {sl_opt_p95:.2f} R) per migliorare il Win Rate."
        )
    elif diff_percentage < -15:
        return (
             f"**Stop Loss Potenzialmente Troppo Ampio:** Il tuo SL medio ({avg_user_stress_ratio:.2f} R) è "
             f"più ampio di quanto necessario per la maggior parte dei tuoi trade vincenti ({sl_opt_p95:.2f} R). "
             f"**Azione:** Potresti valutare se uno SL leggermente più stretto (es. {sl_opt_p95:.2f} R) "
             f"migliora il R:R senza impattare troppo il Win Rate."
        )
    else:
         return (
             f"**Stop Loss Ben Calibrato:** Il tuo SL medio ({avg_user_stress_ratio:.2f} R) è ben allineato "
             f"con lo SL ottimale suggerito ({sl_opt_p95:.2f} R) per i tuoi trade vincenti. "
             f"Buona gestione del rischio iniziale."
         )

def generate_tp_advice(avg_user_planned_tp_r: Optional[float], tp_optimal_median: Optional[float]) -> Optional[str]:
    """Generates advice based on Take Profit optimization.

    Compares the user's average planned Take Profit in R-multiples with the
    median potential R achieved by their winning trades.

    Args:
        avg_user_planned_tp_r (Optional[float]): The user's average planned
            R-multiple for their take profits.
        tp_optimal_median (Optional[float]): The median 'potential_r'
            (mfe_usd / trade_risk) from winning trades.

    Returns:
        Optional[str]: A formatted string with actionable advice, or a message
        indicating insufficient data if inputs are invalid.
    """
    if avg_user_planned_tp_r is None or tp_optimal_median is None or avg_user_planned_tp_r <= 0 or tp_optimal_median <= 0:
        return "Nessun trade vincente nel periodo selezionato per calcolare l'ottimizzazione del Take Profit."

    diff_percentage = ((avg_user_planned_tp_r - tp_optimal_median) / tp_optimal_median) * 100

    if diff_percentage > 25:
        return (
            f"**Take Profit Troppo Ambizioso:** Il tuo TP medio pianificato ({avg_user_planned_tp_r:.2f} R) è "
            f"significativamente più alto del profitto mediano ({tp_optimal_median:.2f} R) raggiunto dai tuoi trade vincenti. "
            f"Questo aumenta il rischio di 'Reversal' (trade che tornano indietro). "
            f"**Azione:** Considera target più realistici (es. vicino a {tp_optimal_median:.2f} R) per "
            f"assicurare i profitti e migliorare il Profit Factor."
        )
    elif diff_percentage < -25:
         return (
             f"**Take Profit Troppo Conservativo:** Il tuo TP medio pianificato ({avg_user_planned_tp_r:.2f} R) è "
             f"molto più basso del potenziale mediano ({tp_optimal_median:.2f} R) dei tuoi trade vincenti. "
             f"Stai probabilmente uscendo troppo presto. **Azione:** Valuta se puoi "
             f"lasciar correre di più i profitti, puntando a target più vicini a {tp_optimal_median:.2f} R."
         )
    else:
        return (
            f"**Take Profit Realistico:** Il tuo TP medio pianificato ({avg_user_planned_tp_r:.2f} R) è "
            f"ben allineato con il potenziale mediano ({tp_optimal_median:.2f} R) dei tuoi trade vincenti. "
            f"Obiettivi di profitto ben calibrati."
        )

def generate_psychological_advice(r_autocorrelation: Optional[float], z_score_dd: Optional[float]) -> str:
    """Generates advice based on psychological metrics.

    Analyzes R-multiple autocorrelation for performance patterns and drawdown
    Z-score for unusual account drawdown.

    Args:
        r_autocorrelation (Optional[float]): The autocorrelation coefficient
            of realized R-multiples.
        z_score_dd (Optional[float]): The Z-score of the current account drawdown.

    Returns:
        str: A formatted string summarizing psychological alerts, or a confirmation
        that no significant patterns were detected.
    """
    advice_list = []

    if r_autocorrelation is not None:
        if r_autocorrelation < -0.15:
            advice_list.append(
                f"**Bias Negativo Rilevato (R-Autocorr: {r_autocorrelation:.2f}):** "
                f"Tendenza a performare peggio dopo un trade precedente (possibile overconfidence post-vittoria "
                f"o revenge trading post-perdita). **Azione:** Considera una pausa obbligatoria dopo ogni trade."
            )
        elif r_autocorrelation > 0.15:
            advice_list.append(
                f"**Tendenza a 'Streak' Rilevata (R-Autocorr: {r_autocorrelation:.2f}):** "
                f"I risultati dei trade tendono a raggrupparsi (serie positive/negative). "
                f"**Azione:** Sii consapevole delle spirali di perdite ('tilt'). Considera uno stop giornaliero dopo N perdite consecutive."
            )

    if z_score_dd is not None and z_score_dd > 1.5:
        advice_list.append(
            f"**Drawdown Anomalo (Z-Score: {z_score_dd:.1f}):** "
            f"Sei in un drawdown statisticamente più profondo del tuo solito. "
            f"**Azione:** Riduci l'esposizione o fai una pausa per rivalutare la strategia/mercato."
        )

    if not advice_list:
        return "✅ **Pattern Psicologici Stabili:** Nessun bias significativo rilevato nell'autocorrelazione dei risultati o nel drawdown attuale."

    return " \n".join(advice_list)

def generate_structured_advice(soa_results: Dict[str, Any]) -> Dict[str, Any]:
    """Orchestrates the generation of all structured advice.

    This function takes the complete numerical results from the SOAService,
    extracts the necessary metrics, and calls the specific advice-generation
    functions to produce a structured dictionary of textual advice.

    Args:
        soa_results (Dict[str, Any]): The complete dictionary of results from
            `SOAService.run_full_analysis()`.

    Returns:
        Dict[str, Any]: A dictionary containing all generated textual advice,
        keyed by advice type (e.g., 'sl_advice', 'tp_advice').
    """
    advice = {}
    optimization_data = soa_results.get("parametric_optimization", {})
    predictive_data = soa_results.get("predictive_metrics", {})
    drawdown_data = soa_results.get("drawdown_z_score", {})

    advice["sl_advice"] = generate_sl_advice(
        optimization_data.get("avg_user_stress_ratio"),
        optimization_data.get("sl_optimal_p95")
    )
    advice["tp_advice"] = generate_tp_advice(
        optimization_data.get("avg_user_planned_tp_r"),
        optimization_data.get("tp_optimal_median")
    )
    advice["psychological_advice"] = generate_psychological_advice(
        predictive_data.get("r_autocorrelation"),
        drawdown_data.get("z_score")
    )
    advice["headline_insight"] = soa_results.get("headline_insight")

    return advice
