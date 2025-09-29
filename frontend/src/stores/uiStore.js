import { defineStore } from 'pinia';

export const useUiStore = defineStore('ui', {
  state: () => ({
    // For the sidebar and mobile menu
    isSidebarCollapsed: false,
    isMobileMenuOpen: false,

    // For the global loader
    isAppLoading: false,

    // For the toast notification system
    notification: {
      show: false,
      message: '',
      type: 'success',
    },

    // For the dashboard statistics panel
    dashboardVisibleStats: [
      'net_pnl',
      'win_rate',
      'profit_factor',
      'total_trades',
      'expectancy',
      'avg_r_multiple'
    ],
  }),

  actions: {
    // --- Sidebar and Menu Actions ---
    toggleSidebar() {
      this.isSidebarCollapsed = !this.isSidebarCollapsed;
    },
    openMobileMenu() {
      this.isMobileMenuOpen = true;
    },
    closeMobileMenu() {
      this.isMobileMenuOpen = false;
    },

    // --- Global Loader Actions ---
    showLoader() {
      this.isAppLoading = true;
    },
    hideLoader() {
      this.isAppLoading = false;
    },

    // --- Toast Notification Actions ---
    showToast({ message, type = 'success' }) {
      this.notification = { show: true, message, type };
      // Auto-hide after 5 seconds
      setTimeout(() => {
        this.hideToast();
      }, 5000);
    },
    hideToast() {
      this.notification.show = false;
    },

    // --- Dashboard Stats Actions ---
    setDashboardVisibleStats(stats) {
      this.dashboardVisibleStats = stats;
    },
  },
});