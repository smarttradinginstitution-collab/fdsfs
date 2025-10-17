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
  const selectedTradingAccountIds = ref([]); // Da singolo oggetto a array di ID
  const isLoading = ref(false);

  // --- GETTERS ---
  const hasTradingAccounts = computed(() => tradingAccounts.value.length > 0);
  const selectedTradingAccounts = computed(() => {
    return tradingAccounts.value.filter(acc => selectedTradingAccountIds.value.includes(acc.id));
  });

  // --- ACTIONS ---

  /**
   * Recupera i conti di trading dell'utente e imposta la selezione iniziale.
   */
  async function fetchTradingAccounts() {
    const authStore = useAuthStore();
    if (!authStore.isAuthenticated) return;

    isLoading.value = true;
    try {
      const { data } = await apiClient.get('/trading-accounts/');
      tradingAccounts.value = data;

      // Imposta gli ID degli account selezionati basandosi sul flag `is_selected`
      const preSelectedIds = data
        .filter(acc => acc.is_selected)
        .map(acc => acc.id);

      selectedTradingAccountIds.value = preSelectedIds;

      // Se ci sono account selezionati, avvia il caricamento dei dati
      if (preSelectedIds.length > 0) {
        const tradesStore = useTradesStore();
        tradesStore.fetchAllDataForAccount();
      }

    } catch (error) {
      console.error("Errore nel recupero dei trading accounts:", error);
      tradingAccounts.value = [];
      selectedTradingAccountIds.value = [];
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Crea un nuovo conto di trading.
   * @param {object} accountData - I dati per il nuovo account.
   */
  async function createTradingAccount(accountData) {
    const authStore = useAuthStore();
    if (!authStore.isAuthenticated) throw new Error("Utente non autenticato.");

    isLoading.value = true;
    try {
      const { data } = await apiClient.post('/trading-accounts/', accountData);
      tradingAccounts.value.push(data);
      // Dopo la creazione, potremmo voler aggiornare la selezione per includere il nuovo account
      const newSelection = [...selectedTradingAccountIds.value, data.id];
      await updateAccountSelection(newSelection);
      return data;
    } catch (error) {
      console.error("Errore nella creazione del trading account:", error);
      throw error;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Aggiorna la selezione degli account sia sul backend che nello store.
   * @param {string[]} accountIds - Array di ID degli account da selezionare.
   */
  async function updateAccountSelection(accountIds) {
    try {
      await apiClient.put('/me/trading-accounts/selection', { trading_account_ids: accountIds });
      selectedTradingAccountIds.value = accountIds;

      // Ricarica i dati per la nuova selezione
      const tradesStore = useTradesStore();
      if (accountIds.length > 0) {
        tradesStore.fetchAllDataForAccount();
      } else {
        tradesStore.$reset(); // Pulisce i dati se nessun account è selezionato
      }
    } catch (error) {
      console.error("Errore nell'aggiornamento della selezione degli account:", error);
      // Potremmo voler ripristinare la selezione precedente in caso di errore
    }
  }

  return {
    tradingAccounts,
    selectedTradingAccountIds,
    isLoading,
    hasTradingAccounts,
    selectedTradingAccounts, // Nuovo getter
    fetchTradingAccounts,
    createTradingAccount,
    updateAccountSelection, // Nuova azione
  };
}, {
  persist: {
    // Persisti solo gli ID, non l'intero oggetto
    paths: ['selectedTradingAccountIds'],
  },
});