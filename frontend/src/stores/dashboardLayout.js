// =============================================================================
// FILE: src/stores/dashboardLayout.js
// DESCRIZIONE: Questo store Pinia gestisce lo stato del layout della dashboard
// personalizzabile. Si occupa di caricare, salvare e modificare la
// disposizione dei widget.
// =============================================================================

import { defineStore } from 'pinia';
import { ref } from 'vue';
import apiClient from '@/services/api';

export const useDashboardLayoutStore = defineStore('dashboardLayout', () => {
  // --- STATE ---
  const layout = ref([]);
  const isLoading = ref(false);
  const error = ref(null);

  // --- ACTIONS ---
  /**
   * Carica il layout della dashboard per un utente specifico dal backend.
   * @param {string} userId - L'ID dell'utente.
   */
  async function fetchLayout(userId) {
    if (!userId) {
      error.value = 'User ID is required to fetch the layout.';
      return;
    }
    isLoading.value = true;
    error.value = null;
    try {
      const response = await apiClient.get('/api/v1/dashboard/layout', {
        params: { user_id: userId }
      });
      // The API returns the full layout object, we just need the 'layout' array
      if (response.data && response.data.layout) {
        layout.value = response.data.layout;
      } else {
        // Handle cases where the response might be malformed or empty
        layout.value = [];
      }
    } catch (err) {
      console.error('Error fetching dashboard layout:', err);
      error.value = 'Failed to fetch dashboard layout.';
      // In case of error, maybe set a default or empty layout
      layout.value = [];
    } finally {
      isLoading.value = false;
    }
  }

  // --- EXPORT ---
  return {
    layout,
    isLoading,
    error,
    fetchLayout,
  };
});