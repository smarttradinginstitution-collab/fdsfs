import { defineStore } from 'pinia';
import { predefinedLayouts } from '../config/dashboardLayouts';

export const useDashboardLayoutStore = defineStore('dashboardLayoutStore', {
  state: () => ({
    // Initialize from localStorage or default to the first predefined layout
    currentLayoutId: localStorage.getItem('dashboardLayoutId') || predefinedLayouts[0].id,
  }),
  getters: {
    // Returns the full layout object for the current ID
    selectedLayout(state) {
      return predefinedLayouts.find(layout => layout.id === state.currentLayoutId) || predefinedLayouts[0];
    },
    // Returns just the widgets array for the vue-grid-layout component
    layout(state) {
      const layout = predefinedLayouts.find(layout => layout.id === state.currentLayoutId);
      return layout ? layout.widgets : predefinedLayouts[0].widgets;
    },
    // Expose all available layouts for the selector component
    availableLayouts: () => predefinedLayouts,
  },
  actions: {
    selectLayout(layoutId) {
      const layoutExists = predefinedLayouts.some(layout => layout.id === layoutId);
      if (layoutExists) {
        this.currentLayoutId = layoutId;
        localStorage.setItem('dashboardLayoutId', layoutId);
      } else {
        console.error(`Layout with id "${layoutId}" not found.`);
      }
    },
  },
});
