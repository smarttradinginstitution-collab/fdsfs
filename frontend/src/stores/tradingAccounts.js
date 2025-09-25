// =============================================================================
// FILE: src/stores/tradingAccounts.js
// DESCRIZIONE: Questo store Pinia gestisce lo stato dei Trading Accounts.
// Si occupa di caricare, creare e selezionare i conti di trading di un utente.
// =============================================================================

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import apiClient from '@/services/api';
import { useAuthStore } from './auth';

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
      const { data } = await apiClient.get('/api/v1/trading-accounts/');
      tradingAccounts.value = data;

      // Se non c'è un account selezionato o quello selezionato non è più valido,
      // seleziona il primo della lista.
      const isSelectedAccountValid = selectedTradingAccount.value && data.some(acc => acc.id === selectedTradingAccount.value.id);
      if (!isSelectedAccountValid && data.length > 0) {
        selectTradingAccount(data[0]);
      } else if (data.length === 0) {
        // Se non ci sono conti, pulisci la selezione
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
   * Imposta il conto di trading attivo.
   * @param {object | null} account - L'oggetto del conto da selezionare o null.
   */
  function selectTradingAccount(account) {
    selectedTradingAccount.value = account;
    if (account) {
      localStorage.setItem('selectedTradingAccount', JSON.stringify(account));
    } else {
      localStorage.removeItem('selectedTradingAccount');
    }
  }

  return {
    tradingAccounts,
    selectedTradingAccount,
    isLoading,
    hasTradingAccounts,
    fetchTradingAccounts,
    selectTradingAccount,
  };
});