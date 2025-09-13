// /app/frontend/src/stores/dashboardLayout.js

import { defineStore } from 'pinia';
import apiClient from '../services/api';
import { useAuthStore } from './auth';
import { useUiStore } from './uiStore';

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
    /**
     * A list of all available widgets that can be added to the dashboard.
     */
    availableWidgets: [
      { i: 'stats', name: 'Statistics Cards', w: 12, h: 2 },
      { i: 'vantageScore', name: 'Vantage Score', w: 4, h: 5 },
      { i: 'rrDistribution', name: 'R:R Distribution', w: 4, h: 5 },
      { i: 'cumulativePnl', name: 'Cumulative P&L', w: 4, h: 5 },
      { i: 'calendar', name: 'Trading Calendar', w: 8, h: 7 },
      { i: 'recentTrades', name: 'Recent Trades', w: 4, h: 7 },
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
    addWidget(widgetId, coordinates = null) {
      const widgetToAdd = this.availableWidgets.find(w => w.i === widgetId);
      if (!widgetToAdd || this.layout.some(w => w.i === widgetId)) {
        return; // Widget not found or already in layout
      }

      let newWidget;
      if (coordinates) {
        // We need to find an empty spot near the coordinates
        // For now, just place it at the coordinates.
        // The empty slot is 1x1, but the widget can be larger.
        // The grid layout will handle overlapping items if vertical-compact is true.
        newWidget = {
          ...widgetToAdd,
          x: coordinates.x,
          y: coordinates.y,
        };
      } else {
        // Find the bottom of the grid to place the new widget
        const y = Math.max(0, ...this.layout.map(w => w.y + w.h));
        newWidget = {
          ...widgetToAdd,
          x: 0, // Place at the left edge
          y: y,
        };
      }

      const newLayout = [...this.layout, newWidget];
      this.saveLayout(newLayout);
    },

    removeWidget(widgetId) {
      const newLayout = this.layout.filter(w => w.i !== widgetId);
      this.saveLayout(newLayout);
    },

    async saveLayout(newLayout) {
      this.layout = newLayout;

      const authStore = useAuthStore();
      if (!authStore.user) {
        console.error('User not authenticated, cannot save layout.');
        return;
      }

      const uiStore = useUiStore();

      try {
        await apiClient.put('/api/v1/dashboard/layout', { layout: this.layout });
      } catch (error) {
        console.error('Error saving dashboard layout:', error);
        uiStore.showNotification({
          message: 'Failed to save dashboard layout.',
          type: 'error',
        });
      }
    },
  },
});
