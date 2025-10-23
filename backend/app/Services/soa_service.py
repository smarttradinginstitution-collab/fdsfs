# backend/app/Services/soa_service.py
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from typing import List, Dict, Any
from scipy.stats import zscore, pearsonr

class SOAService:
    """
    Servizio per l'analisi avanzata dei trade (SOA - Strength & Opportunity Analysis).
    """
    def __init__(self, trades_data: List[Dict[str, Any]]):
        self.raw_trades = trades_data
        self.df = self._preprocess_data()

    def _preprocess_data(self) -> pd.DataFrame:
        """
        Converte i dati grezzi dei trade in un DataFrame Pandas, calcola le metriche
        necessarie e pulisce i dati per l'analisi.
        """
        if not self.raw_trades:
            return pd.DataFrame()

        # 1. Costruzione del DataFrame
        df = pd.DataFrame(self.raw_trades)

        # 2. Conversione Decimal in float e gestione tipi
        cols_to_convert = ['p_l', 'trade_risk', 'mae_usd', 'mfe_usd', 'realized_r_multiple', 'planned_r_multiple', 'duration_minutes', 'SN', 'EP', 'RRv', 'ES', 'RER']
        for col in cols_to_convert:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # 3. Filtro trade non validi per l'analisi
        # Fase 3a: dropna
        cols_for_dropna = ['trade_risk', 'p_l', 'duration_minutes']

        df = df.dropna(subset=cols_for_dropna)

        # Fase 3b: trade_risk > 0
        if not df.empty:

            df = df[df['trade_risk'] > 0]

        # 4. Calcolo Deviazione Durata (DD) - Z-score
        if not df.empty and df['duration_minutes'].nunique() > 1:
            df['DD'] = zscore(df['duration_minutes'])
        else:
            df['DD'] = 0.0

        # 5. Gestione NaN strategica per i vettori SOA
        # I valori condizionali (EP, RRv, ES) sono già a 0 se non applicabili (da enricher)
        # Riempiamo eventuali NaN rimanenti nei vettori con 0, assumendo assenza del fenomeno
        soa_vectors = ['SN', 'EP', 'RRv', 'ES', 'RER', 'DD']
        for vector in soa_vectors:
            if vector not in df.columns:
                df[vector] = 0.0 # Aggiungi colonna se non esiste
        df[soa_vectors] = df[soa_vectors].fillna(0)


        return df

    def run_full_analysis(self):
        """
        Orchestra l'esecuzione di tutte le analisi SOA e restituisce i risultati combinati.
        Restituisce sempre una struttura dati valida per lo schema Pydantic.
        """
        if self.df.empty:
            # Ritorna una struttura dati di default se non ci sono trade validi
            return {
                "clusters_summary": {},
                "causal_analysis": {
                    'playbook': [], 'tag': [], 'mistake': [],
                    'psychology': [], 'news': [], 'rule': []
                },
                "parametric_optimization": {
                    "sl_tp": {},
                    "duration_expectancy": [],
                },
                "predictive_metrics": {
                    "r_autocorrelation": 0.0,
                },
                "trade_details": [],
                "headline_insight": "Nessun trade disponibile per l'analisi.",
            }

        # Livello 1: Clustering
        self.cluster_trades()

        # Livello 2: Analisi Causale
        causal_analysis = {
            'playbook': self.analyze_clusters_by_attribute('playbook_id'),
            'tag': self.analyze_clusters_by_attribute('tag_ids', explode=True),
            'mistake': self.analyze_clusters_by_attribute('mistake_ids', explode=True),
            'psychology': self.analyze_clusters_by_attribute('psychology_state_ids', explode=True),
            'news': self.analyze_clusters_by_attribute('news_impact_ids', explode=True),
            'rule': self.analyze_clusters_by_attribute('rule_ids', explode=True)
        }

        # Livello 3: Ottimizzazione Parametrica
        sl_tp_optimization = self.optimize_sl_tp()
        duration_expectancy = self.analyze_expectancy_by_duration()

        # Livello 4: Metriche Predittive
        r_autocorrelation = self.calculate_r_autocorrelation()

        # Calcolo medie utente e headline insight
        user_averages = self._calculate_user_averages()
        sl_tp_optimization.update(user_averages) # Aggiungo le medie utente ai dati di ottimizzazione

        headline_insight = self._generate_headline_insight(sl_tp_optimization, r_autocorrelation)


        return {
            "clusters_summary": self.get_clusters_summary(),
            "causal_analysis": causal_analysis,
            "parametric_optimization": {
                "sl_tp": sl_tp_optimization,
                "duration_expectancy": duration_expectancy,
            },
            "predictive_metrics": {
                "r_autocorrelation": r_autocorrelation,
            },
            "trade_details": self.df.to_dict(orient='records'),
            "headline_insight": headline_insight,
        }

    def _calculate_user_averages(self) -> Dict:
        """Calcola lo stress ratio medio e il TP pianificato medio dall'utente."""
        if self.df.empty:
            return {"avg_user_stress_ratio": 0.0, "avg_user_planned_tp_r": 0.0}

        # Calcola lo stress ratio per ogni trade e poi fanne la media
        stress_ratio = (self.df['mae_usd'] / self.df['trade_risk']).replace([np.inf, -np.inf], np.nan)
        avg_stress_ratio = stress_ratio.dropna().mean()

        # Per TP, la media del planned_r_multiple è la metrica più diretta
        avg_tp_r = self.df['planned_r_multiple'].dropna().mean()

        return {
            "avg_user_stress_ratio": avg_stress_ratio,
            "avg_user_planned_tp_r": avg_tp_r,
        }

    def _generate_headline_insight(self, sl_tp_data: Dict, r_autocorr: float) -> str:
        """Genera un insight testuale basato sui dati più critici."""

        # Logica di esempio, da affinare
        if sl_tp_data.get('sl_optimal_p95', 0) > sl_tp_data.get('avg_user_stress_ratio', 0) * 1.5:
             return "⚠ Stop Loss potenzialmente troppo stretti: rischi di uscite premature."

        if abs(r_autocorr) > 0.3:
            return f"🧠 Pattern psicologico rilevato: l'esito di un trade sembra influenzare il successivo (Autocorr: {r_autocorr:.2f})."

        # Aggiungere qui altre logiche, es. analisi P/L cluster

        return "✅ Analisi completata. Nessun alert critico rilevato."


    def cluster_trades(self, n_clusters: int = 5) -> None:
        """
        Esegue il clustering K-Means sui vettori SOA + DD.
        """
        soa_vectors = ['SN', 'EP', 'RRv', 'ES', 'RER', 'DD']

        # Assicurati che tutte le colonne esistano, anche se vuote
        for col in soa_vectors:
            if col not in self.df.columns:
                self.df[col] = 0.0

        X = self.df[soa_vectors].values

        if X.shape[0] < n_clusters:
            # Non ci sono abbastanza dati per formare i cluster richiesti
            self.df['cluster_id'] = 0
            return

        # Standardizzazione dei dati
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Esecuzione KMeans
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        self.df['cluster_id'] = kmeans.fit_predict(X_scaled)

        # Mappatura opzionale a etichette
        cluster_map = {i: chr(65 + i) for i in range(n_clusters)}
        self.df['cluster_label'] = self.df['cluster_id'].map(cluster_map)

    def get_clusters_summary(self) -> Dict:
        """
        Restituisce un riepilogo delle caratteristiche medie di ogni cluster.
        """
        if 'cluster_id' not in self.df.columns:
            return {}

        soa_vectors = ['SN', 'EP', 'RRv', 'ES', 'RER', 'DD', 'p_l', 'realized_r_multiple', 'duration_minutes']
        summary = self.df.groupby('cluster_label')[soa_vectors].mean().to_dict(orient='index')

        # Aggiungi conteggio trade per cluster
        counts = self.df.groupby('cluster_label').size().to_dict()
        for label, count in counts.items():
            if label in summary:
                summary[label]['trade_count'] = count

        return summary

    def analyze_clusters_by_attribute(self, attribute_col: str, explode: bool = False) -> List[Dict]:
        """
        Analizza la relazione tra un attributo (es. playbook, tag) e i cluster.
        Restituisce sempre una lista di dizionari per la validazione Pydantic.
        """
        if attribute_col not in self.df.columns or 'cluster_label' not in self.df.columns:
            return []

        df_analysis = self.df.copy()

        if explode:
            # Gestione delle liste di ID per relazioni M-to-M
            df_analysis = df_analysis.dropna(subset=[attribute_col])
            df_analysis = df_analysis[df_analysis[attribute_col].apply(lambda x: isinstance(x, list) and len(x) > 0)]
            if df_analysis.empty:
                return []
            df_analysis = df_analysis.explode(attribute_col)

        df_analysis = df_analysis.dropna(subset=[attribute_col, 'cluster_label'])

        if df_analysis.empty:
            return []

        # Calcoli principali
        grouped = df_analysis.groupby([attribute_col, 'cluster_label'])

        # Conteggio, P/L totale, e medie dei vettori SOA
        agg_metrics = {
            'p_l': ['count', 'sum'],
            'SN': 'mean', 'EP': 'mean', 'RRv': 'mean',
            'ES': 'mean', 'RER': 'mean', 'DD': 'mean'
        }
        result = grouped.agg(agg_metrics)
        result.columns = ['_'.join(col).strip() for col in result.columns.values]
        result = result.rename(columns={'p_l_count': 'trade_count', 'p_l_sum': 'total_pnl'})

        # Calcolo P(Cluster | Attributo)
        total_counts_per_attribute = df_analysis.groupby(attribute_col).size()
        result['probability'] = result.index.map(lambda x: result.loc[x, 'trade_count'] / total_counts_per_attribute[x[0]])

        result = result.reset_index()
        # Rinomina la colonna ID per corrispondere all'alias Pydantic 'attribute_col'
        result = result.rename(columns={attribute_col: 'attribute_col'})

        return result.to_dict(orient='records')

    def optimize_sl_tp(self) -> Dict:
        """
        Calcola i livelli ottimali di Stop Loss e Take Profit basati sui dati storici.
        """
        df_win = self.df[self.df['p_l'] > 0].copy()

        if df_win.empty:
            return {}

        df_win['stress_ratio'] = (df_win['mae_usd'] / df_win['trade_risk']).replace([np.inf, -np.inf], np.nan)
        df_win['potential_r'] = (df_win['mfe_usd'] / df_win['trade_risk']).replace([np.inf, -np.inf], np.nan)

        return {
            "sl_optimal_p90": df_win['stress_ratio'].quantile(0.90),
            "sl_optimal_p95": df_win['stress_ratio'].quantile(0.95),
            "tp_optimal_median": df_win['potential_r'].median(),
            "tp_optimal_mean": df_win['potential_r'].mean(),
        }

    def analyze_expectancy_by_duration(self, n_deciles: int = 10) -> List[Dict]:
        """
        Calcola l'aspettativa (Expectancy) per decili di durata dei trade.
        """
        if 'duration_minutes' not in self.df.columns or self.df['duration_minutes'].nunique() < n_deciles:
            return []

        self.df['duration_decile'] = pd.qcut(self.df['duration_minutes'], q=n_deciles, labels=False, duplicates='drop')

        grouped = self.df.groupby('duration_decile')

        results = []
        for name, group in grouped:
            wins = group[group['p_l'] > 0]
            losses = group[group['p_l'] <= 0]

            win_rate = len(wins) / len(group) if len(group) > 0 else 0
            loss_rate = 1 - win_rate

            avg_win = wins['p_l'].mean() if not wins.empty else 0
            avg_loss = losses['p_l'].mean() if not losses.empty else 0

            expectancy = (win_rate * avg_win) + (loss_rate * avg_loss) # avg_loss è già negativo

            results.append({
                "decile": name,
                "avg_duration": group['duration_minutes'].mean(),
                "expectancy": expectancy,
                "win_rate": win_rate,
                "avg_win_pnl": avg_win,
                "avg_loss_pnl": avg_loss,
                "trade_count": len(group)
            })

        return results

    def calculate_r_autocorrelation(self, lag: int = 1) -> float:
        """
        Calcola l'autocorrelazione dei Realized R-multiples.
        """
        if self.df['realized_r_multiple'].nunique() <= 1:
            return 0.0 # Varianza nulla, autocorrelazione non definita

        df_sorted = self.df.sort_values(by='exit_timestamp').dropna(subset=['realized_r_multiple'])

        if len(df_sorted) < lag + 2:
            return 0.0

        autocorr = df_sorted['realized_r_multiple'].autocorr(lag=lag)
        return autocorr if pd.notna(autocorr) else 0.0


    def calculate_drawdown_zscore(self, daily_balances: List[Dict]) -> Dict:
        """
        Calcola lo Z-score del drawdown corrente basato sulla serie storica dei saldi.
        Restituisce sempre una struttura dati completa e valida per lo schema Pydantic.
        """
        # Valori di default che garantiscono la validazione Pydantic
        default_return = {
            "z_score": 0.0,
            "current_drawdown_usd": 0.0,
            "average_drawdown_usd": 0.0,
            "stddev_drawdown_usd": 0.0
        }

        if not daily_balances or len(daily_balances) < 2:
            return default_return

        df_balance = pd.DataFrame(daily_balances)
        df_balance['date'] = pd.to_datetime(df_balance['date'])
        df_balance = df_balance.sort_values(by='date')
        df_balance['balance'] = pd.to_numeric(df_balance['balance'])

        df_balance['peak_balance'] = df_balance['balance'].expanding().max()
        df_balance['drawdown'] = df_balance['balance'] - df_balance['peak_balance']

        drawdowns = df_balance[df_balance['drawdown'] < 0]['drawdown']

        current_drawdown = df_balance['drawdown'].iloc[-1]

        if drawdowns.empty:
            default_return["current_drawdown_usd"] = current_drawdown if current_drawdown < 0 else 0.0
            return default_return

        avg_drawdown = drawdowns.mean()
        std_drawdown = drawdowns.std()

        # Se non c'è deviazione, lo z-score non è calcolabile in modo significativo
        if std_drawdown == 0 or pd.isna(std_drawdown):
            z_score = 0.0
        else:
            # Lo Z-score ha senso solo se siamo in drawdown
            z_score = (current_drawdown - avg_drawdown) / std_drawdown if current_drawdown < 0 else 0.0

        return {
            "z_score": z_score,
            "current_drawdown_usd": current_drawdown,
            "average_drawdown_usd": avg_drawdown,
            "stddev_drawdown_usd": std_drawdown if pd.notna(std_drawdown) else 0.0
        }

# Esempio di utilizzo (per sviluppo e test)
if __name__ == '__main__':
    # Qui andrebbero i dati di esempio
    pass
