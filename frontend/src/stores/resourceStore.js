// =============================================================================
// FILE: src/stores/resourceStore.js
// DESCRIZIONE: Store per la gestione delle risorse a livello di GeneralAccount,
// come Playbook, Tag, Mistake, ecc.
// =============================================================================
import { defineStore } from 'pinia';
import apiClient from '../services/api';
import { useAccountStore } from './account';

export const useResourceStore = defineStore('resources', {
  state: () => ({
    playbooks: [],
    tags: [],
    mistakes: [],
    isLoading: false,
    error: null,
  }),

  actions: {
    async fetchPlaybooks() {
      try {
        const response = await apiClient.get('/api/v1/playbooks/');
        this.playbooks = response.data;
      } catch (error) {
        console.error('Errore nel recupero dei Playbook:', error);
        this.playbooks = [];
      }
    },

    async fetchTags() {
      try {
        const response = await apiClient.get('/api/v1/tags/');
        this.tags = response.data;
      } catch (error) {
        console.error('Errore nel recupero dei Tag:', error);
        this.tags = [];
      }
    },

    async fetchMistakes() {
      try {
        const response = await apiClient.get('/api/v1/mistakes/');
        this.mistakes = response.data;
      } catch (error) {
        console.error('Errore nel recupero dei Mistake:', error);
        this.mistakes = [];
      }
    },

    /**
     * Azione master per caricare tutte le risorse in parallelo.
     * Deve essere chiamata dopo che il GeneralAccount è stato caricato.
     */
    async fetchAllResources() {
      const accountStore = useAccountStore();
      if (!accountStore.generalAccount) {
        console.warn('GeneralAccount non disponibile. Caricamento risorse saltato.');
        return;
      }

      this.isLoading = true;
      this.error = null;
      try {
        await Promise.allSettled([
          this.fetchPlaybooks(),
          this.fetchTags(),
          this.fetchMistakes(),
        ]);
      } catch (err) {
        this.error = 'Failed to fetch resources.';
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Resetta lo stato dello store, utile durante il logout.
     */
    reset() {
      this.playbooks = [];
      this.tags = [];
      this.mistakes = [];
      this.isLoading = false;
      this.error = null;
    },
  },
});