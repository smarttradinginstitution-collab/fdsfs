// =============================================================================
// FILE: src/stores/tradingAccounts.js
// DESCRIZIONE: Questo store Pinia gestisce lo stato dei Trading Accounts.
// Si occupa di caricare, creare e selezionare i conti di trading di un utente.
// =============================================================================

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import apiClient from '@/services/api';
import { useAuthStore } from './auth';
import { useTradesStore } from './trades';

export const useTradingAccountsStore = defineStore('tradingAccounts', () => {
  // --- STATE ---
  const tradingAccounts = ref([]);
  const isLoading = ref(false);

  // --- GETTERS ---
  const hasTradingAccounts = computed(() => tradingAccounts.value.length > 0);
  const selectedAccounts = computed(() => tradingAccounts.value.filter(acc => acc.is_selected));
  const hasSelectedAccounts = computed(() => selectedAccounts.value.length > 0);

  // --- ACTIONS ---

  /**
   * Recupera i conti di trading dell'utente dal backend.
   * L'elenco include lo stato di selezione (is_selected).
   */
  async function fetchTradingAccounts() {
    const authStore = useAuthStore();
    if (!authStore.isAuthenticated) return;

    isLoading.value = true;
    try {
      const { data } = await apiClient.get('/trading-accounts/');
      tradingAccounts.value = data;
    } catch (error) {
      console.error("Errore nel recupero dei trading accounts:", error);
      tradingAccounts.value = [];
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Crea un nuovo conto di trading. Il backend imposta questo nuovo account come unico selezionato.
   * @param {object} accountData - Dati per il nuovo account (es. { label }).
   */
  async function createTradingAccount(accountData) {
    const authStore = useAuthStore();
    if (!authStore.isAuthenticated) throw new Error("Utente non autenticato.");

    isLoading.value = true;
    try {
      const { data: newAccount } = await apiClient.post('/trading-accounts/', accountData);
      // Dopo la creazione, ricarichiamo tutti gli account per ottenere lo stato di selezione aggiornato
      await fetchTradingAccounts();
      return newAccount;
    } catch (error) {
      console.error("Errore nella creazione del trading account:", error);
      throw error;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Aggiorna la selezione dei conti di trading sul backend.
   * @param {string[]} selectedIds - Un array di ID dei conti da impostare come selezionati.
   */
  async function updateAccountSelection(selectedIds) {
    const authStore = useAuthStore();
    if (!authStore.isAuthenticated) throw new Error("Utente non autenticato.");

    try {
      // API per aggiornare in blocco la selezione
      await apiClient.put('/me/trading-accounts/selection', {
        trading_account_ids: selectedIds
      });

      // Aggiorna lo stato locale per riflettere immediatamente la selezione
      tradingAccounts.value = tradingAccounts.value.map(account => ({
        ...account,
        is_selected: selectedIds.includes(account.id),
      }));

      // Avvia il caricamento dei dati per i nuovi account selezionati
      const tradesStore = useTradesStore();
      if (selectedIds.length > 0) {
        tradesStore.fetchAllDataForDashboard();
      } else {
        tradesStore.$reset(); // Se nessun account è selezionato, pulisce i dati
      }

    } catch (error) {
      console.error("Errore nell'aggiornamento della selezione degli account:", error);
      throw error;
    }
  }

  /**
   * Resetta lo stato dello store.
   */
  function resetState() {
    tradingAccounts.value = [];
    isLoading.value = false;
  }

  return {
    // State
    tradingAccounts,
    isLoading,
    // Getters
    hasTradingAccounts,
    selectedAccounts,
    hasSelectedAccounts,
    // Actions
    fetchTradingAccounts,
    createTradingAccount,
    updateAccountSelection,
    resetState,
  };
});