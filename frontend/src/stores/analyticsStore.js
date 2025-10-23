import { defineStore } from 'pinia';
import { ref } from 'vue';
import apiClient from '../services/api';
import { useTradingAccountsStore } from './tradingAccounts';
import { useFilterStore } from './filterStore';

export const useAnalyticsStore = defineStore('analytics', () => {
  // --- STATE ---
  const tagPerformanceStats = ref([]);
  const soaAnalysisData = ref(null); // Nuovo stato per i dati SOA
  const isLoading = ref(false);
  const isSoaLoading = ref(false); // Stato di caricamento specifico per SOA
  const error = ref(null);
  const soaError = ref(null); // Errore specifico per SOA

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
      soaAnalysisData.value = null;
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

  // Funzione per resettare lo stato
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
    tagPerformanceStats,
    soaAnalysisData,
    isLoading,
    isSoaLoading,
    error,
    soaError,
    fetchTagPerformanceStats,
    fetchSoaAnalysis,
    resetState,
  };
});