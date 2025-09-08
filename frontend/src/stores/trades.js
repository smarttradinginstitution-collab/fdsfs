// =============================================================================
// FILE: stores/trades.js
// DESCRIZIONE: Store Pinia per la gestione centralizzata dei dati dei trade.
// Questo store si occupa di:
// - Mantenere lo stato dei trade, dei setup disponibili e dei dati statistici.
// - Interagire con il backend per recuperare e inviare dati.
// - Fornire dati calcolati (getters) ai componenti Vue.
// =============================================================================

import { defineStore } from 'pinia';
import { useFilterStore } from './filterStore';
import { useAuthStore } from './auth';
import apiClient from '../services/api';

/**
 * Helper per mappare un trade dal formato del backend a quello del frontend.
 * Questo garantisce coerenza e disaccoppia i due modelli.
 * @param {object} trade - L'oggetto trade ricevuto dal backend.
 * @returns {object} L'oggetto trade nel formato utilizzato dal frontend.
 */
const mapBackendTradeToFrontend = (trade) => ({
  id: trade.id,
  ticker: trade.symbol,
  type: trade.direction,
  pnl: trade.p_l,
  date: trade.entry_timestamp,
  strategy: trade.setup, // Mapping cruciale: 'setup' (backend) -> 'strategy' (frontend)
  risk: trade.risk, // Assumendo che 'risk' esista o venga calcolato
  openTime: new Date(trade.entry_timestamp).toLocaleTimeString(),
  instrument: 'Stocks', // Da rendere dinamico se necessario
  commission: trade.commission, // Assumendo che esista
  netROI: trade.net_roi, // Assumendo che esista
  rMultiple: trade.r_multiple, // Assumendo che esista
  ticks: trade.ticks, // Assumendo che esista
  bestExit: trade.best_exit, // Assumendo che esista
  volume: trade.position_size,
  // Manteniamo anche i campi originali se servono altrove
  ...trade,
});


