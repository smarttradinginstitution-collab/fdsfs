// /app/frontend/src/stores/dashboardLayout.js

import { defineStore } from 'pinia';
import apiClient from '../services/api';
import { useAuthStore } from './auth';
import { useUiStore } from './uiStore';

// The 'stats' grid is managed directly in uiStore.
export const useDashboardLayoutStore = defineStore('dashboardLayout', {
  state: () => ({
    selectedLayoutId: 'layout_a',
    layoutTemplates: {
      layout_a: {
        name: 'Layout Standard',
        cssClass: 'layout-standard',
        slots: [
          { id: 'charts', name: 'Grafici', max: 3, allowed: ['vantageScore', 'rrDistribution', 'cumulativePnl'] },
          { id: 'main', name: 'Contenuto Principale', max: 2, allowed: ['calendar', 'recentTrades'] },
          { id: 'secondary_charts', name: 'Grafici Secondari', max: 2, allowed: ['vantageScore', 'rrDistribution', 'cumulativePnl'] },
        ],
      },
      layout_b: {
        name: 'Layout Complesso',
        cssClass: 'layout-complex',
        slots: [
          { id: 'stats1', name: 'Stat 1', max: 1, allowed: ['vantageScore'] }, // Example, should be a real stat widget
          { id: 'stats2', name: 'Stat 2', max: 1, allowed: ['rrDistribution'] },
          { id: 'stats3', name: 'Stat 3', max: 1, allowed: ['cumulativePnl'] },
          { id: 'stats4', name: 'Stat 4', max: 1, allowed: ['vantageScore'] },
          { id: 'chart_v1', name: 'Grafico Verticale 1', max: 1, allowed: ['vantageScore', 'rrDistribution', 'cumulativePnl'] },
          { id: 'chart_v2', name: 'Grafico Verticale 2', max: 1, allowed: ['vantageScore', 'rrDistribution', 'cumulativePnl'] },
          { id: 'calendar_large', name: 'Calendario Grande', max: 1, allowed: ['calendar'] },
          { id: 'chart_h1', name: 'Grafico Orizzontale 1', max: 1, allowed: ['vantageScore', 'rrDistribution', 'cumulativePnl'] },
          { id: 'chart_h2', name: 'Grafico Orizzontale 2', max: 1, allowed: ['vantageScore', 'rrDistribution', 'cumulativePnl'] },
          { id: 'chart_h3', name: 'Grafico Orizzontale 3', max: 1, allowed: ['vantageScore', 'rrDistribution', 'cumulativePnl'] },
        ],
      },
    },
    layoutData: {
      layout_a: {
        charts: [{ i: 'vantageScore' }, { i: 'rrDistribution' }, { i: 'cumulativePnl' }],
        main: [{ i: 'calendar' }, { i: 'recentTrades' }],
        secondary_charts: [],
      },
      layout_b: {
        stats1: [], stats2: [], stats3: [], stats4: [],
        chart_v1: [{ i: 'vantageScore' }],
        chart_v2: [{ i: 'rrDistribution' }],
        calendar_large: [{ i: 'calendar' }],
        chart_h1: [{ i: 'cumulativePnl' }],
        chart_h2: [],
        chart_h3: [],
      },
    },
    isLoading: false,
    originalLayoutData: null,
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
    currentLayoutTemplate(state) {
      return state.layoutTemplates[state.selectedLayoutId];
    },
    currentLayoutData(state) {
      return state.layoutData[state.selectedLayoutId];
    },
    isDirty(state) {
      if (!state.originalLayoutData) return false;
      const uiStore = useUiStore();
      const statsChanged = JSON.stringify(state.originalStats) !== JSON.stringify(uiStore.visibleStatKeys);
      const layoutChanged = JSON.stringify(state.originalLayoutData) !== JSON.stringify(state.layoutData);
      return statsChanged || layoutChanged;
    },
  },

  actions: {
    selectLayout(layoutId) {
      if (this.layoutTemplates[layoutId]) {
        this.selectedLayoutId = layoutId;
      }
    },
    snapshotLayout() {
      const uiStore = useUiStore();
      this.originalLayoutData = JSON.parse(JSON.stringify(this.layoutData));
      this.originalStats = [...uiStore.visibleStatKeys];
    },
    async fetchLayout() {
      this.isLoading = true;
      const authStore = useAuthStore();
      if (!authStore.user) {
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
          // Merge saved data with default data to ensure all layouts have some data
          this.layoutData = { ...this.layoutData, ...savedData.layoutData };
        }

        const uiStore = useUiStore();
        if (savedData.stats && Array.isArray(savedData.stats)) {
          uiStore.setVisibleStatKeys(savedData.stats.map(widget => widget.i));
        }
      } catch (error) {
        console.error('Failed to fetch layout, using default.', error);
      } finally {
        this.isLoading = false;
      }
    },
    addWidget({ slotId, widgetId }) {
      const slot = this.currentLayoutTemplate.slots.find(s => s.id === slotId);
      const slotData = this.currentLayoutData[slotId];
      if (!slot || !slotData) return;

      if (slotData.length >= slot.max) return;
      if (!slot.allowed.includes(widgetId)) return;
      if (slotData.some(w => w.i === widgetId)) return;

      slotData.push({ i: widgetId });
    },
    removeWidget({ slotId, widgetId }) {
      const slotData = this.currentLayoutData[slotId];
      if (!slotData) return;
      const index = slotData.findIndex(w => w.i === widgetId);
      if (index !== -1) {
        slotData.splice(index, 1);
      }
    },
    moveWidget({ slotId, oldIndex, newIndex }) {
      const slotData = this.currentLayoutData[slotId];
      if (!slotData) return;
      const [removed] = slotData.splice(oldIndex, 1);
      slotData.splice(newIndex, 0, removed);
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
        this.originalLayoutData = JSON.parse(JSON.stringify(this.layoutData));
      } catch (error) {
        uiStore.showNotification({
          message: 'Failed to save dashboard layout.',
          type: 'error',
        });
      }
    },
  },
});
