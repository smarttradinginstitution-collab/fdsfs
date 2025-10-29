
import { defineStore } from 'pinia';
import { ref, computed } from 'vue'; // Aggiunto 'computed'
import apiClient from '../services/api';
import { useTradingAccountsStore } from './tradingAccounts';
import { useFilterStore } from './filterStore';

export const useAnalyticsStore = defineStore('analytics', () => {
  // --- STATE ---
  const soaAnalysisData = ref(null);
  const isSoaLoading = ref(false);
  const soaError = ref(null);

  // Per mantenere compatibilità con altri componenti se necessario
  const tagPerformanceStats = ref([]);
  const isLoading = ref(false);
  const error = ref(null);

  // --- GETTERS (come computed properties) ---
  /**
   * Alias per accedere ai dati SOA, per mantere coerenza con il codice
   * che lo utilizzava in precedenza.
   */
  const soaAnalysis = computed(() => soaAnalysisData.value);

  /**
   * Calcola e restituisce una lista ordinata di ID di cluster unici
   * presenti nei dati dell'analisi.
   * @returns {Array<string>} - Un array di ID di cluster unici e ordinati.
   */
  const uniqueClusters = computed(() => {
    if (!soaAnalysisData.value?.cluster_analysis?.trade_clusters) {
      return [];
    }
    const clusterIds = soaAnalysisData.value.cluster_analysis.trade_clusters.map(
      (tc) => tc.cluster_id
    );
    // Usiamo Set per ottenere valori unici e poi sort per ordinarli
    return [...new Set(clusterIds)].sort();
  });


  // --- ACTIONS ---
  async function fetchSoaAnalysis() {
    const tradingAccountsStore = useTradingAccountsStore();
    const selectedAccount = tradingAccountsStore.selectedTradingAccount;
    if (!selectedAccount) {
      soaAnalysisData.value = null;
      return;
    }

    const filterStore = useFilterStore();
    const params = {
      start_date: filterStore.startDate.toISOString().split('T')[0],
      end_date: filterStore.endDate.toISOString().split('T')[0],
    };

    isSoaLoading.value = true;
    soaError.value = null;
    try {
      const response = await apiClient.get(`/analytics/${selectedAccount.id}/soa`, { params });
      soaAnalysisData.value = response.data;
    } catch (err) {
      console.error('Error fetching SOA analysis:', err);
      soaError.value = err.response?.data?.detail || 'Failed to load SOA data.';
      soaAnalysisData.value = null; // Resetta i dati in caso di errore
    } finally {
      isSoaLoading.value = false;
    }
  }

  async function fetchTagPerformanceStats() {
    const tradingAccountsStore = useTradingAccountsStore();
    const selectedAccount = tradingAccountsStore.selectedTradingAccount;
    if (!selectedAccount) {
      tagPerformanceStats.value = [];
      return;
    }

    const filterStore = useFilterStore();
    const params = {
      start_date: filterStore.startDate.toISOString().split('T')[0],
      end_date: filterStore.endDate.toISOString().split('T')[0],
    };

    isLoading.value = true;
    error.value = null;
    try {
      const response = await apiClient.get(`/analytics/tags-performance/${selectedAccount.id}`, { params });
      tagPerformanceStats.value = response.data;
    } catch (err) {
      console.error('Error fetching tag performance stats:', err);
      error.value = err.response?.data?.detail || 'Failed to load tag performance data.';
      tagPerformanceStats.value = [];
    } finally {
      isLoading.value = false;
    }
  }

  function resetState() {
    tagPerformanceStats.value = [];
    soaAnalysisData.value = null;
    isLoading.value = false;
    isSoaLoading.value = false;
    error.value = null;
    soaError.value = null;
  }

  // --- EXPORTS ---
  return {
    // State
    tagPerformanceStats,
    soaAnalysisData, // Esponiamo il ref originale
    isLoading,
    isSoaLoading,
    error,
    soaError,
    // Getters
    soaAnalysis, // Alias
    uniqueClusters, // Nuovo getter
    // Actions
    fetchTagPerformanceStats,
    fetchSoaAnalysis,
    resetState,
  };
});
