// =============================================================================
// FILE: stores/trades.js
// DESCRIZIONE: Store dei trade, refattorizzato per massima efficienza.
// =============================================================================

import { defineStore } from 'pinia';
import { useFilterStore } from './filterStore';
import { useTradingAccountsStore } from './tradingAccounts';
import { useUiStore } from './uiStore';
import { usePlaybookStore } from './playbookStore';
import { useNotebookStore } from './notebookStore';
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
  risk: trade.risk, // Assumendo che 'risk' esista o venga calcolato
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
    playbookTrades: [], // Trades specifici per un playbook
    // 'playbooks' rimosso, verrà letto da playbookStore
    dashboardStats: null,
    calendarData: [],
    processedStats: null,
    equityCurve: null,
    vantageScore: null, // Dati per il VantageScoreWidget
    isLoading: false,
    isSummaryLoading: false,
    activeSummary: null,
    selectedTrade: null,
    isTradeLoading: false,
    dataSignature: null, // Aggiunto per tracciare lo stato dei dati caricati
  }),

  getters: {
    getPreviousTradeId(state) {
      if (!state.selectedTrade || state.trades.length < 2) {
        return null;
      }
      const sortedTrades = [...state.trades].sort((a, b) => new Date(a.date) - new Date(b.date));
      const currentIndex = sortedTrades.findIndex(t => t.id === state.selectedTrade.id);
      return currentIndex > 0 ? sortedTrades[currentIndex - 1].id : null;
    },

    getNextTradeId(state) {
      if (!state.selectedTrade || state.trades.length < 2) {
        return null;
      }
      const sortedTrades = [...state.trades].sort((a, b) => new Date(a.date) - new Date(b.date));
      const currentIndex = sortedTrades.findIndex(t => t.id === state.selectedTrade.id);
      return currentIndex !== -1 && currentIndex < sortedTrades.length - 1 ? sortedTrades[currentIndex + 1].id : null;
    },

    netPnl(state) {
      return state.trades.reduce((sum, trade) => sum + trade.pnl, 0);
    },

    allPlaybooks() {
      const playbookStore = usePlaybookStore();
      const playbookTitles = playbookStore.playbooks.map(p => p.title);
      return ['All', ...playbookTitles];
    },

    allDashboardStats() {
      const tradingAccountsStore = useTradingAccountsStore();
      const selectedAccount = tradingAccountsStore.selectedTradingAccount;

      // Restituisce un set completo di statistiche vuote per evitare errori di rendering
      // se i dati non sono ancora stati caricati o se non c'è un account selezionato.
      const emptyStat = (key, label, category, value = 'N/A') => ({ key, label, category, value, changeType: 'neutral' });
      const emptyStats = {
          netPnl: { ...emptyStat('netPnl', 'Net P&L', 'Profitability', '$0.00'), changeType: 'neutral' },
          roi: { key: 'roi', label: 'ROI', category: 'Profitability', value: '0.00%', changeType: 'neutral' },
          winRate: { key: 'winRate', label: 'Win Rate', category: 'Ratios & Efficiency', value: 'N/A', wins: 0, losses: 0, breakevens: 0, changeType: 'neutral' },
          trades: emptyStat('trades', 'Trades', 'Consistency', '0'),
          profitFactor: emptyStat('profitFactor', 'Profit Factor', 'Ratios & Efficiency'),
          avgWin: emptyStat('avgWin', 'Avg. Win', 'Profitability', '$0.00'),
          avgLoss: emptyStat('avgLoss', 'Avg. Loss', 'Profitability', '$0.00'),
          expectancy: emptyStat('expectancy', 'Expectancy', 'Ratios & Efficiency', '$0.00'),
          avgTradePnl: emptyStat('avgTradePnl', 'Avg. Trade P&L', 'Profitability', '$0.00'),
          largestProfit: emptyStat('largestProfit', 'Largest Profit', 'Profitability', '$0.00'),
          largestLoss: emptyStat('largestLoss', 'Largest Loss', 'Profitability', '$0.00'),
          maxConsecutiveWins: emptyStat('maxConsecutiveWins', 'Max Consec. Wins', 'Consistency', '0'),
          maxConsecutiveLosses: emptyStat('maxConsecutiveLosses', 'Max Consec. Losses', 'Consistency', '0'),
          avgRealizedRr: emptyStat('avgRealizedRr', 'Avg. Realized R:R', 'Ratios & Efficiency'),
          maxDrawdownAbs: { key: 'maxDrawdownAbs', label: 'Max Drawdown', category: 'Risk Management', value: '$0.00 (0.00%)', changeType: 'neutral' },
          sharpeRatio: emptyStat('sharpeRatio', 'Sharpe Ratio', 'Ratios & Efficiency'),
          averageHoldTime: emptyStat('averageHoldTime', 'Avg. Hold Time', 'Other', '0 min'),
          initialBalance: emptyStat('initialBalance', 'Initial Balance', 'Core', '$0.00'),
          currentBalance: emptyStat('currentBalance', 'Current Balance', 'Core', '$0.00'),
          peakBalance: emptyStat('peakBalance', 'Peak Balance', 'Core', '$0.00'),
      };

      if (!this.dashboardStats || !selectedAccount) {
        return emptyStats;
      }

      const stats = this.dashboardStats.stats;
      const totalPnl = parseFloat(stats.net_pnl);
      const tradeCount = stats.trade_count;
      const winningTrades = stats.winning_trades;
      const losingTrades = stats.losing_trades;
      const breakEvenTrades = stats.breakeven_trades;
      const winRate = parseFloat(stats.win_rate);
      const avgWin = parseFloat(stats.avg_win);
      const avgLoss = parseFloat(stats.avg_loss);
      const expectancy = parseFloat(stats.expectancy);
      const avgTradePnl = parseFloat(stats.average_trade_pnl);
      const largestProfit = parseFloat(stats.largest_profit);
      const largestLoss = parseFloat(stats.largest_loss);
      const maxConsecutiveWins = stats.max_consecutive_wins;
      const maxConsecutiveLosses = stats.max_consecutive_losses;
      const avgRealizedRr = parseFloat(stats.avg_realized_rr);
      const maxDrawdownAbs = parseFloat(stats.max_drawdown_abs);
      const maxDrawdownPerc = parseFloat(stats.max_drawdown_percentage);
      const roi = parseFloat(stats.roi_percentage);
      const sharpeRatio = parseFloat(stats.sharpe_ratio);
      const averageHoldTime = parseFloat(stats.average_hold_time);

      // Calcoli per le metriche mancanti
      const initialBalance = parseFloat(selectedAccount.initial_balance ?? 0);
      const currentBalance = initialBalance + totalPnl;
      const peakBalance = this.equityCurve?.data?.length > 0 ? Math.max(...this.equityCurve.data) : initialBalance;

      return {
        ...emptyStats, // Inizia con un oggetto completo per garantire che tutte le chiavi esistano
        netPnl: { key: 'netPnl', label: 'Net P&L', category: 'Profitability', value: `${totalPnl >= 0 ? '+' : ''}$${totalPnl.toFixed(2)}`, changeType: totalPnl >= 0 ? 'positive' : 'negative' },
        roi: { key: 'roi', label: 'ROI', category: 'Profitability', value: `${roi.toFixed(2)}%`, changeType: roi >= 0 ? 'positive' : 'negative' },
        avgWin: { key: 'avgWin', label: 'Avg. Win', category: 'Profitability', value: `$${avgWin.toFixed(2)}`, changeType: 'neutral' },
        avgLoss: { key: 'avgLoss', label: 'Avg. Loss', category: 'Profitability', value: `$${avgLoss.toFixed(2)}`, changeType: 'neutral' },
        avgTradePnl: { key: 'avgTradePnl', label: 'Avg. Trade P&L', category: 'Profitability', value: `$${avgTradePnl.toFixed(2)}`, changeType: 'neutral' },
        largestProfit: { key: 'largestProfit', label: 'Largest Profit', category: 'Profitability', value: `$${largestProfit.toFixed(2)}`, changeType: 'neutral' },
        largestLoss: { key: 'largestLoss', label: 'Largest Loss', category: 'Profitability', value: `$${largestLoss.toFixed(2)}`, changeType: 'neutral' },

        winRate: { key: 'winRate', label: 'Win Rate', category: 'Ratios & Efficiency', value: `${winRate.toFixed(1)}%`, wins: winningTrades, losses: losingTrades, breakevens: breakEvenTrades, changeType: 'neutral' },
        profitFactor: { key: 'profitFactor', label: 'Profit Factor', category: 'Ratios & Efficiency', value: stats.profit_factor_label, changeType: 'neutral' },
        expectancy: { key: 'expectancy', label: 'Expectancy', category: 'Ratios & Efficiency', value: `$${expectancy.toFixed(2)}`, changeType: 'neutral' },
        avgRealizedRr: { key: 'avgRealizedRr', label: 'Avg. Realized R:R', category: 'Ratios & Efficiency', value: `${avgRealizedRr.toFixed(2)}`, changeType: 'neutral' },
        sharpeRatio: { key: 'sharpeRatio', label: 'Sharpe Ratio', category: 'Ratios & Efficiency', value: `${sharpeRatio.toFixed(2)}`, changeType: 'neutral' },

        maxDrawdownAbs: { key: 'maxDrawdownAbs', label: 'Max Drawdown', category: 'Risk Management', value: `$${maxDrawdownAbs.toFixed(2)} (${maxDrawdownPerc.toFixed(2)}%)`, changeType: 'neutral' },

        trades: { key: 'trades', label: 'Trades', category: 'Consistency', value: String(tradeCount), changeType: 'neutral' },
        maxConsecutiveWins: { key: 'maxConsecutiveWins', label: 'Max Consec. Wins', category: 'Consistency', value: String(maxConsecutiveWins), changeType: 'neutral' },
        maxConsecutiveLosses: { key: 'maxConsecutiveLosses', label: 'Max Consec. Losses', category: 'Consistency', value: String(maxConsecutiveLosses), changeType: 'neutral' },

        averageHoldTime: { key: 'averageHoldTime', label: 'Avg. Hold Time', category: 'Other', value: `${averageHoldTime.toFixed(0)} min`, changeType: 'neutral' },

        initialBalance: { key: 'initialBalance', label: 'Initial Balance', category: 'Core', value: `$${initialBalance.toFixed(2)}`, changeType: 'neutral' },
        currentBalance: { key: 'currentBalance', label: 'Current Balance', category: 'Core', value: `$${currentBalance.toFixed(2)}`, changeType: currentBalance >= initialBalance ? 'positive' : 'negative' },
        peakBalance: { key: 'peakBalance', label: 'Peak Balance', category: 'Core', value: `$${peakBalance.toFixed(2)}`, changeType: 'neutral' },
      };
    },

    getVantageScoreData(state) {
      if (!state.vantageScore) {
        // Ritorna una struttura dati vuota/default se i dati non sono ancora stati caricati
        return {
          score: 0,
          metrics: {
            'Win Rate': 0,
            'Profit Factor': 0,
            'Avg Win/Loss': 0,
            'Recovery Factor': 0,
            'Max Drawdown': 0,
            'Consistency': 0,
          },
        };
      }
      // Mappa i dati del backend alle etichette del frontend
      return {
        score: state.vantageScore.vantage_score,
        metrics: {
          'Win Rate': state.vantageScore.win_rate_score,
          'Profit Factor': state.vantageScore.profit_factor_score,
          'Avg Win/Loss': state.vantageScore.avg_win_loss_score,
          'Recovery Factor': state.vantageScore.recovery_factor_score,
          'Max Drawdown': state.vantageScore.max_drawdown_score,
          'Consistency': state.vantageScore.consistency_score,
        },
      };
    },

    getRrDistributionData(state) {
      const labels = ['<-2R', '-2R to -1R', '-1R to 0R', '0R to 1R', '1R to 2R', '>2R'];
      const data = Array(6).fill(0);

      if (!state.trades || state.trades.length === 0) {
        return { labels, datasets: [{ data }] };
      }

      for (const trade of state.trades) {
        const rMultiple = trade.rMultiple ?? 0;

        if (rMultiple < -2) {
          data[0]++;
        } else if (rMultiple >= -2 && rMultiple < -1) {
          data[1]++;
        } else if (rMultiple >= -1 && rMultiple < 0) {
          data[2]++;
        } else if (rMultiple >= 0 && rMultiple < 1) {
          data[3]++;
        } else if (rMultiple >= 1 && rMultiple < 2) {
          data[4]++;
        } else if (rMultiple >= 2) {
          data[5]++;
        }
      }

      return {
        labels,
        datasets: [{
          data,
        }]
      };
    },

    calendarDataByMonth() {
      const dailyDataFromBackend = this.calendarData.reduce((acc, entry) => {
        acc[entry.date] = {
          totalPnl: entry.pnl,
          tradeCount: entry.trade_count,
          winningTrades: entry.winning_trades_count,
        };
        return acc;
      }, {});

      const filterStore = useFilterStore();
      const viewDate = new Date(filterStore.endDate);
      const year = viewDate.getFullYear();
      const month = viewDate.getMonth();

      const daysInMonth = new Date(year, month + 1, 0).getDate();
      const firstDayOfWeek = new Date(year, month, 1).getDay();
      const calendarDays = [];
      const offset = (firstDayOfWeek === 0) ? 6 : firstDayOfWeek - 1; // Lunedì = 0, Domenica = 6

      for (let i = 0; i < offset; i++) {
        calendarDays.push({ isPlaceholder: true, key: `ph-start-${i}` });
      }

      for (let i = 1; i <= daysInMonth; i++) {
        const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(i).padStart(2, '0')}`;
        calendarDays.push({
          date: i,
          fullDate: dateStr,
          dailyData: dailyDataFromBackend[dateStr] || { totalPnl: 0, tradeCount: 0, winningTrades: 0 },
          isPlaceholder: false,
          key: dateStr,
        });
      }

      while (calendarDays.length % 7 !== 0) {
        calendarDays.push({ isPlaceholder: true, key: `ph-end-${calendarDays.length}` });
      }

      const getISOWeekString = (date) => {
        const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
        const dayNum = d.getUTCDay() || 7;
        d.setUTCDate(d.getUTCDate() + 4 - dayNum);
        const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
        const weekNo = Math.ceil((((d - yearStart) / 86400000) + 1) / 7);
        return `${d.getUTCFullYear()}-W${String(weekNo).padStart(2, '0')}`;
      };

      const weeksOfDays = [];
      const weeklySummaries = [];
      for (let i = 0; i < calendarDays.length; i += 7) {
        const weekChunk = calendarDays.slice(i, i + 7);
        weeksOfDays.push(weekChunk);

        const firstDayOfWeek = weekChunk.find(d => !d.isPlaceholder);
        let summary = { weekNumber: (i / 7) + 1, totalPnl: 0, tradingDaysCount: 0 }; // Default

        if (firstDayOfWeek && this.processedStats?.weekly_totals) {
          const isoWeekKey = getISOWeekString(new Date(firstDayOfWeek.fullDate));
          const backendSummary = this.processedStats.weekly_totals[isoWeekKey];
          if (backendSummary) {
            // Mantieni il weekNumber calcolato localmente, aggiorna solo i dati dal backend.
            summary.totalPnl = backendSummary.total_pnl;
            summary.tradingDaysCount = backendSummary.trading_days;
          }
        }
        weeklySummaries.push(summary);
      }

      return { weeksOfDays, weeklySummaries };
    },

    strategyPerformanceData() {
      if (!this.processedStats?.by_strategy) return [];

      const rawData = this.processedStats.by_strategy;
      // Usa il valore pre-calcolato dal backend.
      const maxPnl = this.processedStats.max_abs_pnl_by_strategy || 0;

      return Object.entries(rawData).map(([strategy, stats]) => {
        const winRate = stats.win_rate || 0;
        return {
          label: strategy,
          value: `${stats.trade_count} trades | ${winRate.toFixed(0)}% WR | $${stats.total_pnl.toFixed(2)}`,
          barWidth: maxPnl > 0 ? `${(Math.abs(stats.total_pnl) / maxPnl) * 100}%` : '0%',
          isPositive: stats.total_pnl >= 0,
        };
      });
    },

    performanceByDayOfWeek() {
      return this.processedStats?.by_day_of_week || {};
    },

    winLossDays(state) {
      return state.processedStats?.win_loss_days || { winningDays: 0, losingDays: 0, breakEvenDays: 0 };
    },

    equityCurveData(state) {
      // Restituisce direttamente i dati pre-calcolati dal backend.
      // Fornisce un default per evitare errori nel rendering iniziale.
      return state.equityCurve || { labels: [], data: [] };
    },

    tradeHeaders: () => [
      { key: 'checkbox', text: '' }, // Per la checkbox
      { key: 'entry_timestamp', text: 'Open Date' },
      { key: 'symbol_snapshot', text: 'Symbol' },
      { key: 'status', text: 'Status' },
      { key: 'exit_timestamp', text: 'Close Date' },
      { key: 'entry_price', text: 'Entry Price', align: 'right' },
      { key: 'exit_price', text: 'Exit Price', align: 'right' },
      { key: 'p_l', text: 'Net P&L', align: 'right' },
      { key: 'net_roi', text: 'Net ROI', align: 'right' },
      { key: 'vantage_insights', text: 'Vantage Insights' },
      { key: 'setups', text: 'Setups' },
    ],

    calendarControlsData() {
      const filterStore = useFilterStore();
      const viewDate = new Date(filterStore.endDate);

      if (isNaN(viewDate.getTime())) {
        return { monthLabel: 'Invalid Date', monthlyPnl: 0 };
      }

      const year = viewDate.getFullYear();
      const month = viewDate.getMonth() + 1; // 1-based
      const monthStr = `${year}-${String(month).padStart(2, '0')}`;

      // Legge il P&L mensile direttamente dai totali pre-calcolati dal backend
      const monthlyPnl = this.processedStats?.monthly_totals?.[monthStr] || 0;

      const monthLabel = viewDate.toLocaleString('en-US', { month: 'long', year: 'numeric' });
      return { monthLabel, monthlyPnl };
    }
  },

  actions: {
    /**
     * Azione unificata per recuperare i trade dal backend.
     * Può recuperare tutti i trade o applicare i filtri della dashboard.
     * @param {object} options - Opzioni per il fetch.
     * @param {boolean} options.ignoreFilters - Se true, carica tutti i trade senza filtri.
     */
    async fetchTrades(options = { ignoreFilters: false }) {
      this.isLoading = true;
      const tradingAccountsStore = useTradingAccountsStore();
      const selectedAccount = tradingAccountsStore.selectedTradingAccount;

      if (!selectedAccount) {
        console.log("Nessun trading account selezionato. Non carico i trade.");
        this.trades = [];
        this.isLoading = false;
        return;
      }

      const toYYYYMMDD = (date) => {
        if (!date) return null;
        const d = new Date(date);
        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
      };

      const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
      const params = {
        user_timezone: userTimezone,
      };

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
      } catch (error) {
        console.error('Errore nel recupero dei trade:', error);
        this.trades = [];
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Azione per aggiornare i dati della dashboard in base ai filtri.
     * Non ricarica la lista dei trade, ma solo le statistiche aggregate.
     */
    async fetchAllDataForDashboard() {
      // LOCK: Se un caricamento è già in corso, non avviarne un altro.
      if (this.isLoading) {
        console.log("Caricamento dashboard già in corso. Salto il fetch duplicato.");
        return;
      }
      this.isLoading = true;
      try {
        await Promise.allSettled([
          this.fetchDashboardStats(),
          this.fetchCalendarData(),
          this.fetchProcessedStats(),
          this.fetchEquityCurve(),
          this.fetchVantageScore(),
        ]);
      } finally {
        this.isLoading = false;
      }
    },

    async fetchTradeSummary(dateRange) {
      this.isSummaryLoading = true;
      this.activeSummary = null;

      const tradingAccountsStore = useTradingAccountsStore();
      const selectedAccount = tradingAccountsStore.selectedTradingAccount;
      if (!selectedAccount) {
        console.error("Nessun trading account selezionato per il riepilogo.");
        this.isSummaryLoading = false;
        return;
      }

      const filterStore = useFilterStore();
      const toYYYYMMDD = (date) => {
        if (!date) return null;
        const d = new Date(date);
        return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
      };

      const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
      const params = {
        start_date: toYYYYMMDD(dateRange.startDate),
        end_date: toYYYYMMDD(dateRange.endDate),
        user_timezone: userTimezone,
      };

      if (filterStore.selectedStrategy && filterStore.selectedStrategy.toLowerCase() !== 'all') {
        params.setups = [filterStore.selectedStrategy];
      }

      try {
        // Eseguiamo le due chiamate in parallelo per efficienza
        const [summaryResponse, tradesResponse] = await Promise.all([
          apiClient.get(`/trades/summary/${selectedAccount.id}`, { params }),
          apiClient.get(`/trades/by-trading-account/${selectedAccount.id}`, { params })
        ]);

        const fetchedTrades = tradesResponse.data.map(mapBackendTradeToFrontend);

        this.activeSummary = {
          startDate: dateRange.startDate,
          endDate: dateRange.endDate,
          trades: fetchedTrades,
          stats: summaryResponse.data.stats,
          cumulativePnlForChart: summaryResponse.data.cumulative_pnl_series,
        };

      } catch (error) {
        console.error('Errore nel recupero del riepilogo del trade:', error);
        this.activeSummary = { error: 'Failed to load summary.' };
      } finally {
        this.isSummaryLoading = false;
      }
    },

    async fetchDashboardStats() {
      const tradingAccountsStore = useTradingAccountsStore();
      const selectedAccount = tradingAccountsStore.selectedTradingAccount;
      if (!selectedAccount) return;

      const filterStore = useFilterStore();
      const params = {
        // Rimuoviamo trading_account_id dai parametri, verrà inserito nell'URL
        start_date: filterStore.startDate?.toISOString().split('T')[0],
        end_date: filterStore.endDate?.toISOString().split('T')[0],
      };

      if (filterStore.selectedStrategy && filterStore.selectedStrategy.toLowerCase() !== 'all') {
        params.setups = [filterStore.selectedStrategy];
      }

      try {
        // L'ID del conto è ora parte dell'URL, come per le altre chiamate
        const response = await apiClient.get(`/trades/performance/metrics/${selectedAccount.id}`, { params });
        this.dashboardStats = response.data;
      } catch (error) {
        console.error('Error fetching dashboard stats:', error);
      }
    },

    async fetchCalendarData() {
      const tradingAccountsStore = useTradingAccountsStore();
      const selectedAccount = tradingAccountsStore.selectedTradingAccount;
      if (!selectedAccount) return;

      const filterStore = useFilterStore();
      const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

      const params = {
        start_date: filterStore.startDate?.toISOString().split('T')[0],
        end_date: filterStore.endDate?.toISOString().split('T')[0],
        user_timezone: userTimezone,
      };

      if (filterStore.selectedStrategy && filterStore.selectedStrategy.toLowerCase() !== 'all') {
        params.setups = [filterStore.selectedStrategy];
      }

      try {
        const response = await apiClient.get(`/trades/calendar/data/${selectedAccount.id}`, { params });
        this.calendarData = response.data;
      } catch (error) {
        console.error('Error fetching calendar data:', error);
      }
    },

    async fetchVantageScore() {
      const tradingAccountsStore = useTradingAccountsStore();
      const selectedAccount = tradingAccountsStore.selectedTradingAccount;
      if (!selectedAccount) return;

      const filterStore = useFilterStore();
      const params = {
        start_date: filterStore.startDate?.toISOString().split('T')[0],
        end_date: filterStore.endDate?.toISOString().split('T')[0],
      };
      if (filterStore.selectedStrategy && filterStore.selectedStrategy.toLowerCase() !== 'all') {
        params.setups = [filterStore.selectedStrategy];
      }

      try {
        const response = await apiClient.get(`/trades/vantage-score/${selectedAccount.id}`, { params });
        this.vantageScore = response.data;
      } catch (error) {
        console.error('Error fetching vantage score:', error);
        this.vantageScore = null;
      }
    },

    async addTrade(tradeData) {
      this.isLoading = true;
      try {
        const tradingAccountsStore = useTradingAccountsStore();
        const selectedAccount = tradingAccountsStore.selectedTradingAccount;

        if (!selectedAccount) {
          console.error('Nessun trading account selezionato, impossibile aggiungere il trade.');
          throw new Error('Nessun trading account selezionato');
        }

        // Mappa i dati dal form al payload atteso dal backend
        const payload = {
          trading_account_id: selectedAccount.id, // Aggiungi l'ID del conto di trading
          symbol_snapshot: tradeData.symbol_snapshot,
          p_l: tradeData.pnl,
          playbook: tradeData.playbook,
          direction: tradeData.direction,
          entry_price: tradeData.entry_price,
          exit_price: tradeData.exit_price,
          stop_loss_price: tradeData.stop_loss_price,
          take_profit_price: tradeData.take_profit_price,
          position_size: tradeData.position_size,
          lowest_price_during_trade: tradeData.lowest_price_during_trade,
          highest_price_during_trade: tradeData.highest_price_during_trade,
          entry_timestamp: tradeData.entry_timestamp,
          exit_timestamp: tradeData.exit_timestamp,
          notes: tradeData.notes,
          notes_pre_trade: tradeData.notes_pre_trade,
          notes_post_trade: tradeData.notes_post_trade,
          emotional_state: tradeData.emotional_state,
          // I campi many-to-many ora si aspettano array di ID
          tag_ids: tradeData.tags || [], // Assumendo che 'tags' sia un array di ID
          mistake_ids: tradeData.mistakes || [], // Assumendo che 'mistakes' sia un array di ID
        };

        // Rimuovi le chiavi con valori null o undefined per non inviarle al backend
        Object.keys(payload).forEach(key => {
          if (payload[key] === null || payload[key] === undefined || payload[key] === '') {
            delete payload[key];
          }
        });

        const response = await apiClient.post('/trades/', payload);

        const newTradeFromServer = mapBackendTradeToFrontend(response.data);
        this.trades.unshift(newTradeFromServer);

        // Aggiorna le statistiche
        await this.fetchDashboardStats();
        await this.fetchCalendarData();

        return newTradeFromServer;
      } catch (error) {
        console.error('Error adding trade:', error);
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    async fetchProcessedStats() {
      const tradingAccountsStore = useTradingAccountsStore();
      const selectedAccount = tradingAccountsStore.selectedTradingAccount;
      if (!selectedAccount) return;

      const filterStore = useFilterStore();
      const params = {
        start_date: filterStore.startDate?.toISOString().split('T')[0],
        end_date: filterStore.endDate?.toISOString().split('T')[0],
      };
      if (filterStore.selectedStrategy && filterStore.selectedStrategy.toLowerCase() !== 'all') {
        params.setups = [filterStore.selectedStrategy];
      }

      try {
        const response = await apiClient.get(`/trades/processed-stats/${selectedAccount.id}`, { params });
        this.processedStats = response.data;
      } catch (error) {
        console.error('Error fetching processed stats:', error);
        this.processedStats = null;
      }
    },

    async fetchEquityCurve() {
      const tradingAccountsStore = useTradingAccountsStore();
      const selectedAccount = tradingAccountsStore.selectedTradingAccount;
      if (!selectedAccount) return;

      const filterStore = useFilterStore();
      const params = {
        start_date: filterStore.startDate?.toISOString().split('T')[0],
        end_date: filterStore.endDate?.toISOString().split('T')[0],
      };
      if (filterStore.selectedStrategy && filterStore.selectedStrategy.toLowerCase() !== 'all') {
        params.setups = [filterStore.selectedStrategy];
      }

      try {
        const response = await apiClient.get(`/trades/equity-curve/${selectedAccount.id}`, { params });
        this.equityCurve = response.data;
      } catch (error) {
        console.error('Error fetching equity curve:', error);
        this.equityCurve = null;
      }
    },

    /**
     * Azione per aggiornare i dati della dashboard in base ai filtri.
     * Non ricarica la lista dei trade, ma solo le statistiche aggregate.
     */
    async fetchAllDataForDashboard() {
      // LOCK: Se un caricamento è già in corso, non avviarne un altro.
      if (this.isLoading) {
        console.log("Caricamento dashboard già in corso. Salto il fetch duplicato.");
        return;
      }
      this.isLoading = true;
      try {
        await Promise.allSettled([
          this.fetchDashboardStats(),
          this.fetchCalendarData(),
          this.fetchProcessedStats(),
          this.fetchEquityCurve(),
          this.fetchVantageScore(),
        ]);
      } finally {
        this.isLoading = false;
      }
    },

    async deleteTrade(tradeId) {
      this.isLoading = true;
      try {
        await apiClient.delete(`/trades/${tradeId}`);

        // Remove the trade from the local state
        const index = this.trades.findIndex(t => t.id === tradeId);
        if (index !== -1) {
          this.trades.splice(index, 1);
        }

        // Refresh related data
        await this.fetchAllDataForDashboard();

      } catch (error) {
        console.error('Error deleting trade:', error);
        // Optionally, show a toast notification to the user
        const uiStore = useUiStore();
        uiStore.showToast({ message: 'Failed to delete trade.', type: 'danger' });
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    async deleteSelectedTrades(tradeIds) {
      this.isLoading = true;
      const uiStore = useUiStore();
      try {
        // Usa Promise.all per inviare le richieste di cancellazione in parallelo
        await Promise.all(tradeIds.map(id => apiClient.delete(`/trades/${id}`)));

        // Rimuovi i trade dallo stato locale
        this.trades = this.trades.filter(trade => !tradeIds.includes(trade.id));

        uiStore.showToast({ message: `${tradeIds.length} trades cancellati con successo.`, type: 'success' });

        // Aggiorna i dati della dashboard
        await this.fetchAllDataForDashboard();

      } catch (error) {
        console.error('Errore nella cancellazione dei trade selezionati:', error);
        uiStore.showToast({ message: 'Impossibile cancellare i trade selezionati.', type: 'danger' });
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    async fetchTradesByPlaybook(playbookId) {
      this.isLoading = true;
      try {
        const response = await apiClient.get(`/playbooks/${playbookId}/trades`);
        this.playbookTrades = response.data.map(mapBackendTradeToFrontend);
      } catch (error) {
        console.error(`Errore nel recupero dei trade per il playbook ${playbookId}:`, error);
        this.playbookTrades = [];
      } finally {
        this.isLoading = false;
      }
    },

    async fetchTradeById(tradeId) {
      this.isTradeLoading = true;
      try {
        const response = await apiClient.get(`/trades/${tradeId}`);
        this.selectedTrade = mapBackendTradeToFrontend(response.data);
      } catch (error) {
        console.error(`Errore nel recupero del trade ${tradeId}:`, error);
        this.selectedTrade = null;
        // Potremmo voler mostrare un errore all'utente qui
      } finally {
        this.isTradeLoading = false;
      }
    },

    async updateTrade(tradeId, payload) {
      this.isTradeLoading = true;
      const uiStore = useUiStore();
      try {
        const response = await apiClient.put(`/trades/${tradeId}`, payload);
        const updatedTrade = mapBackendTradeToFrontend(response.data);

        // Update the selected trade with the new data
        this.selectedTrade = updatedTrade;

        // Also update the trade in the main list
        const index = this.trades.findIndex(t => t.id === tradeId);
        if (index !== -1) {
          this.trades[index] = updatedTrade;
        }

        uiStore.showNotification({ message: 'Trade updated successfully!', type: 'success' });

        // Refresh dashboard stats to reflect changes
        await this.fetchAllDataForDashboard();

      } catch (error) {
        console.error('Error updating trade:', error);
        uiStore.showNotification({ message: 'Failed to update trade.', type: 'danger' });
      } finally {
        this.isTradeLoading = false;
      }
    },

    async fetchTradeTags(tradeId) {
      this.isTradeLoading = true;
      try {
        const response = await apiClient.get(`/trades/${tradeId}/tags`);
        if (this.selectedTrade && this.selectedTrade.id === tradeId) {
          this.selectedTrade.tags = response.data;
        }
      } catch (error) {
        console.error(`Error fetching tags for trade ${tradeId}:`, error);
        const uiStore = useUiStore();
        uiStore.showNotification({ message: 'Failed to load trade tags.', type: 'danger' });
      } finally {
        this.isTradeLoading = false;
      }
    },

    async updateTradeTags(tradeId, tagIds) {
      this.isTradeLoading = true;
      const uiStore = useUiStore();
      try {
        const response = await apiClient.post(`/trades/${tradeId}/tags`, tagIds);
        const updatedTags = response.data;

        if (this.selectedTrade && this.selectedTrade.id === tradeId) {
          this.selectedTrade.tags = updatedTags;
        }

        const index = this.trades.findIndex(t => t.id === tradeId);
        if (index !== -1) {
          this.trades[index].tags = updatedTags;
        }

        uiStore.showNotification({ message: 'Tags updated successfully!', type: 'success' });
        return updatedTags;
      } catch (error) {
        console.error('Error updating trade tags:', error);
        uiStore.showNotification({ message: 'Failed to update tags.', type: 'danger' });
        throw error;
      } finally {
        this.isTradeLoading = false;
      }
    },

    // Helper generico per aggiornare le etichette (Mistakes, Psychology, etc.)
    async _updateTradeLabels(tradeId, labelType, labelIds) {
      this.isTradeLoading = true;
      const uiStore = useUiStore();
      try {
        const response = await apiClient.post(`/trades/${tradeId}/${labelType}`, labelIds);
        const updatedLabels = response.data;
        const stateKey = labelType.replace('-', '_'); // es. 'psychology-states' -> 'psychology_states'

        if (this.selectedTrade && this.selectedTrade.id === tradeId) {
          this.selectedTrade[stateKey] = updatedLabels;
        }

        const index = this.trades.findIndex(t => t.id === tradeId);
        if (index !== -1) {
          this.trades[index][stateKey] = updatedLabels;
        }

        const formattedLabel = labelType.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase());
        uiStore.showNotification({ message: `${formattedLabel} updated successfully!`, type: 'success' });
        return updatedLabels;

      } catch (error) {
        const formattedLabel = labelType.replace('-', ' ');
        console.error(`Error updating trade ${formattedLabel}:`, error);
        uiStore.showNotification({ message: `Failed to update ${formattedLabel}.`, type: 'danger' });
        throw error;
      } finally {
        this.isTradeLoading = false;
      }
    },

    async updateTradeMistakes(tradeId, mistakeIds) {
      return this._updateTradeLabels(tradeId, 'mistakes', mistakeIds);
    },

    async updateTradePsychology(tradeId, psychologyIds) {
      return this._updateTradeLabels(tradeId, 'psychology-states', psychologyIds);
    },

    async updateTradeNewsImpacts(tradeId, newsImpactIds) {
      this.isTradeLoading = true;
      const uiStore = useUiStore();
      try {
        const response = await apiClient.post(`/trades/${tradeId}/news-impacts`, newsImpactIds);
        const updatedImpacts = response.data;

        if (this.selectedTrade && this.selectedTrade.id === tradeId) {
          this.selectedTrade.news_impacts = updatedImpacts;
        }

        const index = this.trades.findIndex(t => t.id === tradeId);
        if (index !== -1) {
          this.trades[index].news_impacts = updatedImpacts;
        }

        uiStore.showNotification({ message: 'News Impacts updated successfully!', type: 'success' });
        return updatedImpacts;
      } catch (error) {
        console.error('Error updating trade news impacts:', error);
        uiStore.showNotification({ message: 'Failed to update news impacts.', type: 'danger' });
        throw error;
      } finally {
        this.isTradeLoading = false;
      }
    },

    async updateTradeRules(tradeId, ruleIds) {
      this.isTradeLoading = true;
      const uiStore = useUiStore();
      try {
        const response = await apiClient.put(`/trades/${tradeId}/rules`, ruleIds);
        const updatedRuleIds = response.data;

        // Fetch the full trade again to get all updated relations
        await this.fetchTradeById(tradeId);

        uiStore.showNotification({ message: 'Playbook rules updated successfully!', type: 'success' });
        return updatedRuleIds;
      } catch (error) {
        console.error('Error updating trade rules:', error);
        uiStore.showNotification({ message: 'Failed to update playbook rules.', type: 'danger' });
        throw error;
      } finally {
        this.isTradeLoading = false;
      }
    },
  },
});