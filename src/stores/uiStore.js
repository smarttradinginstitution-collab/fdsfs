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
  // `isSidebarCollapsed` è un booleano che ci dice se la sidebar è collassata o meno.
  const isSidebarCollapsed = ref(false);

  // `isMobileMenuOpen` gestisce la visibilità della sidebar su mobile (come overlay)
  const isMobileMenuOpen = ref(false);

  // Usiamo @vueuse/core per reagire alla larghezza dello schermo,
  // usando il valore del token direttamente dal file JSON per coerenza.
  const isMobile = useMediaQuery(`(max-width: ${breakpointTokens.base.layout.breakpoint.md.$value})`);

  // Chiudiamo automaticamente il menu mobile se si passa a una visuale desktop
  watch(isMobile, (isNowMobile) => {
    if (!isNowMobile) {
      closeMobileMenu();
    }
  });

  // `visibleStatKeys` è un array che memorizza le chiavi delle statistiche
  // che l'utente ha scelto di visualizzare nella dashboard.
  // Impostiamo 5 valori di default per riempire la griglia.
  const visibleStatKeys = ref(['netPnl', 'winRate', 'profitFactor', 'trades', 'avgWin']);

  // Nuovo stato per la visibilità del riepilogo settimanale del calendario
  const isWeeklySummaryVisible = ref(true);

  // Nuovi stati per la visibilità dei dettagli nelle celle del calendario
  const isCalendarTradeCountVisible = ref(true);
  const isCalendarWinRateVisible = ref(true);


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

  // `toggleStatVisibility` aggiunge o rimuove una chiave dall'array delle statistiche visibili.
  function toggleStatVisibility(key) {
    const index = visibleStatKeys.value.indexOf(key);
    if (index === -1) {
      // Se la chiave non c'è, la aggiungiamo.
      visibleStatKeys.value.push(key);
    } else {
      // Se la chiave c'è già, la rimuoviamo.
      visibleStatKeys.value.splice(index, 1);
    }
  }

  // --- STATO E AZIONI PER IL MODALE DI RIEPILOGO GIORNALIERO ---
  const isDailySummaryModalOpen = ref(false);
  const selectedDate = ref(null);

  function openDailySummaryModal(date) {
    selectedDate.value = date;
    isDailySummaryModalOpen.value = true;
  }

  function closeDailySummaryModal() {
    isDailySummaryModalOpen.value = false;
    selectedDate.value = null;
  }

  // --- STATO E AZIONI PER IL MODALE DI RIEPILOGO SETTIMANALE ---
  const isWeeklySummaryModalOpen = ref(false);
  const selectedWeekIndex = ref(null);

  function openWeeklySummaryModal(weekIndex) {
    selectedWeekIndex.value = weekIndex;
    isWeeklySummaryModalOpen.value = true;
  }

  function closeWeeklySummaryModal() {
    isWeeklySummaryModalOpen.value = false;
    selectedWeekIndex.value = null;
  }


  // --- ESPORTAZIONE ---
  return {
    isSidebarCollapsed,
    toggleSidebar,
    isMobileMenuOpen,
    isMobile,
    toggleMobileMenu,
    closeMobileMenu,
    visibleStatKeys,
    toggleStatVisibility,
    isWeeklySummaryVisible,
    toggleWeeklySummary,
    isCalendarTradeCountVisible,
    toggleCalendarTradeCount,
    isCalendarWinRateVisible,
    toggleCalendarWinRate,

    // Esportazione per il modale giornaliero
    isDailySummaryModalOpen,
    selectedDate,
    openDailySummaryModal,
    closeDailySummaryModal,

    // Esportazione per il modale settimanale
    isWeeklySummaryModalOpen,
    selectedWeekIndex,
    openWeeklySummaryModal,
    closeWeeklySummaryModal,
  };
});
