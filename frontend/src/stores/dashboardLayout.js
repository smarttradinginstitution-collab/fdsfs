import { defineStore } from 'pinia';
import apiClient from '../services/api';
import { useAuthStore } from './auth';

export const useDashboardLayoutStore = defineStore('dashboardLayout', {
  state: () => ({
    /**
     * The layout configuration for the dashboard widgets.
     * Each object in the array represents a widget and its position/size.
     * Example: [{ i: 'widgetId', x: 0, y: 0, w: 2, h: 2 }]
     */
    layout: [],
    isLoading: false,
    error: null,
  }),
  actions: {
    /**
     * Fetches the user's saved dashboard layout from the backend.
     * If the backend returns a default layout (because none is saved),
     * it will be used to populate the state.
     */
    async fetchLayout() {
      this.isLoading = true;
      this.error = null;
      const authStore = useAuthStore();
      if (!authStore.isAuthenticated) {
        this.error = 'User not authenticated.';
        this.isLoading = false;
        console.warn('fetchLayout called without an authenticated user.');
        return;
      }

      try {
        const response = await apiClient.get('/api/v1/users/me/dashboard-layout');
        if (response.data && response.data.layout_config) {
          this.layout = response.data.layout_config;
        } else {
          // Fallback to an empty array if the response is not as expected
          this.layout = [];
        }
      } catch (error) {
        console.error('Error fetching dashboard layout:', error);
        this.error = 'Failed to fetch dashboard layout.';
        // In case of error (e.g., network issue, 500), clear the layout
        this.layout = [];
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Saves the user's current dashboard layout to the backend.
     * @param {Array} newLayout - The new layout configuration array to save.
     */
    async saveLayout(newLayout) {
      // Update the local state immediately for a responsive UI
      this.layout = newLayout;

      this.isLoading = true;
      this.error = null;
      const authStore = useAuthStore();
      if (!authStore.isAuthenticated) {
        this.error = 'User not authenticated.';
        this.isLoading = false;
        console.warn('saveLayout called without an authenticated user.');
        return;
      }

      try {
        const payload = { layout_config: newLayout };
        // The API will return the saved layout, which we can use to update state again
        // ensuring consistency with the database.
        const response = await apiClient.put('/api/v1/users/me/dashboard-layout', payload);
        this.layout = response.data.layout_config;
      } catch (error) {
        console.error('Error saving dashboard layout:', error);
        this.error = 'Failed to save dashboard layout. Layout changes may not be persisted.';
        // Optionally, you could implement a rollback mechanism here if the save fails
      } finally {
        this.isLoading = false;
      }
    },
  },
});
