// /app/frontend/src/stores/dashboardLayout.js

import { defineStore } from 'pinia';
import apiClient from '../services/api';
import { useAuthStore } from './auth';
import { useUiStore } from './uiStore';

// This store now only manages the layout for the 'complex' and 'main' widget zones.
// The 'stats' grid is managed directly in uiStore.
export const useDashboardLayoutStore = defineStore('dashboardLayout', {
  state: () => ({
    layout: {
      complex: [],
      main: [],
    },
    isLoading: false,
    defaultLayout: {
      complex: [
        { i: 'vantageScore' },
        { i: 'rrDistribution' },
        { i: 'cumulativePnl' },
      ],
      main: [
        { i: 'calendar' },
        { i: 'recentTrades' },
      ],
    },
    widgetConfig: {
      complex: {
        max: 3,
        allowed: ['vantageScore', 'rrDistribution', 'cumulativePnl'],
      },
      main: {
        max: 2,
        allowed: ['calendar', 'recentTrades'],
      },
    },
    availableWidgets: [
        { i: 'vantageScore', name: 'Vantage Score' },
        { i: 'rrDistribution', name: 'R:R Distribution' },
        { i: 'cumulativePnl', name: 'Cumulative P&L' },
        { i: 'calendar', name: 'Trading Calendar' },
        { i: 'recentTrades', name: 'Recent Trades' },
    ],
  }),

  actions: {
    async fetchLayout() {
      this.isLoading = true;
      const authStore = useAuthStore();
      if (!authStore.user) {
        this.layout = JSON.parse(JSON.stringify(this.defaultLayout));
        this.isLoading = false;
        return;
      }
      try {
        const response = await apiClient.get('/api/v1/dashboard/layout');
        const savedLayout = response.data.layout || {};
        this.layout = {
          complex: savedLayout.complex || this.defaultLayout.complex,
          main: savedLayout.main || this.defaultLayout.main,
        };
      } catch (error) {
        console.log('No saved layout found, using default.');
        this.layout = JSON.parse(JSON.stringify(this.defaultLayout));
      } finally {
        this.isLoading = false;
      }
    },

    addWidget({ zone, widgetId }) {
      const zoneConfig = this.widgetConfig[zone];
      if (!zoneConfig || this.layout[zone].length >= zoneConfig.max) return;
      if (!zoneConfig.allowed.includes(widgetId)) return;
      if (this.layout[zone].some(w => w.i === widgetId)) return;

      this.layout[zone].push({ i: widgetId });
      this.saveLayout();
    },

    removeWidget({ zone, widgetId }) {
      const zoneLayout = this.layout[zone];
      if (!zoneLayout) return;
      const index = zoneLayout.findIndex(w => w.i === widgetId);
      if (index !== -1) {
        zoneLayout.splice(index, 1);
        this.saveLayout();
      }
    },

    moveWidget({ zone, oldIndex, newIndex }) {
        const zoneLayout = this.layout[zone];
        if (!zoneLayout) return;
        const [removed] = zoneLayout.splice(oldIndex, 1);
        zoneLayout.splice(newIndex, 0, removed);
        this.saveLayout();
    },

    async saveLayout() {
      const authStore = useAuthStore();
      if (!authStore.user) return;
      const uiStore = useUiStore();

      // We need to merge this layout with the stats layout from uiStore
      // to create the complete layout object for the backend.
      const fullLayout = {
        stats: uiStore.visibleStatKeys.map(key => ({ i: key })),
        ...this.layout
      };

      try {
        await apiClient.put('/api/v1/dashboard/layout', { layout: fullLayout });
      } catch (error) {
        uiStore.showNotification({
          message: 'Failed to save dashboard layout.',
          type: 'error',
        });
      }
    },
  },
});
