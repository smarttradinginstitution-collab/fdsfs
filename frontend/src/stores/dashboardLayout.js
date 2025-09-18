// /app/frontend/src/stores/dashboardLayout.js

import { defineStore } from 'pinia';
import apiClient from '../services/api';
import { useAuthStore } from './auth';
import { useUiStore } from './uiStore';

// This store now only manages the layout for the 'complex' and 'main' widget zones.
// The 'stats' grid is managed directly in uiStore.
export const useDashboardLayoutStore = defineStore('dashboardLayout', {
  state: () => ({
    selectedLayoutId: 'default',
    layoutTemplates: {
      default: {
        name: 'Layout Predefinito',
        cssClass: 'layout-default',
        zones: {
          charts: {
            max: 3,
            allowed: ['vantageScore', 'rrDistribution', 'cumulativePnl'],
          },
          main: {
            max: 2,
            allowed: ['calendar', 'recentTrades'],
          },
        },
      },
      'focus-principale': {
        name: 'Focus Principale',
        cssClass: 'layout-focus-principale',
        zones: {
          charts_a: {
            name: 'Grafici Principali',
            max: 3,
            allowed: ['vantageScore', 'rrDistribution', 'cumulativePnl'],
          },
          main_content: {
            name: 'Contenuto Principale',
            max: 2,
            allowed: ['calendar', 'recentTrades'],
          },
          charts_b: {
            name: 'Grafici Secondari',
            max: 2,
            allowed: ['vantageScore', 'rrDistribution', 'cumulativePnl'],
          },
        },
      },
    },
    layoutData: {
      default: {
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
      'focus-principale': {
        charts_a: [
            { i: 'cumulativePnl' },
        ],
        main_content: [
            { i: 'calendar' },
            { i: 'recentTrades' },
        ],
        charts_b: [],
      },
    },
    isLoading: false,
    originalLayout: null,
    originalStats: null,
    availableWidgets: [
        { i: 'vantageScore', name: 'Vantage Score' },
        { i: 'rrDistribution', name: 'R:R Distribution' },
        { i: 'cumulativePnl', name: 'Cumulative P&L' },
        { i: 'calendar', name: 'Trading Calendar' },
        { i: 'recentTrades', name: 'Recent Trades' },
    ],
  }),

  getters: {
    layout(state) {
      return state.layoutData[state.selectedLayoutId];
    },
    currentLayoutTemplate(state) {
      return state.layoutTemplates[state.selectedLayoutId];
    },
    isDirty(state) {
      if (!state.originalLayout || !state.originalStats) {
        return false; // Not in edit mode or no snapshot taken
      }
      const uiStore = useUiStore();
      const statsChanged = JSON.stringify(state.originalStats) !== JSON.stringify(uiStore.visibleStatKeys);
      // Use the 'layout' getter to ensure we're comparing the correct layout data
      const layoutChanged = JSON.stringify(state.originalLayout) !== JSON.stringify(this.layout);
      return statsChanged || layoutChanged;
    }
  },

  actions: {
    selectLayout(layoutId) {
      if (this.layoutTemplates[layoutId]) {
        this.selectedLayoutId = layoutId;
      }
    },
    snapshotLayout() {
      const uiStore = useUiStore();
      // The 'layout' getter provides the data for the currently selected layout
      this.originalLayout = JSON.parse(JSON.stringify(this.layout));
      this.originalStats = [...uiStore.visibleStatKeys];
    },
    async fetchLayout() {
      this.isLoading = true;
      const authStore = useAuthStore();
      if (!authStore.user) {
        // No user, no need to do anything, state is already default
        this.isLoading = false;
        return;
      }
      try {
        const response = await apiClient.get('/api/v1/dashboard/layout');
        const savedData = response.data.layout || {};

        if (savedData.selectedLayoutId && this.layoutTemplates[savedData.selectedLayoutId]) {
          this.selectedLayoutId = savedData.selectedLayoutId;
        }

        if (savedData.layoutData) {
          this.layoutData = { ...this.layoutData, ...savedData.layoutData };
        }

        const uiStore = useUiStore();
        if (savedData.stats && Array.isArray(savedData.stats)) {
          const statKeys = savedData.stats.map(widget => widget.i);
          uiStore.setVisibleStatKeys(statKeys);
        }
      } catch (error) {
        console.log('No saved layout found or error, using default state.');
        // State is already defaulted, so we just log the error.
      } finally {
        this.isLoading = false;
      }
    },

    addWidget({ zone, widgetId }) {
      const zoneConfig = this.currentLayoutTemplate.zones[zone];
      const zoneData = this.layout[zone];

      if (!zoneConfig || !zoneData || zoneData.length >= zoneConfig.max) return;
      if (!zoneConfig.allowed.includes(widgetId)) return;
      if (zoneData.some(w => w.i === widgetId)) return;

      zoneData.push({ i: widgetId });
    },

    removeWidget({ zone, widgetId }) {
      const zoneData = this.layout[zone];
      if (!zoneData) return;
      const index = zoneData.findIndex(w => w.i === widgetId);
      if (index !== -1) {
        zoneData.splice(index, 1);
      }
    },

    moveWidget({ zone, oldIndex, newIndex }) {
        const zoneData = this.layout[zone];
        if (!zoneData) return;
        const [removed] = zoneData.splice(oldIndex, 1);
        zoneData.splice(newIndex, 0, removed);
    },

    async saveLayout() {
      const authStore = useAuthStore();
      if (!authStore.user) return;
      const uiStore = useUiStore();

      const fullLayout = {
        selectedLayoutId: this.selectedLayoutId,
        layoutData: this.layoutData,
        stats: uiStore.visibleStatKeys.map(key => ({ i: key })),
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
