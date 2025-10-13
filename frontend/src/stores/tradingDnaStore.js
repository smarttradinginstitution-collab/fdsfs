import { ref, reactive } from 'vue';
import { defineStore } from 'pinia';
import apiClient from '../services/api';
import { useUiStore } from './uiStore';

export const useTradingDnaStore = defineStore('tradingDna', () => {
  // --- STATE ---
  const report = ref(null);
  const isLoading = ref(false);
  const error = ref(null);

  const filters = reactive({
    tag_ids: [],
    mistake_ids: [],
    psychology_state_ids: [],
    news_impact_ids: [],
  });

  // --- ACTIONS ---
  async function fetchTradingDnaReport() {
    isLoading.value = true;
    error.value = null;
    const uiStore = useUiStore();

    const params = new URLSearchParams();
    for (const key in filters) {
      if (filters[key] && filters[key].length > 0) {
        filters[key].forEach(id => params.append(key, id));
      }
    }
    const hasFilters = params.toString() !== '';

    if (!hasFilters) {
      const cachedReport = localStorage.getItem('tradingDnaReport');
      if (cachedReport) {
        try {
          report.value = JSON.parse(cachedReport);
          isLoading.value = false;
          console.log("Trading DNA report loaded from cache.");
          return;
        } catch (e) {
          console.error("Error parsing cached Trading DNA report:", e);
        }
      }
    }

    try {
      console.log("Fetching Trading DNA report from API...");
      const response = await apiClient.get('/reports/trading-dna', { params });
      report.value = response.data;
      if (!hasFilters) {
        localStorage.setItem('tradingDnaReport', JSON.stringify(response.data));
      }
    } catch (err) {
      console.error('Error fetching Trading DNA report:', err);
      const errorMessage = err.response?.data?.detail || 'An unexpected error occurred while fetching the report.';
      error.value = errorMessage;
      uiStore.showNotification({ message: errorMessage, type: 'error' });
      report.value = null;
      if (!hasFilters) {
        localStorage.removeItem('tradingDnaReport');
      }
    } finally {
      isLoading.value = false;
    }
  }

  function updateFilters(newFilters) {
    Object.assign(filters, newFilters);
    fetchTradingDnaReport();
  }

  // --- EXPORTS ---
  return {
    report,
    isLoading,
    error,
    filters,
    fetchTradingDnaReport,
    updateFilters,
  };
});