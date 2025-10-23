# backend/tests/services/test_soa_service.py
import pytest
import pandas as pd
from decimal import Decimal
from datetime import datetime, timedelta
from app.Services.soa_service import SOAService

# Dati di test per i trade
mock_trades_data = [
    {
        'id': '1', 'p_l': Decimal('150.0'), 'trade_risk': Decimal('50.0'), 'mae_usd': Decimal('20.0'),
        'mfe_usd': Decimal('200.0'), 'realized_r_multiple': Decimal('3.0'), 'planned_r_multiple': Decimal('2.0'),
        'duration_minutes': 60, 'exit_timestamp': datetime(2023, 1, 1, 10, 0),
        'playbook_id': 'pb_1', 'tag_ids': ['tag_a', 'tag_b'], 'mistake_ids': [],
        'psychology_state_ids': ['ps_calm'], 'news_impact_ids': [], 'rule_ids': ['rule_1'],
        'SN': Decimal('0.4'), 'EP': Decimal('0.75'), 'RRv': Decimal('0'), 'ES': Decimal('0'), 'RER': Decimal('1.5')
    },
    {
        'id': '2', 'p_l': Decimal('-50.0'), 'trade_risk': Decimal('50.0'), 'mae_usd': Decimal('55.0'),
        'mfe_usd': Decimal('10.0'), 'realized_r_multiple': Decimal('-1.0'), 'planned_r_multiple': Decimal('2.0'),
        'duration_minutes': 30, 'exit_timestamp': datetime(2023, 1, 1, 12, 0),
        'playbook_id': 'pb_1', 'tag_ids': ['tag_c'], 'mistake_ids': ['err_1'],
        'psychology_state_ids': ['ps_fomo'], 'news_impact_ids': [], 'rule_ids': [],
        'SN': Decimal('1.1'), 'EP': Decimal('0'), 'RRv': Decimal('0.2'), 'ES': Decimal('1.1'), 'RER': Decimal('-0.5')
    },
    {
        'id': '3', 'p_l': Decimal('300.0'), 'trade_risk': Decimal('100.0'), 'mae_usd': Decimal('10.0'),
        'mfe_usd': Decimal('350.0'), 'realized_r_multiple': Decimal('3.0'), 'planned_r_multiple': Decimal('3.0'),
        'duration_minutes': 120, 'exit_timestamp': datetime(2023, 1, 2, 10, 0),
        'playbook_id': 'pb_2', 'tag_ids': ['tag_a'], 'mistake_ids': [],
        'psychology_state_ids': ['ps_calm'], 'news_impact_ids': ['news_high'], 'rule_ids': ['rule_2'],
        'SN': Decimal('0.1'), 'EP': Decimal('0.85'), 'RRv': Decimal('0'), 'ES': Decimal('0'), 'RER': Decimal('1.0')
    },
    # Trade con dati mancanti o non validi
    {
        'id': '4', 'p_l': Decimal('100.0'), 'trade_risk': Decimal('0'), # Rischio non valido
        'duration_minutes': 10, 'exit_timestamp': datetime(2023, 1, 2, 11, 0),
        'playbook_id': 'pb_2', 'tag_ids': [], 'mistake_ids': [], 'psychology_state_ids': [],
        'news_impact_ids': [], 'rule_ids': []
    }
]

@pytest.fixture
def soa_service():
    return SOAService(mock_trades_data)

def test_preprocess_data(soa_service):
    df = soa_service.df
    assert isinstance(df, pd.DataFrame)
    # Dovrebbe filtrare il trade 4 con trade_risk = 0
    assert len(df) == 3
    assert 'DD' in df.columns
    # Verifica che i tipi Decimal siano stati convertiti in float
    assert df['p_l'].dtype == 'float64'
    assert df['SN'].dtype == 'float64'

def test_cluster_trades(soa_service):
    # Dati insufficienti per 5 cluster, K-Means dovrebbe comunque girare
    soa_service.cluster_trades(n_clusters=2)
    assert 'cluster_id' in soa_service.df.columns
    assert 'cluster_label' in soa_service.df.columns
    assert soa_service.df['cluster_label'].nunique() <= 2

def test_analyze_clusters_by_attribute(soa_service):
    soa_service.cluster_trades(n_clusters=2)
    # Analisi per Playbook (relazione 1-to-1)
    analysis = soa_service.analyze_clusters_by_attribute('playbook_id')
    assert isinstance(analysis, list)
    assert len(analysis) > 0
    assert 'probability' in analysis[0]

    # Analisi per Tag (relazione M-to-M, richiede explode)
    analysis_tags = soa_service.analyze_clusters_by_attribute('tag_ids', explode=True)
    assert isinstance(analysis_tags, list)
    assert len(analysis_tags) > 0 # Ci aspettiamo di vedere tag_a, tag_b, tag_c

def test_optimize_sl_tp(soa_service):
    optimization_results = soa_service.optimize_sl_tp()
    assert 'sl_optimal_p90' in optimization_results
    assert 'tp_optimal_median' in optimization_results
    # Con i dati di test, i trade vincenti sono il primo e il terzo
    df_win = soa_service.df[soa_service.df['p_l'] > 0]
    assert optimization_results['sl_optimal_p90'] == (df_win['mae_usd'] / df_win['trade_risk']).quantile(0.90)

def test_calculate_r_autocorrelation(soa_service):
    autocorr = soa_service.calculate_r_autocorrelation()
    # Con solo 3 punti dati, il calcolo potrebbe essere NaN, che dovrebbe essere gestito
    assert isinstance(autocorr, float)

def test_calculate_drawdown_zscore(soa_service):
    daily_balances = [
        {'date': datetime(2023, 1, 1).date(), 'balance': 1000},
        {'date': datetime(2023, 1, 2).date(), 'balance': 1100}, # Peak
        {'date': datetime(2023, 1, 3).date(), 'balance': 1050}, # Drawdown
        {'date': datetime(2023, 1, 4).date(), 'balance': 1020}  # Drawdown
    ]
    zscore_results = soa_service.calculate_drawdown_zscore(daily_balances)
    assert 'z_score' in zscore_results
    assert 'current_drawdown_usd' in zscore_results
    assert zscore_results['current_drawdown_usd'] < 0
