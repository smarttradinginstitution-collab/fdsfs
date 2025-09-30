import { defineStore } from 'pinia';
import { ref, watch } from 'vue';
import { useMediaQuery } from '@vueuse/core';
import breakpointTokens from '../../tokens/base/layout/breakpoint.json';

export const useUiStore = defineStore('ui', () => {

  // --- STATE ---
  const isSidebarCollapsed = ref(false);
  const isMobileMenuOpen = ref(false);
  const isLayoutEditing = ref(false);
  const isStatSelectorVisible = ref(false);
  const visibleStatKeys = ref(['netPnl', 'winRate', 'profitFactor', 'trades', 'avgWin', 'avgTradePnl', 'maxDrawdownAbs']);
  const isWeeklySummaryVisible = ref(true);
  const isCalendarTradeCountVisible = ref(true);
  const isCalendarWinRateVisible = ref(true);
  const notification = ref({ show: false, message: '', type: 'success' });
  const isDailySummaryModalOpen = ref(false);
  const isWeeklySummaryModalOpen = ref(false);
  const theme = ref('light');
  const isAppLoading = ref(false);
  const loaderMessage = ref('');
  const isInitialLoadPending = ref(false); // Nuovo stato

  // --- RESPONSIVE LOGIC ---
  const isMobile = useMediaQuery(`(max-width: ${breakpointTokens.base.layout.breakpoint.md.$value})`);
  watch(isMobile, (isNowMobile) => {
    if (!isNowMobile && isMobileMenuOpen.value) {
      closeMobileMenu();
    }
  });

  // --- ACTIONS ---
  function toggleStatSelector() { isStatSelectorVisible.value = !isStatSelectorVisible.value; }
  function closeStatSelector() { isStatSelectorVisible.value = false; }
  function toggleLayoutEditing() { isLayoutEditing.value = !isLayoutEditing.value; }
  function toggleWeeklySummary() { isWeeklySummaryVisible.value = !isWeeklySummaryVisible.value; }
  function toggleCalendarTradeCount() { isCalendarTradeCountVisible.value = !isCalendarTradeCountVisible.value; }
  function toggleCalendarWinRate() { isCalendarWinRateVisible.value = !isCalendarWinRateVisible.value; }
  function toggleSidebar() { if (!isMobile.value) { isSidebarCollapsed.value = !isSidebarCollapsed.value; } }
  function toggleMobileMenu() { isMobileMenuOpen.value = !isMobileMenuOpen.value; }
  function closeMobileMenu() { isMobileMenuOpen.value = false; }
  function toggleStatVisibility(key) {
    const index = visibleStatKeys.value.indexOf(key);
    if (index === -1) { visibleStatKeys.value.push(key); } else { visibleStatKeys.value.splice(index, 1); }
  }
  function moveStat({ oldIndex, newIndex }) {
    const [item] = visibleStatKeys.value.splice(oldIndex, 1);
    visibleStatKeys.value.splice(newIndex, 0, item);
  }
  function setVisibleStatKeys(keys) { if (Array.isArray(keys)) { visibleStatKeys.value = keys; } }

  // --- NOTIFICATION ACTIONS ---
  let notificationTimeout = null;
  function showNotification({ message, type = 'success' }) {
    if (notificationTimeout) clearTimeout(notificationTimeout);
    notification.value = { show: true, message, type };
    notificationTimeout = setTimeout(() => hideNotification(), 4000);
  }
  function hideNotification() { notification.value.show = false; }

  // --- MODAL ACTIONS ---
  let sidebarStateBeforeModal = false;
  function _openModal(modalStateRef) {
    modalStateRef.value = true;
    if (!isMobile.value) {
      sidebarStateBeforeModal = isSidebarCollapsed.value;
      isSidebarCollapsed.value = true;
    }
  }
  function _closeModal(modalStateRef) {
    modalStateRef.value = false;
    if (!isMobile.value) { isSidebarCollapsed.value = sidebarStateBeforeModal; }
  }
  function openDailySummaryModal() { _openModal(isDailySummaryModalOpen); }
  function closeDailySummaryModal() { _closeModal(isDailySummaryModalOpen); }
  function openWeeklySummaryModal() { _openModal(isWeeklySummaryModalOpen); }
  function closeWeeklySummaryModal() { _closeModal(isWeeklySummaryModalOpen); }

  // --- THEME MANAGEMENT ---
  function setTheme(newTheme) {
    theme.value = newTheme;
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
  }
  function toggleTheme() {
    const newTheme = theme.value === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
  }
  function initTheme() {
    const savedTheme = localStorage.getItem('theme');
    const userPrefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    if (savedTheme) { setTheme(savedTheme); } else if (userPrefersDark) { setTheme('dark'); } else { setTheme('light'); }
  }

  // --- GLOBAL LOADER ACTIONS ---
  function showLoader(message = '') {
    loaderMessage.value = message;
    isAppLoading.value = true;
  }
  function hideLoader() {
    isAppLoading.value = false;
    loaderMessage.value = '';
  }

  function setInitialLoadPending(status) {
    isInitialLoadPending.value = status;
  }

  // Initialize the theme when the store is created
  initTheme();

  // --- EXPORTS ---
  return {
    theme,
    toggleTheme,
    initTheme,
    isSidebarCollapsed,
    isMobileMenuOpen,
    isLayoutEditing,
    isMobile,
    visibleStatKeys,
    isWeeklySummaryVisible,
    isCalendarTradeCountVisible,
    isCalendarWinRateVisible,
    isDailySummaryModalOpen,
    isWeeklySummaryModalOpen,
    isStatSelectorVisible,
    isAppLoading,
    loaderMessage,
    isInitialLoadPending,
    showLoader,
    hideLoader,
    setInitialLoadPending,
    toggleStatSelector,
    closeStatSelector,
    toggleLayoutEditing,
    toggleSidebar,
    toggleMobileMenu,
    closeMobileMenu,
    toggleStatVisibility,
    moveStat,
    setVisibleStatKeys,
    toggleWeeklySummary,
    toggleCalendarTradeCount,
    toggleCalendarWinRate,
    openDailySummaryModal,
    closeDailySummaryModal,
    openWeeklySummaryModal,
    closeWeeklySummaryModal,
    notification,
    showNotification,
  };
});