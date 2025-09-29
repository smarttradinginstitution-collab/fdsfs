import { defineStore } from 'pinia';

export const useUiStore = defineStore('ui', {
  state: () => ({
    isAppLoading: false,
  }),
  actions: {
    showLoader() {
      this.isAppLoading = true;
    },
    hideLoader() {
      this.isAppLoading = false;
    },
  },
});