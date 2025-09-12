// /app/frontend/src/stores/dashboardLayout.js

import { defineStore } from 'pinia';
import apiClient from '../services/api';
import { useAuthStore } from './auth';

export const useDashboardLayoutStore = defineStore('dashboardLayout', {
  state: () => ({
    /**
     * The layout is an array of objects, where each object is a grid item.
     * The format is compatible with vue-grid-layout.
     * Example: { x: 0, y: 0, w: 2, h: 2, i: 'unique-id' }
     */
    layout: [],
    isLoading: false,
    /**
     * A default layout to be used when a user has no saved layout.
     * The `i` property is a unique identifier for each widget.
     */
    defaultLayout: [
      { x: 0, y: 0, w: 12, h: 2, i: 'stats' },
      { x: 0, y: 2, w: 4, h: 5, i: 'vantageScore' },
      { x: 4, y: 2, w: 4, h: 5, i: 'rrDistribution' },
      { x: 8, y: 2, w: 4, h: 5, i: 'cumulativePnl' },
      { x: 0, y: 7, w: 8, h: 7, i: 'calendar' },
      { x: 8, y: 7, w: 4, h: 7, i: 'recentTrades' },
    ],
  }),

  actions: {
    /**
     * Fetches the user's dashboard layout from the backend.
     * If no layout is found, it sets the layout to the default.
     */
    async fetchLayout() {
      this.isLoading = true;
      const authStore = useAuthStore();
      if (!authStore.user) {
        console.warn('User not authenticated. Cannot fetch layout. Using default.');
        this.layout = this.defaultLayout;
        this.isLoading = false;
        return;
      }

      try {
        const response = await apiClient.get('/api/v1/dashboard/layout');
        this.layout = response.data.layout;
      } catch (error) {
        if (error.response && error.response.status === 404) {
          console.log('No saved layout found for user. Using default layout.');
          this.layout = this.defaultLayout;
        } else {
          console.error('Error fetching dashboard layout:', error);
          console.log('Falling back to default layout due to error.');
          this.layout = this.defaultLayout;
        }
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Saves the user's current layout to the backend.
     */
    async saveLayout() {
      // This will be implemented in a future phase.
    },
  },
});
