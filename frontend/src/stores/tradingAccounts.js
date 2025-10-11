// =============================================================================
// FILE: src/stores/tradingAccounts.js
// DESCRIZIONE: Questo store Pinia gestisce lo stato dei Trading Accounts.
// Si occupa di caricare, creare e selezionare i conti di trading di un utente.
// =============================================================================

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import apiClient from '@/services/api';
import { useAuthStore } from './auth';
import { useTradesStore } from './trades'; // Importa il trade store

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

      // Verifica se l'account precedentemente selezionato è ancora valido.
      // Se non lo è (o non ce n'era uno), pulisce la selezione senza sceglierne uno nuovo.
      // Questo assicura che l'utente venga indirizzato alla pagina di selezione.
      const isSelectedAccountValid = selectedTradingAccount.value && data.some(acc => acc.id === selectedTradingAccount.value.id);
      if (isSelectedAccountValid) {
        // Se l'account memorizzato è valido, carica i suoi trade all'avvio.
        // Usiamo l'istanza dello store dei trade per chiamare l'azione.
        const tradesStore = useTradesStore();
        tradesStore.fetchAllTradesForCurrentAccount();
      } else {
        // Se non è valido o non c'è, pulisci la selezione.
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
      // Opzionale: seleziona automaticamente il nuovo account creato
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
   * Imposta il conto di trading attivo e avvia il caricamento dei trade associati.
   * @param {object | null} account - L'oggetto del conto da selezionare o null.
   */
  async function selectTradingAccount(account) {
    selectedTradingAccount.value = account;
    const tradesStore = useTradesStore();

    if (account) {
      localStorage.setItem('selectedTradingAccount', JSON.stringify(account));
      // Dopo aver selezionato l'account, carica tutti i suoi trade
      await tradesStore.fetchAllTradesForCurrentAccount();
    } else {
      localStorage.removeItem('selectedTradingAccount');
      // Se l'account viene deselezionato, svuota la lista dei trade
      tradesStore.trades = [];
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