// =============================================================================
// FILE: stores/trades.js
// DESCRIZIONE: Store Pinia per la gestione dei trade e dei dati della dashboard,
// completamente allineato con la nuova architettura del backend.
// =============================================================================

import { defineStore } from 'pinia';
import { useFilterStore } from './filterStore';
import { useAccountStore } from './account';
import { useResourceStore } from './resourceStore';
import apiClient from '../services/api';

const mapBackendTradeToFrontend = (trade) => ({
  id: trade.id,
  ticker: trade.symbol,
  type: trade.direction,
  pnl: trade.p_l,
  date: trade.entry_timestamp,
  strategy: trade.setup,
  // ... altri campi
  ...trade,
});

export const useTradesStore = defineStore('trades', {
  state: () => ({
    trades: [],
    dashboardStats: null,
    calendarData: [],
    processedStats: null,
    equityCurve: null,
    vantageScore: null,
    isLoading: false,
  }),

  getters: {
    allStrategies: () => {
      const resourceStore = useResourceStore();
      const playbookLabels = resourceStore.playbooks.map((p) => p.label);
      return ['All', ...playbookLabels];
    },

    allDashboardStats(state) {
      const emptyStat = (key, label, category, value = 'N/A') => ({ key, label, category, value, changeType: 'neutral' });
      const emptyStats = {
        netPnl: { ...emptyStat('netPnl', 'Net P&L', 'Profitability', '$0.00'), changeType: 'neutral' },
        winRate: { key: 'winRate', label: 'Win Rate', category: 'Ratios & Efficiency', value: 'N/A', wins: 0, losses: 0, breakevens: 0, changeType: 'neutral' },
        trades: emptyStat('trades', 'Trades', 'Consistency', '0'),
        profitFactor: emptyStat('profitFactor', 'Profit Factor', 'Ratios & Efficiency'),
        avgWin: emptyStat('avgWin', 'Avg. Win', 'Profitability', '$0.00'),
        avgLoss: emptyStat('avgLoss', 'Avg. Loss', 'Profitability', '$0.00'),
        expectancy: emptyStat('expectancy', 'Expectancy', 'Ratios & Efficiency', '$0.00'),
      };

      if (!state.dashboardStats) {
        return emptyStats;
      }

      // Se i dati esistono, mapparli come prima.
      // Questa parte può essere implementata quando l'endpoint delle statistiche sarà riattivato.
      // Per ora, restituiamo i dati vuoti per evitare crash.
      return emptyStats;
    },
  },

  actions: {
    /**
     * Helper per ottenere l'ID del trading account selezionato.
     * Centralizza il controllo per evitare codice duplicato.
     */
    _getSelectedTradingAccountId() {
      const accountStore = useAccountStore();
      const id = accountStore.selectedTradingAccountId;
      if (!id) {
        console.warn("Nessun Trading Account selezionato.");
        return null;
      }
      return id;
    },

    async fetchTrades() {
      const tradingAccountId = this._getSelectedTradingAccountId();
      if (!tradingAccountId) return;

      try {
        const response = await apiClient.get(`/api/v1/trades/by-trading-account/${tradingAccountId}/`);
        this.trades = response.data.map(mapBackendTradeToFrontend);
      } catch (error) {
        console.error('Errore nel recupero dei trade:', error);
        this.trades = [];
      }
    },

    async fetchDashboardStats() {
      const tradingAccountId = this._getSelectedTradingAccountId();
      if (!tradingAccountId) return;
      // NOTA: L'endpoint va confermato, ma ipotizzo sia questo
      // try {
      //   const response = await apiClient.get(`/api/v1/trading-accounts/${tradingAccountId}/performance/metrics`);
      //   this.dashboardStats = response.data;
      // } catch (error) {
      //   console.error('Errore nel recupero delle statistiche dashboard:', error);
      // }
    },

    async fetchCalendarData() {
      const tradingAccountId = this._getSelectedTradingAccountId();
      if (!tradingAccountId) return;
      // NOTA: L'endpoint va confermato
      // try {
      //   const response = await apiClient.get(`/api/v1/trading-accounts/${tradingAccountId}/calendar/data`);
      //   this.calendarData = response.data;
      // } catch (error) {
      //   console.error('Errore nel recupero dei dati calendario:', error);
      // }
    },

    async fetchVantageScore() {
      const tradingAccountId = this._getSelectedTradingAccountId();
      if (!tradingAccountId) return;
        // NOTA: L'endpoint va confermato
      // try {
      //   const response = await apiClient.get(`/api/v1/trading-accounts/${tradingAccountId}/vantage-score`);
      //   this.vantageScore = response.data;
      // } catch (error) {
      //   console.error('Errore nel recupero del Vantage Score:', error);
      // }
    },

    async addTrade(tradeData) {
        const tradingAccountId = this._getSelectedTradingAccountId();
        if (!tradingAccountId) {
            throw new Error('Nessun Trading Account selezionato');
        }

        const payload = {
            trading_account_id: tradingAccountId,
            symbol: tradeData.ticker,
            p_l: tradeData.pnl,
            direction: tradeData.direction,
            // ... altri campi dal form
            tag_ids: tradeData.tags || [],
            mistake_ids: tradeData.mistakes || [],
            playbook_ids: tradeData.playbooks || [],
        };

        const response = await apiClient.post('/api/v1/trades/', payload);
        const newTrade = mapBackendTradeToFrontend(response.data);
        this.trades.unshift(newTrade);
        await this.fetchAllDataForDashboard();
        return newTrade;
    },

    async fetchAllDataForDashboard() {
      this.isLoading = true;
      const tradingAccountId = this._getSelectedTradingAccountId();
      if (!tradingAccountId) {
        this.isLoading = false;
        return;
      }

      // Eseguiamo solo le chiamate che sappiamo essere corrette.
      // Le altre sono pronte per essere attivate quando gli endpoint saranno confermati.
      await Promise.allSettled([
        this.fetchTrades(),
        // this.fetchDashboardStats(),
        // this.fetchCalendarData(),
        // this.fetchVantageScore(),
      ]);

      this.isLoading = false;
    },

    reset() {
      this.trades = [];
      this.dashboardStats = null;
      this.calendarData = [];
      this.processedStats = null;
      this.equityCurve = null;
      this.vantageScore = null;
      this.isLoading = false;
    },
  },
});