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
  const isLayoutEditing = ref(false);
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
  /*
    BEST PRACTICE: Sincronizzazione JS e CSS tramite Token
    Per la logica responsiva in JavaScript (es. per sapere se siamo su mobile),
    è fondamentale usare la stessa identica soglia (breakpoint) del nostro CSS.
    Invece di scrivere un valore fisso (es. 768px), importiamo direttamente il
    file JSON dei token e usiamo il valore del breakpoint `md`.
    Questo garantisce che se un giorno modificheremo il token, la logica JS
    si aggiornerà automaticamente insieme al CSS.
  */
  const isMobile = useMediaQuery(`(max-width: ${breakpointTokens.base.layout.breakpoint.md.$value})`);

  // Chiudiamo automaticamente il menu mobile se l'utente allarga la finestra
  // passando dalla visuale mobile a quella desktop.
  watch(isMobile, (isNowMobile) => {
    if (!isNowMobile && isMobileMenuOpen.value) {
      closeMobileMenu();
    }
  });


  // --- AZIONI (Actions) ---

  function toggleLayoutEditing() {
    isLayoutEditing.value = !isLayoutEditing.value;
  }

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
    // La sidebar collassabile funziona solo su schermi grandi.
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

  function moveStat({ oldIndex, newIndex }) {
    const [item] = visibleStatKeys.value.splice(oldIndex, 1);
    visibleStatKeys.value.splice(newIndex, 0, item);
  }

  function setVisibleStatKeys(keys) {
    if (Array.isArray(keys)) {
      visibleStatKeys.value = keys;
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
    }, 4000); // Hide after 4 seconds
  }

  function hideNotification() {
    notification.value.show = false;
  }


  // --- STATO E AZIONI PER I MODALI ---
  const isDailySummaryModalOpen = ref(false);
  const isWeeklySummaryModalOpen = ref(false);
  const isAddTradeModalOpen = ref(false);

  // Salviamo lo stato della sidebar prima di aprire un modale
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


  // --- ESPORTAZIONE ---
  return {
    isSidebarCollapsed,
    isMobileMenuOpen,
    isLayoutEditing,
    isMobile, // Esportiamo lo stato reattivo
    visibleStatKeys,
    isWeeklySummaryVisible,
    isCalendarTradeCountVisible,
    isCalendarWinRateVisible,
    isDailySummaryModalOpen,
    isWeeklySummaryModalOpen,
    isAddTradeModalOpen,

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
    openAddTradeModal,
    closeAddTradeModal,

    // Notifications
    notification,
    showNotification,
  };
});
