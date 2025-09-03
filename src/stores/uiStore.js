// =============================================================================
// FILE: stores/uiStore.js
// DESCRIZIONE: Questo store Pinia gestisce lo stato generale dell'interfaccia
// utente (UI) che non è legato a dati specifici di business (come i trade).
// Esempi includono lo stato di apertura/chiusura di modali, sidebar, etc.
// =============================================================================

import { defineStore } from 'pinia';
import { ref } from 'vue';

// Definiamo lo store usando la sintassi "Setup Store"
export const useUiStore = defineStore('ui', () => {

  // --- STATO (State) ---
  // `isSidebarCollapsed` è un booleano che ci dice se la sidebar è collassata o meno.
  const isSidebarCollapsed = ref(false);

  // `isMobileMenuOpen` gestisce la visibilità della sidebar su mobile (come overlay)
  const isMobileMenuOpen = ref(false);

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
    isSidebarCollapsed.value = !isSidebarCollapsed.value;
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

  // --- ESPORTAZIONE ---
  return {
    isSidebarCollapsed,
    toggleSidebar,
    isMobileMenuOpen,
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
  };
});
