import { defineStore } from 'pinia';
import apiClient from '../services/api';
import { useAuthStore } from './auth';

export const usePlaybookStore = defineStore('playbooks', {
  state: () => ({
    playbooks: [],
    isLoading: false,
    error: null,
  }),

  getters: {
    /**
     * Returns all playbooks, useful for selectors or lists.
     * @param {object} state - The current state.
     * @returns {Array} The list of playbooks.
     */
    allPlaybooks(state) {
      return state.playbooks;
    },
  },

  actions: {
    /**
     * Fetches the user's playbooks from the backend, including calculated stats.
     */
    async fetchPlaybooks() {
      const authStore = useAuthStore();
      if (!authStore.isAuthenticated) {
        console.log("User not authenticated. Skipping playbook fetch.");
        return;
      }

      this.isLoading = true;
      this.error = null;
      try {
        const response = await apiClient.get('/me/playbooks');
        // The backend now returns playbooks with a 'stats' object.
        // No special mapping is needed if the frontend can use the structure directly.
        this.playbooks = response.data;
      } catch (err) {
        console.error('Error fetching playbooks:', err);
        this.error = err.response?.data?.detail || 'An unexpected error occurred.';
        this.playbooks = []; // Reset on error
      } finally {
        this.isLoading = false;
      }
    },
  },
});