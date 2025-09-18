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
      charts: [],
      main: [],
    },
    isLoading: false,
    originalLayout: null,
    originalStats: null,
    defaultLayout: {
      charts: [
        { i: 'vantageScore' },
        { i: 'rrDistribution' },
        { i: 'cumulativePnl' },
      ],
      // The 'main' zone is now structured as an array of columns.
      // Each column is an array of widgets.
      main: [
        [{ i: 'calendar' }], // Column 1
        [{ i: 'recentTrades' }, { i: 'vantageScore' }], // Column 2
      ],
    },
    widgetConfig: {
      charts: {
        max: 3,
        allowed: ['vantageScore', 'rrDistribution', 'cumulativePnl'],
      },
      main: {
        // TODO: The config for the main zone needs to be adapted for the new column structure.
        // For now, we increase max to allow more widgets in total.
        max: 4,
        allowed: ['calendar', 'recentTrades', 'vantageScore', 'rrDistribution', 'cumulativePnl'],
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

  getters: {
    isDirty(state) {
      if (!state.originalLayout || !state.originalStats) {
        return false; // Not in edit mode or no snapshot taken
      }
      const uiStore = useUiStore();
      const statsChanged = JSON.stringify(state.originalStats) !== JSON.stringify(uiStore.visibleStatKeys);
      const layoutChanged = JSON.stringify(state.originalLayout) !== JSON.stringify(state.layout);
      return statsChanged || layoutChanged;
    }
  },

  actions: {
    snapshotLayout() {
      const uiStore = useUiStore();
      this.originalLayout = JSON.parse(JSON.stringify(this.layout));
      this.originalStats = [...uiStore.visibleStatKeys];
    },
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
          charts: savedLayout.charts || this.defaultLayout.charts,
          main: savedLayout.main || this.defaultLayout.main,
        };

        // Also update the uiStore with the stats layout
        const uiStore = useUiStore();
        if (savedLayout.stats && Array.isArray(savedLayout.stats)) {
          const statKeys = savedLayout.stats.map(widget => widget.i);
          uiStore.setVisibleStatKeys(statKeys);
        }
      } catch (error) {
        console.log('No saved layout found, using default.');
        this.layout = JSON.parse(JSON.stringify(this.defaultLayout));
      } finally {
        this.isLoading = false;
      }
    },

    addWidget({ zone, widgetId, columnIndex }) {
      if (zone === 'main') {
        const column = this.layout.main[columnIndex];
        if (column) {
          // TODO: This doesn't check against a max number of items per column yet.
          // The widgetConfig would need to be refactored to support that.
          if (!column.some(w => w.i === widgetId)) {
            column.push({ i: widgetId });
          }
        }
        return;
      }

      const zoneConfig = this.widgetConfig[zone];
      if (!zoneConfig || this.layout[zone].length >= zoneConfig.max) return;
      if (!zoneConfig.allowed.includes(widgetId)) return;
      if (this.layout[zone].some(w => w.i === widgetId)) return;

      this.layout[zone].push({ i: widgetId });
    },

    removeWidget({ zone, widgetId, columnIndex, widgetIndex }) {
      if (zone === 'main') {
        const column = this.layout.main[columnIndex];
        if (column && column[widgetIndex] && column[widgetIndex].i === widgetId) {
          // Re-assigning with .filter() is more robust for reactivity
          this.layout.main[columnIndex] = column.filter((_, index) => index !== widgetIndex);
        }
        return;
      }

      const zoneLayout = this.layout[zone];
      if (!zoneLayout) return;
      // The old logic for flat layouts used findIndex, but for nested we receive the direct index.
      // The flat layout also passes widgetIndex now, which is the 'index' from the v-for.
      if (widgetIndex !== null && zoneLayout[widgetIndex]?.i === widgetId) {
         zoneLayout.splice(widgetIndex, 1);
      } else {
        // Fallback to searching if index is not reliable
        const index = zoneLayout.findIndex(w => w.i === widgetId);
        if (index !== -1) {
          zoneLayout.splice(index, 1);
        }
      }
    },

    moveWidget({ zone, fromColumnIndex, toColumnIndex, oldIndex, newIndex }) {
      if (zone === 'main') {
        const fromColumn = this.layout.main[fromColumnIndex];
        const toColumn = this.layout.main[toColumnIndex];

        if (fromColumn && toColumn) {
          const [widget] = fromColumn.splice(oldIndex, 1);
          toColumn.splice(newIndex, 0, widget);
        }
        return;
      }

      // Handle flat layouts
      const zoneLayout = this.layout[zone];
      if (!zoneLayout) return;
      const [removed] = zoneLayout.splice(oldIndex, 1);
      zoneLayout.splice(newIndex, 0, removed);
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
        uiStore.showNotification({
          message: 'Layout salvato con successo!',
          type: 'success',
        });
      } catch (error) {
        uiStore.showNotification({
          message: 'Failed to save dashboard layout.',
          type: 'error',
        });
      }
    },
  },
});
