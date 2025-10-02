import { ref, computed } from 'vue';

// This composable manages the navigation list for trades.
export function useTradeNavigation() {
  const tradeIds = ref([]);
  const isLoading = ref(false);
  const error = ref(null);

  // Function to fetch a list of trade IDs for a given account and date range.
  const fetchTradeList = async (tradingAccountId, startDate, endDate) => {
    isLoading.value = true;
    error.value = null;
    try {
      // Build query parameters, filtering out null values
      const params = new URLSearchParams();
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);

      const response = await fetch(`/api/trades/by-trading-account/${tradingAccountId}?${params.toString()}`);

      if (!response.ok) {
        throw new Error('Failed to fetch trade list');
      }

      const trades = await response.json();
      // We only need the IDs for navigation
      tradeIds.value = trades.map(trade => trade.id);

    } catch (e) {
      console.error(e);
      error.value = e.message;
    } finally {
      isLoading.value = false;
    }
  };

  // Computeds to find the previous and next trade IDs
  const getNavigationIds = (currentTradeId) => {
    return computed(() => {
      const currentIndex = tradeIds.value.findIndex(id => id === currentTradeId);
      if (currentIndex === -1) {
        return { prevTradeId: null, nextTradeId: null };
      }

      const prevTradeId = currentIndex > 0 ? tradeIds.value[currentIndex - 1] : null;
      const nextTradeId = currentIndex < tradeIds.value.length - 1 ? tradeIds.value[currentIndex + 1] : null;

      return { prevTradeId, nextTradeId };
    });
  };

  return {
    isLoading,
    error,
    fetchTradeList,
    getNavigationIds,
  };
}