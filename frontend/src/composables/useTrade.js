import { ref } from 'vue';
import { format, parseISO } from 'date-fns';

// Helper function to format date strings
const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = parseISO(dateString);
  return format(date, 'EEE, MMM dd, yyyy');
};

// This composable will manage the state and fetching of a single trade.
export function useTrade() {
  const trade = ref(null);
  const isLoading = ref(false);
  const error = ref(null);

  // Function to fetch a single trade by its ID from the backend.
  const fetchTrade = async (tradeId) => {
    isLoading.value = true;
    error.value = null;
    trade.value = null;

    try {
      // The '/api' prefix is assumed to be configured in the dev server (e.g., vite.config.js)
      // to proxy requests to the backend, avoiding CORS issues.
      const response = await fetch(`/api/trades/${tradeId}`);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Failed to fetch trade with status: ${response.status}`);
      }

      const rawData = await response.json();

      // We can format or process data here before setting the state
      trade.value = {
        ...rawData,
        // Create a formatted date string for display
        display_date: formatDate(rawData.timestamp),
      };

    } catch (e) {
      console.error(e);
      error.value = e.message;
    } finally {
      isLoading.value = false;
    }
  };

  // Function to update a trade's "reviewed" status.
  const markAsReviewed = async (tradeId) => {
    try {
      const response = await fetch(`/api/trades/${tradeId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ is_reviewed: true }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to mark as reviewed');
      }

      // If the update is successful, update the local state as well
      if (trade.value) {
        trade.value.is_reviewed = true;
      }

      return true;
    } catch (e) {
      console.error(e);
      // Optionally, set an error state to show in the UI
      return false;
    }
  };

  return {
    trade,
    isLoading,
    error,
    fetchTrade,
    markAsReviewed,
  };
}