export const useTradesStore = defineStore('trades', {
  state: () => ({
    trades: [], // Inizializzato vuoto, verrà popolato dal backend
    setups: [], // Elenco dei setup/strategie per i filtri
    dashboardStats: null,
    calendarData: [],
    isLoading: false,
    isSummaryLoading: false, // Potrebbe essere unificato con isLoading
    activeSummary: null,
  }),

  getters: {
    // Fornisce i setup per il menu a discesa del filtro.
    allStrategies(state) {
      // Ora usa l'elenco dei setup caricato dal backend.
      return ['All', ...state.setups];
    },

    // Filtra i trade in base ai filtri attivi (data e strategia).
    filteredTrades: (state) => {
      const filterStore = useFilterStore();
      let tradesToFilter = state.trades;

      // 1. Filtro per data
      if (filterStore.startDate && filterStore.endDate) {
        const start = new Date(filterStore.startDate).setHours(0, 0, 0, 0);
        const end = new Date(filterStore.endDate).setHours(23, 59, 59, 999);
        tradesToFilter = tradesToFilter.filter(trade => {
          const tradeDate = new Date(trade.date);
          return tradeDate >= start && tradeDate <= end;
        });
      }

      // 2. Filtro per strategia/setup
      if (filterStore.selectedStrategy && filterStore.selectedStrategy !== 'All') {
        tradesToFilter = tradesToFilter.filter(trade => trade.strategy === filterStore.selectedStrategy);
      }

      return tradesToFilter;
    },

    // Tutti gli altri getters (processedData, allDashboardStats, etc.) dovrebbero
    // funzionare correttamente dato che si basano su `filteredTrades`.
    // NOTA: I campi usati in questi getters (es. `pnl`, `date`, `strategy`)
    // devono essere presenti dopo il mapping da backend a frontend.

    processedData(state) {
      const trades = this.filteredTrades;
      const filterStore = useFilterStore();
      const viewDateForCalendar = new Date(filterStore.endDate);

      const stats = { totalPnl: 0, tradeCount: 0, winningTrades: 0, losingTrades: 0, breakEvenTrades: 0, grossProfit: 0, grossLoss: 0, totalRisk: 0 };
      const dailyDataForCalendar = {};
      const performanceByStrategy = {};
      const performanceByDayOfWeek = {};
      const pnlByDay = {};
      const daysOfWeek = ['Domenica', 'Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato'];
      daysOfWeek.forEach(day => {
        performanceByDayOfWeek[day] = { totalPnl: 0, tradeCount: 0, winningTrades: 0 };
      });

      for (const trade of trades) {
        stats.totalPnl += trade.pnl;
        stats.tradeCount++;
        stats.totalRisk += trade.risk;
        if (trade.pnl > 0) {
          stats.winningTrades++;
          stats.grossProfit += trade.pnl;
        } else if (trade.pnl < 0) {
          stats.losingTrades++;
          stats.grossLoss += Math.abs(trade.pnl);
        } else {
          stats.breakEvenTrades++;
        }

        const tradeDate = new Date(trade.date);
        const dayKey = tradeDate.toISOString().split('T')[0];

        if (!pnlByDay[dayKey]) pnlByDay[dayKey] = 0;
        pnlByDay[dayKey] += trade.pnl;

        if (tradeDate.getFullYear() === viewDateForCalendar.getFullYear() && tradeDate.getMonth() === viewDateForCalendar.getMonth()) {
          if (!dailyDataForCalendar[dayKey]) {
            dailyDataForCalendar[dayKey] = { totalPnl: 0, tradeCount: 0, winningTrades: 0 };
          }
          dailyDataForCalendar[dayKey].totalPnl += trade.pnl;
          dailyDataForCalendar[dayKey].tradeCount++;
          if (trade.pnl > 0) dailyDataForCalendar[dayKey].winningTrades++;
        }

        if (trade.strategy) {
          if (!performanceByStrategy[trade.strategy]) {
            performanceByStrategy[trade.strategy] = { totalPnl: 0, tradeCount: 0, winningTrades: 0 };
          }
          performanceByStrategy[trade.strategy].totalPnl += trade.pnl;
          performanceByStrategy[trade.strategy].tradeCount++;
          if (trade.pnl > 0) performanceByStrategy[trade.strategy].winningTrades++;
        }

        const dayName = daysOfWeek[tradeDate.getDay()];
        performanceByDayOfWeek[dayName].totalPnl += trade.pnl;
        performanceByDayOfWeek[dayName].tradeCount++;
        if (trade.pnl > 0) performanceByDayOfWeek[dayName].winningTrades++;
      }

      const winLossDaysStats = { winningDays: 0, losingDays: 0, breakEvenDays: 0 };
      for (const dayPnl of Object.values(pnlByDay)) {
        if (dayPnl > 0) winLossDaysStats.winningDays++;
        else if (dayPnl < 0) winLossDaysStats.losingDays++;
        else winLossDaysStats.breakEvenDays++;
      }

      return { stats, dailyDataForCalendar, performanceByStrategy, performanceByDayOfWeek, winLossDaysStats };
    },

    tradeHeaders: () => [
        { key: 'symbol', text: 'Ticker' },
        { key: 'direction', text: 'Side' },
        { key: 'p_l', text: 'Net P&L' },
        { key: 'entry_timestamp', text: 'Date' },
    ],
  },

  actions: {
    /**
     * Recupera l'elenco di tutti i setup/strategie univoci per l'utente.
     */
    async fetchSetups() {
      const authStore = useAuthStore();
      const userId = authStore.user?.id;
      if (!userId) return;

      try {
        const response = await apiClient.get(`/api/v1/trades/setups?user_id=${userId}`);
        this.setups = response.data;
      } catch (error) {
        console.error('Errore nel recupero dei setup:', error);
        this.setups = []; // Resetta in caso di errore
      }
    },

    /**
     * Azione unificata per recuperare i trade dal backend con filtri.
     */
    async fetchTrades() {
      this.isLoading = true;
      const authStore = useAuthStore();
      const filterStore = useFilterStore();
      const userId = authStore.user?.id;

      if (!userId) {
        console.error("Utente non autenticato.");
        this.isLoading = false;
        return;
      }

      // Prepara i parametri per la richiesta API
      const params = {
        user_id: userId,
        start_date: filterStore.startDate?.toISOString().split('T')[0],
        end_date: filterStore.endDate?.toISOString().split('T')[0],
      };

      // Aggiungi il filtro per setup solo se non è 'All'
      if (filterStore.selectedStrategy && filterStore.selectedStrategy !== 'All') {
        params.setups = [filterStore.selectedStrategy];
      }

      try {
        const response = await apiClient.get('/api/v1/trades/', { params });
        // Mappa i dati dal backend al formato del frontend
        this.trades = response.data.map(mapBackendTradeToFrontend);
      } catch (error) {
        console.error('Errore nel recupero dei trade:', error);
        this.trades = []; // Resetta i trade in caso di errore
      } finally {
        this.isLoading = false;
      }
    },

    async fetchDashboardStats() {
      const authStore = useAuthStore();
      const userId = authStore.user?.id;

      if (!userId) {
        console.error('User not authenticated, cannot fetch dashboard stats.');
        return;
      }

      try {
        const response = await apiClient.get(`/api/v1/trades/performance/metrics?user_id=${userId}`);
        this.dashboardStats = response.data;
      } catch (error) {
        console.error('Error fetching dashboard stats:', error);
      }
    },

    async fetchCalendarData() {
        const authStore = useAuthStore();
        const userId = authStore.user?.id;

        if (!userId) {
          console.error('User not authenticated, cannot fetch calendar data.');
          return;
        }

        try {
          const response = await apiClient.get(`/api/v1/trades/calendar/data?user_id=${userId}`);
          this.calendarData = response.data;
        } catch (error) {
          console.error('Error fetching calendar data:', error);
        }
      },

    async addTrade(tradeData) {
      this.isLoading = true;
      try {
        const authStore = useAuthStore();
        const userId = authStore.user?.id;

        if (!userId) {
          throw new Error('User not authenticated');
        }

        const payload = { ...tradeData };
        // Qui la mappatura è da frontend a backend, se necessaria
        // Esempio: payload.p_l = tradeData.pnl; delete payload.pnl;

        const response = await apiClient.post(`/api/v1/trades/?user_id=${userId}`, payload);
        const newTrade = mapBackendTradeToFrontend(response.data);
        this.trades.unshift(newTrade);

        // Aggiorna le statistiche correlate
        await this.fetchDashboardStats();
        await this.fetchCalendarData();
        // Potrebbe essere utile anche ri-filtrare o aggiornare la vista

        return newTrade;
      } catch (error) {
        console.error('Error adding trade:', error);
        throw error;
      } finally {
        this.isLoading = false;
      }
    },
  },
});
