import { defineStore } from 'pinia';
import { ref } from 'vue';
import apiClient from '../services/api';
import { useTradingAccountsStore } from './tradingAccounts';
import { useFilterStore } from './filterStore';

export const useAnalyticsStore = defineStore('analytics', () => {
  // --- STATE ---
  const tagPerformanceStats = ref([]);
  const isLoading = ref(false);
  const error = ref(null);

  // --- ACTIONS ---
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
    isLoading.value = false;
    error.value = null;
  }

  // --- EXPORTS ---
  return {
    tagPerformanceStats,
    isLoading,
    error,
    fetchTagPerformanceStats,
    resetState,
  };
});