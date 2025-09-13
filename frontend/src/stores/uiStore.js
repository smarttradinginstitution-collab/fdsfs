// =============================================================================
// FILE: stores/uiStore.js
// DESCRIZIONE: Questo store Pinia gestisce lo stato generale dell'interfaccia
// utente (UI) che non è legato a dati specifici di business (come i trade).
// Esempi includono lo stato di apertura/chiusura di modali, sidebar, etc.
// =============================================================================

import { defineStore } from 'pinia';
import { ref, watch } from 'vue';
import { useMediaQuery } from '@vueuse/core';
import breakpointTokens from '../../tokens/base/layout/breakpoint.json';

// Definiamo lo store usando la sintassi "Setup Store"
export const useUiStore = defineStore('ui', () => {

  // --- STATO (State) ---
  const isSidebarCollapsed = ref(false);
  const isMobileMenuOpen = ref(false);
  const visibleStatKeys = ref(['netPnl', 'winRate', 'profitFactor', 'trades', 'avgWin', 'avgTradePnl', 'maxDrawdownAbs']);
  const isWeeklySummaryVisible = ref(true);
  const isCalendarTradeCountVisible = ref(true);
  const isCalendarWinRateVisible = ref(true);

  // --- NOTIFICATION STATE ---
  const notification = ref({
    show: false,
    message: '',
    type: 'success', // 'success' or 'error'
  });

  // --- LOGICA RESPONSIVE ---
  const isMobile = useMediaQuery(`(max-width: ${breakpointTokens.base.layout.breakpoint.md.$value})`);

  watch(isMobile, (isNowMobile) => {
    if (!isNowMobile && isMobileMenuOpen.value) {
      closeMobileMenu();
    }
  });


  // --- AZIONI (Actions) ---

  function toggleWeeklySummary() {
    isWeeklySummaryVisible.value = !isWeeklySummaryVisible.value;
  }

  function toggleCalendarTradeCount() {
    isCalendarTradeCountVisible.value = !isCalendarTradeCountVisible.value;
  }

  function toggleCalendarWinRate() {
    isCalendarWinRateVisible.value = !isCalendarWinRateVisible.value;
  }

  function toggleSidebar() {
    if (!isMobile.value) {
      isSidebarCollapsed.value = !isSidebarCollapsed.value;
    }
  }

  function toggleMobileMenu() {
    isMobileMenuOpen.value = !isMobileMenuOpen.value;
  }

  function closeMobileMenu() {
    isMobileMenuOpen.value = false;
  }

  function toggleStatVisibility(key) {
    const index = visibleStatKeys.value.indexOf(key);
    if (index === -1) {
      visibleStatKeys.value.push(key);
    } else {
      visibleStatKeys.value.splice(index, 1);
    }
  }

  // --- NOTIFICATION ACTIONS ---
  let notificationTimeout = null;

  function showNotification({ message, type = 'success' }) {
    if (notificationTimeout) {
      clearTimeout(notificationTimeout);
    }
    notification.value = { show: true, message, type };
    notificationTimeout = setTimeout(() => {
      hideNotification();
    }, 4000);
  }

  function hideNotification() {
    notification.value.show = false;
  }


  // --- STATO E AZIONI PER I MODALI ---
  const isDailySummaryModalOpen = ref(false);
  const isWeeklySummaryModalOpen = ref(false);
  const isAddTradeModalOpen = ref(false);
  const isSettingsModalOpen = ref(false);

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
    if (!isMobile.value) {
      isSidebarCollapsed.value = sidebarStateBeforeModal;
    }
  }

  function openAddTradeModal() {
    _openModal(isAddTradeModalOpen);
  }

  function closeAddTradeModal() {
    _closeModal(isAddTradeModalOpen);
  }

  function openDailySummaryModal() {
    _openModal(isDailySummaryModalOpen);
  }

  function closeDailySummaryModal() {
    _closeModal(isDailySummaryModalOpen);
  }

  function openWeeklySummaryModal() {
    _openModal(isWeeklySummaryModalOpen);
  }

  function closeWeeklySummaryModal() {
    _closeModal(isWeeklySummaryModalOpen);
  }

  function openSettingsModal() {
    _openModal(isSettingsModalOpen);
  }

  function closeSettingsModal() {
    _closeModal(isSettingsModalOpen);
  }


  // --- ESPORTAZIONE ---
  return {
    isSidebarCollapsed,
    isMobileMenuOpen,
    isMobile,
    visibleStatKeys,
    isWeeklySummaryVisible,
    isCalendarTradeCountVisible,
    isCalendarWinRateVisible,
    isDailySummaryModalOpen,
    isWeeklySummaryModalOpen,
    isAddTradeModalOpen,
    isSettingsModalOpen,

    toggleSidebar,
    toggleMobileMenu,
    closeMobileMenu,
    toggleStatVisibility,
    toggleWeeklySummary,
    toggleCalendarTradeCount,
    toggleCalendarWinRate,
    openDailySummaryModal,
    closeDailySummaryModal,
    openWeeklySummaryModal,
    closeWeeklySummaryModal,
    openAddTradeModal,
    closeAddTradeModal,
    openSettingsModal,
    closeSettingsModal,

    // Notifications
    notification,
    showNotification,
  };
});
