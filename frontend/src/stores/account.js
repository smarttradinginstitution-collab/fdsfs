// =============================================================================
// FILE: src/stores/account.js
// DESCRIZIONE: Store per la gestione del GeneralAccount e dei TradingAccounts.
// =============================================================================
import { defineStore } from 'pinia';
import apiClient from '../services/api';
import { useAuthStore } from './auth';

export const useAccountStore = defineStore('account', {
  state: () => ({
    generalAccount: null,
    tradingAccounts: [],
    selectedTradingAccountId: null,
    isLoading: false,
    error: null,
  }),

  getters: {
    /**
     * Restituisce l'oggetto completo del TradingAccount attualmente selezionato.
     */
    selectedTradingAccount(state) {
      if (!state.selectedTradingAccountId || state.tradingAccounts.length === 0) {
        return null;
      }
      return state.tradingAccounts.find(
        (acc) => acc.id === state.selectedTradingAccountId
      );
    },
  },

  actions: {
    /**
     * Recupera il GeneralAccount dell'utente autenticato.
     */
    async fetchGeneralAccount() {
      const authStore = useAuthStore();
      if (!authStore.isAuthenticated) {
        console.error('User not authenticated, cannot fetch general account.');
        return;
      }

      this.isLoading = true;
      this.error = null;
      try {
        const response = await apiClient.get('/api/v1/general-accounts/me');
        this.generalAccount = response.data;
      } catch (error) {
        this.error = 'Failed to fetch general account.';
        console.error('Error fetching general account:', error);
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Recupera tutti i TradingAccount associati al GeneralAccount dell'utente.
     */
    async fetchTradingAccounts() {
      const authStore = useAuthStore();
      if (!authStore.isAuthenticated) {
        console.error('User not authenticated, cannot fetch trading accounts.');
        return;
      }

      this.isLoading = true;
      this.error = null;
      try {
        const response = await apiClient.get('/api/v1/trading-accounts/');
        this.tradingAccounts = response.data;

        // Se non c'è un trading account selezionato e ne abbiamo caricati,
        // selezioniamo il primo di default.
        if (!this.selectedTradingAccountId && this.tradingAccounts.length > 0) {
          this.selectTradingAccount(this.tradingAccounts[0].id);
        }
      } catch (error) {
        this.error = 'Failed to fetch trading accounts.';
        console.error('Error fetching trading accounts:', error);
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Imposta un TradingAccount come quello attivo.
     * @param {string} accountId - L'ID del TradingAccount da selezionare.
     */
    selectTradingAccount(accountId) {
      const accountExists = this.tradingAccounts.some(acc => acc.id === accountId);
      if (accountExists) {
        this.selectedTradingAccountId = accountId;
        // Potremmo salvare l'ID nel localStorage per persistenza tra le sessioni
        localStorage.setItem('selectedTradingAccountId', accountId);
        console.log(`Trading Account selezionato: ${accountId}`);
      } else {
        console.warn(`Tentativo di selezionare un TradingAccount non esistente: ${accountId}`);
      }
    },

    /**
     * Azione master per inizializzare tutti i dati dell'account.
     * Recupera prima il GeneralAccount e poi i TradingAccounts.
     */
    async initializeAccounts() {
      await this.fetchGeneralAccount();
      if (this.generalAccount) {
        await this.fetchTradingAccounts();
      }
      // Prova a caricare l'ID salvato dal localStorage
      const savedAccountId = localStorage.getItem('selectedTradingAccountId');
      if (savedAccountId) {
          this.selectTradingAccount(savedAccountId);
      }
    },

    /**
     * Resetta lo stato dello store, utile durante il logout.
     */
    reset() {
      this.generalAccount = null;
      this.tradingAccounts = [];
      this.selectedTradingAccountId = null;
      this.isLoading = false;
      this.error = null;
      localStorage.removeItem('selectedTradingAccountId');
    },
  },
});