
// =============================================================================
// FILE: stores/trades.js
// DESCRIZIONE: Store per la gestione completa dei dati dei trade, inclusi filtri
// e integrazione con l'analisi SOA.
// =============================================================================

import { defineStore } from 'pinia';
import { useFilterStore } from './filterStore';
import { useTradingAccountsStore } from './tradingAccounts';
import { useUiStore } from './uiStore';
import { usePlaybookStore } from './playbookStore';
import apiClient from '../services/api';

/**
 * Helper per mappare un trade dal formato del backend a quello del frontend.
 * Questo garantisce coerenza e disaccoppia i due modelli.
 * @param {object} trade - L'oggetto trade ricevuto dal backend.
 * @returns {object} L'oggetto trade nel formato utilizzato dal frontend.
 */
const mapBackendTradeToFrontend = (trade) => ({
  id: trade.id,
  type: trade.direction,
  pnl: trade.p_l,
  date: trade.entry_timestamp,
  strategy: trade.playbook?.title ?? 'N/A',
  risk: trade.risk,
  instrument: 'Stocks',
  commission: trade.commission,
  netROI: trade.net_roi,
  rMultiple: trade.r_multiple,
  ticks: trade.ticks,
  bestExit: trade.best_exit,
  volume: trade.position_size,
  is_reviewed: trade.is_reviewed,
  ...trade,
  mistakes: trade.mistakes || [],
  psychology_states: trade.psychology_states || [],
  rules_followed: trade.rules_followed || [],
});

