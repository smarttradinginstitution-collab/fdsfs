// /app/frontend/src/stores/dashboardLayout.js

import { defineStore } from 'pinia';
import apiClient from '../services/api';
import { useAuthStore } from './auth';
import { useUiStore } from './uiStore';

export const useDashboardLayoutStore = defineStore('dashboardLayout', {
  state: () => ({
    layout: {
      stats: [],
      main: [],
      charts: [],
    },
    isLoading: false,
    defaultLayout: {
      stats: [
        { i: 'stats' }, // This will be a special component that renders multiple stat cards
      ],
      main: [
        { i: 'calendar' },
        { i: 'recentTrades' },
      ],
      charts: [
        { i: 'vantageScore' },
        { i: 'rrDistribution' },
        { i: 'cumulativePnl' },
      ],
    },
    // We can define which widgets are allowed in which zone
    widgetConfig: {
      stats: {
        max: 1, // Only one 'stats' group widget
        allowed: ['stats'],
      },
      main: {
        max: 2,
        allowed: ['calendar', 'recentTrades'],
      },
      charts: {
        max: 3,
        allowed: ['vantageScore', 'rrDistribution', 'cumulativePnl'],
      },
    },
  }),

  actions: {
    async fetchLayout() {
      this.isLoading = true;
      const authStore = useAuthStore();
      if (!authStore.user) {
        console.warn('User not authenticated. Cannot fetch layout. Using default.');
        this.layout = JSON.parse(JSON.stringify(this.defaultLayout));
        this.isLoading = false;
        return;
      }

      try {
        const response = await apiClient.get('/api/v1/dashboard/layout');
        // Ensure all zones exist, even if the saved layout is partial or old
        this.layout = {
          ...JSON.parse(JSON.stringify(this.defaultLayout)),
          ...response.data.layout,
        };
      } catch (error) {
        if (error.response && error.response.status === 404) {
          console.log('No saved layout found for user. Using default layout.');
          this.layout = JSON.parse(JSON.stringify(this.defaultLayout));
        } else {
          console.error('Error fetching dashboard layout:', error);
          console.log('Falling back to default layout due to error.');
          this.layout = JSON.parse(JSON.stringify(this.defaultLayout));
        }
      } finally {
        this.isLoading = false;
      }
    },

    addWidget({ zone, widgetId }) {
      const zoneConfig = this.widgetConfig[zone];
      if (!zoneConfig || this.layout[zone].length >= zoneConfig.max) {
        return; // Zone is full or invalid
      }
      if (!zoneConfig.allowed.includes(widgetId)) {
        return; // Widget not allowed in this zone
      }
      // Prevent duplicates in the same zone
      if (this.layout[zone].some(w => w.i === widgetId)) {
        return;
      }
      this.layout[zone].push({ i: widgetId });
      this.saveLayout();
    },

    removeWidget({ zone, widgetId }) {
      const zoneLayout = this.layout[zone];
      const index = zoneLayout.findIndex(w => w.i === widgetId);
      if (index !== -1) {
        zoneLayout.splice(index, 1);
        this.saveLayout();
      }
    },

    moveWidget({ zone, oldIndex, newIndex }) {
        const zoneLayout = this.layout[zone];
        const [removed] = zoneLayout.splice(oldIndex, 1);
        zoneLayout.splice(newIndex, 0, removed);
        this.saveLayout();
    },

    async saveLayout() {
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
