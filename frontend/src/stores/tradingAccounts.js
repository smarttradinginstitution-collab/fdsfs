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
   * Richiede che l'utente sia autenticato.
   */
  async function fetchTradingAccounts() {
    const authStore = useAuthStore();
    if (!authStore.isAuthenticated) {
      console.log("Utente non autenticato, impossibile recuperare i trading accounts.");
      return;
    }

    isLoading.value = true;
    try {
      const { data } = await apiClient.get('/trading-accounts/');
      tradingAccounts.value = data;

      // Dopo aver caricato i conti, se ce ne sono di selezionati,
      // avvia il caricamento dei dati associati (es. trades).
      if (hasSelectedAccounts.value) {
        const tradesStore = useTradesStore();
        tradesStore.fetchAllDataForAccount();
      }

    } catch (error) {
      console.error("Errore nel recupero dei trading accounts:", error);
      tradingAccounts.value = [];
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Crea un nuovo conto di trading.
   * @param {object} accountData - I dati per il nuovo account (es. { label, broker_id }).
   */
  async function createTradingAccount(accountData) {
    const authStore = useAuthStore();
    if (!authStore.isAuthenticated) {
      throw new Error("Utente non autenticato.");
    }

    isLoading.value = true;
    try {
      const { data } = await apiClient.post('/trading-accounts/', accountData);
      // Aggiungi il nuovo account e ricarica la lista per avere lo stato aggiornato
      // dal backend (es. `is_selected` potrebbe essere true di default).
      await fetchTradingAccounts();
      return data;
    } catch (error) {
      console.error("Errore nella creazione del trading account:", error);
      throw error;
    } finally {
      isLoading.value = false;
    }
  }

  return {
    tradingAccounts,
    isLoading,
    hasTradingAccounts,
    selectedAccounts,
    hasSelectedAccounts,
    fetchTradingAccounts,
    createTradingAccount,
  };
}, {
  persist: true,
});