export const useTradesStore = defineStore('trades', {
  state: () => ({
    trades: [],
    playbookTrades: [],
    dashboardStats: null,
    calendarData: [],
    processedStats: null,
    equityCurve: null,
    vantageScore: null,
    isLoading: false,
    isSummaryLoading: false,
    activeSummary: null,
    selectedTrade: null,
    isTradeLoading: false,
    dataSignature: null,
    tradeIdFilter: [], // Nuovo stato per i filtri ID da TradesView
  }),

  getters: {
    // Getter esistenti...
    getPreviousTradeId: (state) => { /* ... */ },
    getNextTradeId: (state) => { /* ... */ },
    netPnl: (state) => { /* ... */ },
    allPlaybooks: () => { /* ... */ },
    allDashboardStats(state) { /* ... */ },
    getVantageScoreData: (state) => { /* ... */ },
    getRrDistributionData: (state) => { /* ... */ },
    calendarDataByMonth(state) { /* ... */ },
    strategyPerformanceData(state) { /* ... */ },
    performanceByDayOfWeek(state) { /* ... */ },
    winLossDays: (state) => { /* ... */ },
    equityCurveData: (state) => { /* ... */ },
    calendarControlsData(state) { /* ... */ },

    /**
     * Getter per gli header della tabella dei trade.
     * @returns {Array<object>} L'array di configurazione degli header.
     */
    tradeHeaders: () => [
      { key: 'checkbox', text: '' },
      { key: 'entry_timestamp', text: 'Open Date' },
      { key: 'symbol_snapshot', text: 'Symbol' },
      { key: 'status', text: 'Status' },
      { key: 'exit_timestamp', text: 'Close Date' },
      { key: 'duration_minutes', text: 'Duration' },
      { key: 'entry_price', text: 'Entry Price', align: 'right' },
      { key: 'exit_price', text: 'Exit Price', align: 'right' },
      { key: 'p_l', text: 'Net P&L', align: 'right' },
      { key: 'net_roi', text: 'Net ROI', align: 'right' },
      { key: 'vantage_insights', text: 'Vantage Insights' },
      { key: 'setups', text: 'Setups' },
    ],

    /**
     * Nuovo getter per gli header della tabella che include la colonna SOA.
     * @returns {Array<object>} Array di header con la colonna SOA.
     */
    tradeHeadersWithSoa() {
      const headers = this.tradeHeaders;
      // Inserisce la colonna SOA Cluster dopo 'Status'
      const statusIndex = headers.findIndex(h => h.key === 'status');
      if (statusIndex !== -1) {
        const newHeaders = [...headers];
        newHeaders.splice(statusIndex + 1, 0, { key: 'cluster_id', text: 'SOA Cluster' });
        return newHeaders;
      }
      return headers;
    },

    /**
     * Nuovo getter per restituire i trade filtrati in base al tradeIdFilter.
     * @param {object} state - Lo stato dello store.
     * @returns {Array<object>} La lista dei trade filtrati.
     */
    filteredTrades: (state) => {
      if (!state.tradeIdFilter || state.tradeIdFilter.length === 0) {
        return state.trades; // Se non c'è filtro, restituisce tutti i trade
      }
      return state.trades.filter(trade => state.tradeIdFilter.includes(trade.id));
    },
  },

  actions: {
    /**
     * Nuova azione per impostare il filtro basato su una lista di ID di trade.
     * @param {Array<string>} tradeIds - Array di UUID dei trade da mostrare.
     */
    setTradeIdFilter(tradeIds) {
      this.tradeIdFilter = tradeIds;
    },

    /**
     * Azione unificata per recuperare i trade dal backend.
     * @param {object} options - Opzioni per il fetch.
     * @param {boolean} options.ignoreFilters - Se true, carica tutti i trade senza filtri.
     */
    async fetchTrades(options = { ignoreFilters: false }) {
      this.isLoading = true;
      const tradingAccountsStore = useTradingAccountsStore();
      const selectedAccount = tradingAccountsStore.selectedTradingAccount;

      if (!selectedAccount) {
        this.trades = [];
        this.isLoading = false;
        return;
      }

      const toYYYYMMDD = (date) => date ? new Date(date).toISOString().split('T')[0] : null;

      const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
      const params = { user_timezone: userTimezone };

      if (!options.ignoreFilters) {
        const filterStore = useFilterStore();
        params.start_date = toYYYYMMDD(filterStore.startDate);
        params.end_date = toYYYYMMDD(filterStore.endDate);

        if (filterStore.selectedStrategy && filterStore.selectedStrategy.toLowerCase() !== 'all') {
          params.setups = [filterStore.selectedStrategy];
        }
      }

      try {
        const response = await apiClient.get(`/trades/by-trading-account/${selectedAccount.id}`, { params });
        this.trades = response.data.map(mapBackendTradeToFrontend);
        // Resetta il filtro ID quando i dati principali vengono ricaricati
        this.tradeIdFilter = [];
      } catch (error) {
        console.error('Errore nel recupero dei trade:', error);
        this.trades = [];
      } finally {
        this.isLoading = false;
      }
    },

    // Altre azioni esistenti...
    async fetchAllDataForDashboard() { /* ... */ },
    async fetchTradeSummary(dateRange) { /* ... */ },
    async fetchDashboardStats() { /* ... */ },
    async fetchCalendarData() { /* ... */ },
    async fetchVantageScore() { /* ... */ },
    async addTrade(tradeData) { /* ... */ },
    async fetchProcessedStats() { /* ... */ },
    async fetchEquityCurve() { /* ... */ },
    async deleteTrade(tradeId) { /* ... */ },
    async deleteSelectedTrades(tradeIds) { /* ... */ },
    async fetchTradesByPlaybook(playbookId) { /* ... */ },
    async fetchTradeById(tradeId) { /* ... */ },
    async updateTrade(tradeId, payload) { /* ... */ },
    async fetchTradeTags(tradeId) { /* ... */ },
    async updateTradeTags(tradeId, tagIds) { /* ... */ },
    async _updateTradeLabels(tradeId, labelType, labelIds) { /* ... */ },
    async updateTradeMistakes(tradeId, mistakeIds) { /* ... */ },
    async updateTradePsychology(tradeId, psychologyIds) { /* ... */ },
    async updateTradeNewsImpacts(tradeId, newsImpactIds) { /* ... */ },
    async updateTradeRules(tradeId, ruleIds) { /* ... */ },
    async toggleReviewedStatus(tradeId) { /* ... */ },
  },
});
// Nota: Le implementazioni delle azioni esistenti sono state omesse per brevità
// ma rimangono invariate. Ho solo aggiunto la nuova logica.
