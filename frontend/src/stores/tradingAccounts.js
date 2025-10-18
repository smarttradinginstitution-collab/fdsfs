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
  const selectedTradingAccount = ref(JSON.parse(localStorage.getItem('selectedTradingAccount')) || null);
  const isLoading = ref(false);

  // --- GETTERS ---
  const hasTradingAccounts = computed(() => tradingAccounts.value.length > 0);

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

      const isSelectedAccountValid = selectedTradingAccount.value && data.some(acc => acc.id === selectedTradingAccount.value.id);

      if (isSelectedAccountValid) {
        const fullAccount = data.find(acc => acc.id === selectedTradingAccount.value.id);
        selectTradingAccount(fullAccount);
      } else {
        selectTradingAccount(null);
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
      tradingAccounts.value.push(data);
      selectTradingAccount(data);
      return data;
    } catch (error) {
      console.error("Errore nella creazione del trading account:", error);
      throw error;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Imposta il conto di trading attivo.
   * @param {object | null} account - L'oggetto del conto da selezionare o null.
   */
  function selectTradingAccount(account) {
    selectedTradingAccount.value = account;

    if (account) {
      localStorage.setItem('selectedTradingAccount', JSON.stringify(account));
      // Il caricamento dei dati è ora gestito dal watcher in DashboardView.
    } else {
      localStorage.removeItem('selectedTradingAccount');
      const tradesStore = useTradesStore();
      // Resetta lo store dei trade se nessun account è selezionato.
      tradesStore.$reset();
    }
  }

  return {
    tradingAccounts,
    selectedTradingAccount,
    isLoading,
    hasTradingAccounts,
    fetchTradingAccounts,
    createTradingAccount,
    selectTradingAccount,
  };
});