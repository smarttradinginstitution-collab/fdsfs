# app/Services/soa_advisor.py
from typing import Dict, Any, Optional

def generate_sl_advice(avg_user_stress_ratio: Optional[float], sl_opt_p95: Optional[float]) -> Optional[str]:
    """Genera consiglio basato sull'ottimizzazione dello Stop Loss."""
    if avg_user_stress_ratio is None or sl_opt_p95 is None or avg_user_stress_ratio <= 0 or sl_opt_p95 <= 0:
        return "Nessun trade vincente nel periodo selezionato per calcolare l'ottimizzazione dello Stop Loss."

    diff_percentage = ((sl_opt_p95 - avg_user_stress_ratio) / avg_user_stress_ratio) * 100

    if diff_percentage > 15: # Se l'ottimale è significativamente più ampio (>15%)
        return (
            f"**Stop Loss Troppo Stretto:** Il tuo SL medio ({avg_user_stress_ratio:.2f} R) è "
            f"significativamente più stretto dello SL ottimale suggerito ({sl_opt_p95:.2f} R), "
            f"calcolato sul 95% dei tuoi trade vincenti. Stai probabilmente tagliando vincite "
            f"a causa del rumore. **Azione:** Considera di testare uno SL più ampio "
            f"(es. {sl_opt_p95:.2f} R) per migliorare il Win Rate."
        )
    elif diff_percentage < -15: # Se l'ottimale è significativamente più stretto (raro, ma possibile)
        return (
             f"**Stop Loss Potenzialmente Troppo Ampio:** Il tuo SL medio ({avg_user_stress_ratio:.2f} R) è "
             f"più ampio di quanto necessario per la maggior parte dei tuoi trade vincenti ({sl_opt_p95:.2f} R). "
             f"**Azione:** Potresti valutare se uno SL leggermente più stretto (es. {sl_opt_p95:.2f} R) "
             f"migliora il R:R senza impattare troppo il Win Rate."
        )
    else: # Se sono vicini
         return (
             f"**Stop Loss Ben Calibrato:** Il tuo SL medio ({avg_user_stress_ratio:.2f} R) è ben allineato "
             f"con lo SL ottimale suggerito ({sl_opt_p95:.2f} R) per i tuoi trade vincenti. "
             f"Buona gestione del rischio iniziale."
         )

def generate_tp_advice(avg_user_planned_tp_r: Optional[float], tp_median: Optional[float]) -> Optional[str]:
    """Genera consiglio basato sull'ottimizzazione del Take Profit."""
    if avg_user_planned_tp_r is None or tp_median is None or avg_user_planned_tp_r <= 0 or tp_median <= 0:
        return "Nessun trade vincente nel periodo selezionato per calcolare l'ottimizzazione del Take Profit."

    diff_percentage = ((avg_user_planned_tp_r - tp_median) / tp_median) * 100

    if diff_percentage > 25: # Se il TP pianificato è molto più alto della mediana (>25%)
        return (
            f"**Take Profit Troppo Ambizioso:** Il tuo TP medio pianificato ({avg_user_planned_tp_r:.2f} R) è "
            f"significativamente più alto del profitto mediano ({tp_median:.2f} R) raggiunto dai tuoi trade vincenti. "
            f"Questo aumenta il rischio di 'Reversal' (trade che tornano indietro). "
            f"**Azione:** Considera target più realistici (es. vicino a {tp_median:.2f} R) per "
            f"assicurare i profitti e migliorare il Profit Factor."
        )
    elif diff_percentage < -25: # Se il TP pianificato è molto più basso della mediana (lasci soldi sul tavolo)
         return (
             f"**Take Profit Troppo Conservativo:** Il tuo TP medio pianificato ({avg_user_planned_tp_r:.2f} R) è "
             f"molto più basso del potenziale mediano ({tp_median:.2f} R) dei tuoi trade vincenti. "
             f"Stai probabilmente uscendo troppo presto. **Azione:** Valuta se puoi "
             f"lasciar correre di più i profitti, puntando a target più vicini a {tp_median:.2f} R."
         )
    else: # Se sono vicini
        return (
            f"**Take Profit Realistico:** Il tuo TP medio pianificato ({avg_user_planned_tp_r:.2f} R) è "
            f"ben allineato con il potenziale mediano ({tp_median:.2f} R) dei tuoi trade vincenti. "
            f"Obiettivi di profitto ben calibrati."
        )

def generate_psychological_advice(r_autocorrelation: Optional[float], z_score_dd: Optional[float]) -> str:
    """Genera consiglio basato sugli alert psicologici."""
    advice_list = []

    # Autocorrelazione
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

    # Z-Score Drawdown
    if z_score_dd is not None and z_score_dd > 1.5: # Soglia esempio
        advice_list.append(
            f"**Drawdown Anomalo (Z-Score: {z_score_dd:.1f}):** "
            f"Sei in un drawdown statisticamente più profondo del tuo solito. "
            f"**Azione:** Riduci l'esposizione o fai una pausa per rivalutare la strategia/mercato."
        )

    if not advice_list:
        return "✅ **Pattern Psicologici Stabili:** Nessun bias significativo rilevato nell'autocorrelazione dei risultati o nel drawdown attuale."

    return " \n".join(advice_list) # Unisce i consigli se ce ne sono multipli

# --- Funzione Principale ---
def generate_structured_advice(soa_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prende i risultati numerici SOA e aggiunge i consigli strutturati.
    """
    advice = {}

    # Estrai i dati necessari da soa_results (usa .get() per sicurezza)
    optimization_data = soa_results.get("parametric_optimization", {})
    predictive_data = soa_results.get("predictive_metrics", {})
    drawdown_data = soa_results.get("drawdown_z_score", {})

    # Genera consigli
    advice["sl_advice"] = generate_sl_advice(
        optimization_data.get("avg_user_stress_ratio"), # Corretto
        optimization_data.get("sl_optimal_p95") # Corretto
    )
    advice["tp_advice"] = generate_tp_advice(
        optimization_data.get("avg_user_planned_tp_r"),
        optimization_data.get("tp_optimal_median") # Corretto
    )
    advice["psychological_advice"] = generate_psychological_advice(
        predictive_data.get("r_autocorrelation"),
        drawdown_data.get("z_score")
    )
    advice["headline_insight"] = soa_results.get("headline_insight") # Assumendo che sia già generato

    # Puoi aggiungere qui la logica per generare consigli basati sui cluster
    # es. analizzando soa_results.get("causal_analysis")

    return advice
