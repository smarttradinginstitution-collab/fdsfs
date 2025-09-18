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
    activeLayoutId: 'custom', // 'custom' or a template ID like 'template-1'
    isLoading: false,
    originalLayout: null,
    originalStats: null,
    defaultLayout: {
      charts: [
        { i: 'vantageScore' },
        { i: 'rrDistribution' },
        { i: 'cumulativePnl' },
      ],
      main: [
        { i: 'calendar' },
        { i: 'recentTrades' },
      ],
    },
    templates: {
      'template-1': {
        name: 'Standard',
        layout: {
          // Based on a 12-column grid
          stats: [
            { i: 'netPnl', x: 0, y: 0, w: 3, h: 1 },
            { i: 'winRate', x: 3, y: 0, w: 3, h: 1 },
            { i: 'profitFactor', x: 6, y: 0, w: 3, h: 1 },
            { i: 'trades', x: 9, y: 0, w: 3, h: 1 },
          ],
          charts: [
            { i: 'cumulativePnl', x: 0, y: 0, w: 12, h: 1 },
          ],
          main: [
            { i: 'calendar', x: 0, y: 0, w: 8, h: 2 },
            { i: 'recentTrades', x: 8, y: 0, w: 4, h: 2 },
          ]
        }
      }
    },
    widgetConfig: {
      charts: {
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

  getters: {
    isTemplateActive(state) {
      return state.activeLayoutId !== 'custom';
    },
    activeLayout(state) {
      if (state.activeLayoutId !== 'custom' && state.templates[state.activeLayoutId]) {
        return state.templates[state.activeLayoutId].layout;
      }
      return state.layout;
    },
    isDirty(state) {
      // Layout is only considered "dirty" if we are in custom mode
      if (state.activeLayoutId !== 'custom' || !state.originalLayout || !state.originalStats) {
        return false; // Not in edit mode or no snapshot taken
      }
      const uiStore = useUiStore();
      const statsChanged = JSON.stringify(state.originalStats) !== JSON.stringify(uiStore.visibleStatKeys);
      const layoutChanged = JSON.stringify(state.originalLayout) !== JSON.stringify(state.layout);
      return statsChanged || layoutChanged;
    }
  },

  actions: {
    setActiveLayout(layoutId) {
      this.activeLayoutId = layoutId;
    },
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

    addWidget({ zone, widgetId }) {
      const zoneConfig = this.widgetConfig[zone];
      if (!zoneConfig || this.layout[zone].length >= zoneConfig.max) return;
      if (!zoneConfig.allowed.includes(widgetId)) return;
      if (this.layout[zone].some(w => w.i === widgetId)) return;

      this.layout[zone].push({ i: widgetId });
    },

    removeWidget({ zone, widgetId }) {
      const zoneLayout = this.layout[zone];
      if (!zoneLayout) return;
      const index = zoneLayout.findIndex(w => w.i === widgetId);
      if (index !== -1) {
        zoneLayout.splice(index, 1);
      }
    },

    moveWidget({ zone, oldIndex, newIndex }) {
        const zoneLayout = this.layout[zone];
        if (!zoneLayout) return;
        const [removed] = zoneLayout.splice(oldIndex, 1);
        zoneLayout.splice(newIndex, 0, removed);
    },

    async saveLayout() {
      // Do not save if a template is active, templates are read-only.
      if (this.activeLayoutId !== 'custom') return;

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
