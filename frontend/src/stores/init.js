import { defineStore } from 'pinia';
import { useTradingAccountsStore } from './tradingAccounts';
import { useDashboardLayoutStore } from './dashboardLayout';
import { useTradesStore } from './trades';
import { useNotebookStore } from './notebookStore';
import { useTagsStore } from './tagsStore';
import { usePlaybookStore } from './playbookStore';
import { useTradingDnaStore } from './tradingDnaStore';
import { useUiStore } from './uiStore';

/**
 * Store per orchestrare il caricamento iniziale dei dati della sessione.
 */
export const useInitStore = defineStore('init', {
  state: () => ({
    isInitialized: false,
    isLoading: false,
  }),
  actions: {
    /**
     * Esegue la sequenza di caricamento dati in 3 gruppi.
     * 1. Dati essenziali (bloccante)
     * 2. Dati della dashboard (parallelo, bloccante)
     * 3. Dati secondari (parallelo, non bloccante)
     */
    async initSessionData() {
      // Previene inizializzazioni multiple
      if (this.isInitialized || this.isLoading) {
        console.log('Inizializzazione già in corso o completata.');
        return;
      }

      const uiStore = useUiStore();
      this.isLoading = true;
      uiStore.showLoader('Inizializzazione della sessione...');

      try {
        // --- GRUPPO 1: Dati Essenziali dell'Account ---
        uiStore.updateLoaderMessage('Caricamento del tuo account...');
        const tradingAccountsStore = useTradingAccountsStore();
        // L'azione `fetchTradingAccounts` ora imposterà anche l'account selezionato
        // ma NON avvierà più il caricamento a catena.
        await tradingAccountsStore.fetchTradingAccounts();

        // Se non ci sono conti o non ne è selezionato nessuno, non ha senso continuare.
        if (!tradingAccountsStore.hasTradingAccounts || !tradingAccountsStore.selectedTradingAccount) {
          console.warn('Nessun conto di trading trovato o selezionato. Caricamento dati dashboard interrotto.');
          this.isInitialized = true;
          return;
        }

        // --- GRUPPO 2: Dati Principali della Dashboard (in parallelo) ---
        uiStore.updateLoaderMessage('Caricamento della dashboard...');
        const tradesStore = useTradesStore();
        const dashboardLayoutStore = useDashboardLayoutStore();
        const tagsStore = useTagsStore();
        const playbookStore = usePlaybookStore();
        const tradingDnaStore = useTradingDnaStore();

        await Promise.allSettled([
          tradesStore.fetchTrades({ ignoreFilters: true }), // Carica la lista di tutti i trade
          tradesStore.fetchAllDataForDashboard(),
          dashboardLayoutStore.fetchLayout(),
          tagsStore.fetchTags(),
          playbookStore.fetchPlaybooks(),
          tradingDnaStore.fetchTradingDna(),
        ]);

        // --- GRUPPO 3: Dati Secondari (in background) ---
        // Questi vengono caricati per ultimi. L'interfaccia può già essere utilizzabile.
        // Non usiamo `await` qui per non bloccare la UI.
        const notebookStore = useNotebookStore();
        Promise.allSettled([
          notebookStore.fetchFolders(),
          notebookStore.fetchAllNotes(),
        ]);

        this.isInitialized = true;
        console.log('Inizializzazione della sessione completata.');

      } catch (error) {
        console.error('Errore durante l-inizializzazione dei dati della sessione:', error);
        uiStore.showToast({ message: 'Errore nel caricamento dei dati.', type: 'danger' });
      } finally {
        this.isLoading = false;
        uiStore.hideLoader();
      }
    },
  },
});
