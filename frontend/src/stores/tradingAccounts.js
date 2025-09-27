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
      const { data } = await apiClient.get('/trading-accounts/');
      tradingAccounts.value = data;

      // Se un account è selezionato, aggiornalo con i dati freschi dall'API
      // per assicurarsi che contenga tutte le informazioni (es. nome del broker).
      if (selectedTradingAccount.value) {
        const fullSelectedAccount = data.find(acc => acc.id === selectedTradingAccount.value.id);
        if (fullSelectedAccount) {
          // Aggiorna l'account selezionato con i dati completi.
          selectTradingAccount(fullSelectedAccount);
        } else {
          // L'account precedentemente selezionato non è più valido.
          selectTradingAccount(null);
        }
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
    createTradingAccount,
    selectTradingAccount,
  };
});