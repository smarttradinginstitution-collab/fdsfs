# backend/app/Services/soa_service.py
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from typing import List, Dict, Any, Optional
from scipy.stats import zscore, pearsonr

class SOAService:
    """Service for advanced Strength & Opportunity Analysis (SOA) of trades.

    This service takes raw trade data, preprocesses it into a pandas DataFrame,
    and provides methods for clustering, causal analysis, and parametric
    optimization. It is designed to be the computational core of the SOA feature.

    Attributes:
        raw_trades (List[Dict[str, Any]]): The initial list of trade dictionaries.
        df (pd.DataFrame): The preprocessed and cleaned pandas DataFrame used
            for all analyses.
    """
    def __init__(self, trades_data: List[Dict[str, Any]]):
        """Initializes the SOAService with a list of raw trade data.

        Args:
            trades_data (List[Dict[str, Any]]): A list of dictionaries, where
                each dictionary represents a trade with its enriched metrics.
        """
        self.raw_trades = trades_data
        self.df = self._preprocess_data()

    def _preprocess_data(self) -> pd.DataFrame:
        """Converts raw trade data into a cleaned pandas DataFrame for analysis.

        This private method performs several key steps:
        1.  Constructs a DataFrame from the raw data.
        2.  Converts all numerical metrics from Decimal/str to float, coercing errors.
        3.  Filters out invalid trades by dropping rows with NaN in critical columns
            (`trade_risk`, `p_l`, `duration_minutes`).
        4.  Ensures all trades have a positive `trade_risk`.
        5.  Calculates the Duration Deviation (DD) as a z-score of `duration_minutes`.
        6.  Fills any remaining NaN values in SOA vectors with 0.

        Returns:
            pd.DataFrame: A cleaned and prepared DataFrame ready for analysis.
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
        cols_for_dropna = ['trade_risk', 'p_l', 'duration_minutes']
        df = df.dropna(subset=cols_for_dropna)

        if not df.empty:
            df = df[df['trade_risk'] > 0]

        # 4. Calcolo Deviazione Durata (DD) - Z-score
        if not df.empty and df['duration_minutes'].nunique() > 1:
            df['DD'] = zscore(df['duration_minutes'])
        else:
            df['DD'] = 0.0

        # 5. Gestione NaN strategica per i vettori SOA
        soa_vectors = ['SN', 'EP', 'RRv', 'ES', 'RER', 'DD']
        for vector in soa_vectors:
            if vector not in df.columns:
                df[vector] = 0.0
        df[soa_vectors] = df[soa_vectors].fillna(0)

        return df

    def run_full_analysis(self) -> Dict[str, Any]:
        """Orchestrates the execution of all SOA analysis levels.

        This is the main public method that calls all the individual analysis
        steps and assembles their results into a single, comprehensive dictionary.
        It handles the edge case of no valid trades by returning a default,
        empty structure that conforms to the API schema.

        Returns:
            Dict[str, Any]: A nested dictionary containing the results of all
            analysis, including clustering, causal analysis, parametric
            optimization, predictive metrics, and trade details.
        """
        if self.df.empty:
            return {
                "clusters_summary": {},
                "causal_analysis": {
                    'playbook': [], 'tag': [], 'mistake': [],
                    'psychology': [], 'news': [], 'rule': []
                },
                "parametric_optimization": {
                    "sl_optimal_p90": None,
                    "sl_optimal_p95": None,
                    "tp_optimal_median": None,
                    "tp_optimal_mean": None,
                    "avg_user_stress_ratio": 0.0,
                    "avg_user_planned_tp_r": 0.0,
                    "duration_expectancy": []
                },
                "predictive_metrics": {
                    "r_autocorrelation": 0.0,
                },
                "trade_details": [],
                "headline_insight": "Nessun trade disponibile per l'analisi.",
            }

        self.cluster_trades()
        causal_analysis = {
            'playbook': self.analyze_clusters_by_attribute('playbook_id'),
            'tag': self.analyze_clusters_by_attribute('tag_ids', explode=True),
            'mistake': self.analyze_clusters_by_attribute('mistake_ids', explode=True),
            'psychology': self.analyze_clusters_by_attribute('psychology_state_ids', explode=True),
            'news': self.analyze_clusters_by_attribute('news_impact_ids', explode=True),
            'rule': self.analyze_clusters_by_attribute('rule_ids', explode=True)
        }
        sl_tp_optimization = self.optimize_sl_tp()
        duration_expectancy = self.analyze_expectancy_by_duration()
        r_autocorrelation = self.calculate_r_autocorrelation()
        user_averages = self._calculate_user_averages()

        parametric_optimization = {
            **sl_tp_optimization,
            **user_averages,
            "duration_expectancy": duration_expectancy
        }
        headline_insight = self._generate_headline_insight(parametric_optimization, r_autocorrelation)

        clusters_summary = self.get_clusters_summary()
        total_trades = sum(cluster['trade_count'] for cluster in clusters_summary.values())
        cluster_percentages = {
            label: (summary['trade_count'] / total_trades) * 100 if total_trades > 0 else 0
            for label, summary in clusters_summary.items()
        }

        return {
            "clusters_summary": clusters_summary,
            "cluster_percentages": cluster_percentages,
            "causal_analysis": causal_analysis,
            "parametric_optimization": parametric_optimization,
            "predictive_metrics": {
                "r_autocorrelation": r_autocorrelation,
            },
            "trade_details": self.df.to_dict(orient='records'),
            "headline_insight": headline_insight,
        }

    def _calculate_user_averages(self) -> Dict[str, float]:
        """Calculates the user's average stress ratio and planned R-multiple for TP.

        Returns:
            Dict[str, float]: A dictionary containing the user's average metrics.
        """
        if self.df.empty:
            return {"avg_user_stress_ratio": 0.0, "avg_user_planned_tp_r": 0.0}

        stress_ratio = (self.df['mae_usd'] / self.df['trade_risk']).replace([np.inf, -np.inf], np.nan)
        avg_stress_ratio = stress_ratio.dropna().mean()
        avg_tp_r = self.df['planned_r_multiple'].dropna().mean()

        return {
            "avg_user_stress_ratio": avg_stress_ratio,
            "avg_user_planned_tp_r": avg_tp_r,
        }

    def _generate_headline_insight(self, sl_tp_data: Dict, r_autocorr: float) -> str:
        """Generates a brief, actionable text insight based on critical metrics.

        Args:
            sl_tp_data (Dict): The dictionary of SL/TP optimization results.
            r_autocorr (float): The calculated R-multiple autocorrelation.

        Returns:
            str: A formatted string with the most important insight.
        """
        if sl_tp_data.get('sl_optimal_p95', 0) > sl_tp_data.get('avg_user_stress_ratio', 0) * 1.5:
             return "⚠ Stop Loss potenzialmente troppo stretti: rischi di uscite premature."
        if abs(r_autocorr) > 0.3:
            return f"🧠 Pattern psicologico rilevato: l'esito di un trade sembra influenzare il successivo (Autocorr: {r_autocorr:.2f})."
        return "✅ Analisi completata. Nessun alert critico rilevato."

    def cluster_trades(self, n_clusters: int = 5) -> None:
        """Performs K-Means clustering on the SOA vectors.

        This method standardizes the 6 SOA vectors + DD, runs K-Means, and adds
        'cluster_id' and 'cluster_label' columns to the DataFrame.

        Args:
            n_clusters (int): The number of clusters to form.
        """
        soa_vectors = ['SN', 'EP', 'RRv', 'ES', 'RER', 'DD']
        for col in soa_vectors:
            if col not in self.df.columns:
                self.df[col] = 0.0

        X = self.df[soa_vectors].values
        if X.shape[0] < n_clusters:
            self.df['cluster_id'] = 0
            return

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        self.df['cluster_id'] = kmeans.fit_predict(X_scaled)
        cluster_map = {i: chr(65 + i) for i in range(n_clusters)}
        self.df['cluster_label'] = self.df['cluster_id'].map(cluster_map)

    def get_clusters_summary(self) -> Dict[str, Any]:
        """Generates a summary of the average characteristics of each cluster.

        Returns:
            Dict[str, Any]: A dictionary where keys are cluster labels and
            values are dictionaries of the mean metric values for that cluster.
        """
        if 'cluster_id' not in self.df.columns:
            return {}

        soa_vectors = ['SN', 'EP', 'RRv', 'ES', 'RER', 'DD', 'p_l', 'realized_r_multiple', 'duration_minutes']
        summary = self.df.groupby('cluster_label')[soa_vectors].mean().to_dict(orient='index')
        counts = self.df.groupby('cluster_label').size().to_dict()
        for label, count in counts.items():
            if label in summary:
                summary[label]['trade_count'] = count
        return summary

    def analyze_clusters_by_attribute(self, attribute_col: str, explode: bool = False) -> List[Dict]:
        """Analyzes the relationship between a trade attribute and the clusters.

        This method groups trades by a specific attribute (e.g., 'playbook_id' or
        'tag_ids') and calculates the distribution and performance across clusters
        for that attribute.

        Args:
            attribute_col (str): The DataFrame column name of the attribute to analyze.
            explode (bool): If True, the method will "explode" list-like entries
                in the attribute column (for many-to-many relationships like tags).

        Returns:
            List[Dict]: A list of dictionaries, each representing the performance
            of an attribute value within a specific cluster.
        """
        if attribute_col not in self.df.columns or 'cluster_label' not in self.df.columns:
            return []

        df_analysis = self.df.copy()
        if explode:
            df_analysis = df_analysis.dropna(subset=[attribute_col])
            df_analysis = df_analysis[df_analysis[attribute_col].apply(lambda x: isinstance(x, list) and len(x) > 0)]
            if df_analysis.empty:
                return []
            df_analysis = df_analysis.explode(attribute_col)

        df_analysis = df_analysis.dropna(subset=[attribute_col, 'cluster_label'])
        if df_analysis.empty:
            return []

        grouped = df_analysis.groupby([attribute_col, 'cluster_label'])
        agg_metrics = {
            'p_l': ['count', 'sum'],
            'SN': 'mean', 'EP': 'mean', 'RRv': 'mean',
            'ES': 'mean', 'RER': 'mean', 'DD': 'mean'
        }
        result = grouped.agg(agg_metrics)
        result.columns = ['_'.join(col).strip() for col in result.columns.values]
        result = result.rename(columns={'p_l_count': 'trade_count', 'p_l_sum': 'total_pnl'})

        total_counts_per_attribute = df_analysis.groupby(attribute_col).size()
        result['probability'] = result.index.map(lambda x: result.loc[x, 'trade_count'] / total_counts_per_attribute[x[0]])
        result = result.reset_index()
        result = result.rename(columns={attribute_col: 'attribute_col'})

        return result.to_dict(orient='records')

    def optimize_sl_tp(self) -> Dict[str, Optional[float]]:
        """Calculates optimal Stop Loss and Take Profit levels from historical data.

        This analysis is performed only on winning trades (p_l > 0).
        - SL is optimized based on the 'stress ratio' (mae_usd / trade_risk).
        - TP is optimized based on the 'potential_r' (mfe_usd / trade_risk).

        Returns:
            Dict[str, Optional[float]]: A dictionary with optimal p90/p95 SL
            and median/mean TP values. Returns None for values if calculation
            is not possible (e.g., no winning trades).
        """
        df_win = self.df[self.df['p_l'] > 0].copy()

        if df_win.empty:
            return {
                "sl_optimal_p90": None, "sl_optimal_p95": None,
                "tp_optimal_median": None, "tp_optimal_mean": None
            }

        stress_ratio_series = (df_win['mae_usd'] / df_win['trade_risk']).replace([np.inf, -np.inf], np.nan).dropna()
        potential_r_series = (df_win['mfe_usd'] / df_win['trade_risk']).replace([np.inf, -np.inf], np.nan).dropna()

        if stress_ratio_series.empty or potential_r_series.empty:
            return {
                "sl_optimal_p90": None, "sl_optimal_p95": None,
                "tp_optimal_median": None, "tp_optimal_mean": None
            }

        return {
            "sl_optimal_p90": float(stress_ratio_series.quantile(0.90)),
            "sl_optimal_p95": float(stress_ratio_series.quantile(0.95)),
            "tp_optimal_median": float(potential_r_series.median()),
            "tp_optimal_mean": float(potential_r_series.mean()),
        }

    def analyze_expectancy_by_duration(self, n_deciles: int = 10) -> List[Dict]:
        """Calculates trading expectancy across deciles of trade duration.

        Args:
            n_deciles (int): The number of groups (quantiles) to split the
                duration data into.

        Returns:
            List[Dict]: A list of dictionaries, each containing the expectancy
            and other stats for a duration decile.
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
            expectancy = (win_rate * avg_win) + (loss_rate * avg_loss)
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
        """Calculates the autocorrelation of Realized R-multiples.

        This metric can indicate psychological patterns, such as a tendency
        for performance to be influenced by the previous trade's outcome.

        Args:
            lag (int): The lag (number of trades back) to use for the
                autocorrelation calculation.

        Returns:
            float: The autocorrelation coefficient, between -1 and 1.
        """
        if self.df['realized_r_multiple'].nunique() <= 1:
            return 0.0

        df_sorted = self.df.sort_values(by='exit_timestamp').dropna(subset=['realized_r_multiple'])
        if len(df_sorted) < lag + 2:
            return 0.0

        autocorr = df_sorted['realized_r_multiple'].autocorr(lag=lag)
        return autocorr if pd.notna(autocorr) else 0.0

    def calculate_drawdown_zscore(self, daily_balances: List[Dict]) -> Dict:
        """Calculates the Z-score of the current drawdown.

        This metric indicates how statistically significant the current drawdown
        is compared to the historical average drawdown.

        Args:
            daily_balances (List[Dict]): A list of dictionaries, each with 'date'
                and 'balance' keys.

        Returns:
            Dict: A dictionary containing the z_score and other drawdown stats,
            always conforming to the Pydantic schema.
        """
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
        if std_drawdown == 0 or pd.isna(std_drawdown):
            z_score = 0.0
        else:
            z_score = (current_drawdown - avg_drawdown) / std_drawdown if current_drawdown < 0 else 0.0

        return {
            "z_score": z_score,
            "current_drawdown_usd": current_drawdown,
            "average_drawdown_usd": avg_drawdown,
            "stddev_drawdown_usd": std_drawdown if pd.notna(std_drawdown) else 0.0
        }
