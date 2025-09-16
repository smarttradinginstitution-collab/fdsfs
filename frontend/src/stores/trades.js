// =============================================================================
// FILE: stores/trades.js
// DESCRIZIONE: Store dei trade, refattorizzato per massima efficienza.
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
    processedStats: null,
    equityCurve: null,
    vantageScore: null, // Dati per il VantageScoreWidget
    isLoading: false,
    isSummaryLoading: false,
    activeSummary: null,
  }),

  getters: {
    allStrategies(state) {
      // Ora usa l'elenco dei setup caricato dal backend.
      return ['All', ...state.setups];
    },

    allDashboardStats() {
      if (!this.dashboardStats) {
        const emptyStat = (key, label, category, value = 'N/A') => ({ key, label, category, value, changeType: 'neutral' });
        return {
          // Profitability
          netPnl: { ...emptyStat('netPnl', 'Net P&L', 'Profitability', '$0.00'), changeType: 'neutral' },
          avgWin: emptyStat('avgWin', 'Avg. Win', 'Profitability', '$0.00'),
          avgLoss: emptyStat('avgLoss', 'Avg. Loss', 'Profitability', '$0.00'),
          avgTradePnl: emptyStat('avgTradePnl', 'Avg. Trade P&L', 'Profitability', '$0.00'),
          largestProfit: emptyStat('largestProfit', 'Largest Profit', 'Profitability', '$0.00'),
          largestLoss: emptyStat('largestLoss', 'Largest Loss', 'Profitability', '$0.00'),
          totalPnlLongs: emptyStat('totalPnlLongs', 'Total P&L Longs', 'Profitability', '$0.00'),
          totalPnlShorts: emptyStat('totalPnlShorts', 'Total P&L Shorts', 'Profitability', '$0.00'),

          // Ratios & Efficiency
          winRate: { key: 'winRate', label: 'Win Rate', category: 'Ratios & Efficiency', value: 'N/A', wins: 0, losses: 0, breakevens: 0, changeType: 'neutral' },
          profitFactor: emptyStat('profitFactor', 'Profit Factor', 'Ratios & Efficiency'),
          expectancy: emptyStat('expectancy', 'Expectancy', 'Ratios & Efficiency', '$0.00'),
          avgRealizedRr: emptyStat('avgRealizedRr', 'Avg. Realized R:R', 'Ratios & Efficiency'),
          sharpeRatio: emptyStat('sharpeRatio', 'Sharpe Ratio', 'Ratios & Efficiency'),
          sortinoRatio: emptyStat('sortinoRatio', 'Sortino Ratio', 'Ratios & Efficiency'),
          calmarRatio: emptyStat('calmarRatio', 'Calmar Ratio', 'Ratios & Efficiency'),
          sellEfficiency: emptyStat('sellEfficiency', 'Sell Efficiency', 'Ratios & Efficiency', 'N/A%'),
          totalEfficiency: emptyStat('totalEfficiency', 'Total Efficiency', 'Ratios & Efficiency', 'N/A%'),
          plannedRr: emptyStat('plannedRr', 'Planned R:R', 'Ratios & Efficiency'),

          // Risk Management
          maxDrawdownAbs: emptyStat('maxDrawdownAbs', 'Max Drawdown', 'Risk Management', '$0.00'),
          maxDrawdownPercent: emptyStat('maxDrawdownPercent', 'Max Drawdown %', 'Risk Management', 'N/A%'),
          recoveryFactor: emptyStat('recoveryFactor', 'Recovery Factor', 'Risk Management'),
          var95: emptyStat('var95', 'Value at Risk (95%)', 'Risk Management', '$0.00'),
          cvar95: emptyStat('cvar95', 'Cond. VaR (95%)', 'Risk Management', '$0.00'),

          // Consistency
          trades: emptyStat('trades', 'Trades', 'Consistency', '0'),
          maxConsecutiveWins: emptyStat('maxConsecutiveWins', 'Max Consec. Wins', 'Consistency', '0'),
          maxConsecutiveLosses: emptyStat('maxConsecutiveLosses', 'Max Consec. Losses', 'Consistency', '0'),
          winningTradesCount: emptyStat('winningTradesCount', 'Winning Trades', 'Consistency', '0'),
          losingTradesCount: emptyStat('losingTradesCount', 'Losing Trades', 'Consistency', '0'),
          breakevenTradesCount: emptyStat('breakevenTradesCount', 'Breakeven Trades', 'Consistency', '0'),
          longsCount: emptyStat('longsCount', 'Longs', 'Consistency', '0'),
          shortsCount: emptyStat('shortsCount', 'Shorts', 'Consistency', '0'),

          // Other
          averageHoldTime: emptyStat('averageHoldTime', 'Avg. Hold Time', 'Other', '0 min'),
          skewness: emptyStat('skewness', 'Skewness', 'Other'),
          kurtosis: emptyStat('kurtosis', 'Kurtosis', 'Other'),
        };
      }

      const stats = this.dashboardStats.stats;
      const {
        total_pl,
        trade_count,
        winning_trades_count,
        losing_trades_count,
        breakeven_trades_count,
        win_rate,
        avg_win,
        avg_loss,
        expectancy,
        average_trade_pnl,
        largest_profit,
        largest_loss,
        max_consecutive_wins,
        max_consecutive_losses,
        avg_realized_rr,
        max_drawdown_abs,
        max_drawdown_percent,
        sharpe_ratio,
        sortino_ratio,
        calmar_ratio,
        recovery_factor,
        average_hold_time,
        profit_factor_label,
        var_95,
        cvar_95,
        total_pnl_longs,
        total_pnl_shorts,
        longs_count,
        shorts_count,
        sell_efficiency,
        total_efficiency,
        planned_rr,
        skewness,
        kurtosis
      } = stats;

      return {
        // Profitability
        netPnl: { key: 'netPnl', label: 'Net P&L', category: 'Profitability', value: `${total_pl >= 0 ? '+' : ''}$${total_pl.toFixed(2)}`, changeType: total_pl >= 0 ? 'positive' : 'negative' },
        avgWin: { key: 'avgWin', label: 'Avg. Win', category: 'Profitability', value: `$${avg_win.toFixed(2)}`, changeType: 'neutral' },
        avgLoss: { key: 'avgLoss', label: 'Avg. Loss', category: 'Profitability', value: `$${avg_loss.toFixed(2)}`, changeType: 'neutral' },
        avgTradePnl: { key: 'avgTradePnl', label: 'Avg. Trade P&L', category: 'Profitability', value: `$${average_trade_pnl.toFixed(2)}`, changeType: 'neutral' },
        largestProfit: { key: 'largestProfit', label: 'Largest Profit', category: 'Profitability', value: `$${largest_profit.toFixed(2)}`, changeType: 'neutral' },
        largestLoss: { key: 'largestLoss', label: 'Largest Loss', category: 'Profitability', value: `$${largest_loss.toFixed(2)}`, changeType: 'neutral' },
        totalPnlLongs: { key: 'totalPnlLongs', label: 'Total P&L Longs', category: 'Profitability', value: `$${total_pnl_longs.toFixed(2)}`, changeType: 'neutral' },
        totalPnlShorts: { key: 'totalPnlShorts', label: 'Total P&L Shorts', category: 'Profitability', value: `$${total_pnl_shorts.toFixed(2)}`, changeType: 'neutral' },

        // Ratios & Efficiency
        winRate: { key: 'winRate', label: 'Win Rate', category: 'Ratios & Efficiency', value: `${win_rate.toFixed(1)}%`, wins: winning_trades_count, losses: losing_trades_count, breakevens: breakeven_trades_count, changeType: 'neutral' },
        profitFactor: { key: 'profitFactor', label: 'Profit Factor', category: 'Ratios & Efficiency', value: profit_factor_label, changeType: 'neutral' },
        expectancy: { key: 'expectancy', label: 'Expectancy', category: 'Ratios & Efficiency', value: `$${expectancy.toFixed(2)}`, changeType: 'neutral' },
        avgRealizedRr: { key: 'avgRealizedRr', label: 'Avg. Realized R:R', category: 'Ratios & Efficiency', value: `${avg_realized_rr.toFixed(2)}`, changeType: 'neutral' },
        sharpeRatio: { key: 'sharpeRatio', label: 'Sharpe Ratio', category: 'Ratios & Efficiency', value: `${sharpe_ratio.toFixed(2)}`, changeType: 'neutral' },
        sortinoRatio: { key: 'sortinoRatio', label: 'Sortino Ratio', category: 'Ratios & Efficiency', value: `${sortino_ratio.toFixed(2)}`, changeType: 'neutral' },
        calmarRatio: { key: 'calmarRatio', label: 'Calmar Ratio', category: 'Ratios & Efficiency', value: `${calmar_ratio.toFixed(2)}`, changeType: 'neutral' },
        sellEfficiency: { key: 'sellEfficiency', label: 'Sell Efficiency', category: 'Ratios & Efficiency', value: `${(sell_efficiency * 100).toFixed(1)}%`, changeType: 'neutral' },
        totalEfficiency: { key: 'totalEfficiency', label: 'Total Efficiency', category: 'Ratios & Efficiency', value: `${(total_efficiency * 100).toFixed(1)}%`, changeType: 'neutral' },
        plannedRr: { key: 'plannedRr', label: 'Planned R:R', category: 'Ratios & Efficiency', value: `${planned_rr.toFixed(2)}`, changeType: 'neutral' },

        // Risk Management
        maxDrawdownAbs: { key: 'maxDrawdownAbs', label: 'Max Drawdown', category: 'Risk Management', value: `$${max_drawdown_abs.toFixed(2)}`, changeType: 'neutral' },
        maxDrawdownPercent: { key: 'maxDrawdownPercent', label: 'Max Drawdown %', category: 'Risk Management', value: `${max_drawdown_percent.toFixed(2)}%`, changeType: 'neutral' },
        recoveryFactor: { key: 'recoveryFactor', label: 'Recovery Factor', 'category': 'Risk Management', value: `${recovery_factor.toFixed(2)}`, changeType: 'neutral' },
        var95: { key: 'var95', label: 'Value at Risk (95%)', category: 'Risk Management', value: `$${var_95.toFixed(2)}`, changeType: 'neutral' },
        cvar95: { key: 'cvar95', label: 'Cond. VaR (95%)', category: 'Risk Management', value: `$${cvar_95.toFixed(2)}`, changeType: 'neutral' },

        // Consistency
        trades: { key: 'trades', label: 'Trades', category: 'Consistency', value: String(trade_count), changeType: 'neutral' },
        maxConsecutiveWins: { key: 'maxConsecutiveWins', label: 'Max Consec. Wins', category: 'Consistency', value: String(max_consecutive_wins), changeType: 'neutral' },
        maxConsecutiveLosses: { key: 'maxConsecutiveLosses', 'label': 'Max Consec. Losses', 'category': 'Consistency', value: String(max_consecutive_losses), changeType: 'neutral' },
        winningTradesCount: { key: 'winningTradesCount', label: 'Winning Trades', category: 'Consistency', value: String(winning_trades_count), changeType: 'neutral' },
        losingTradesCount: { key: 'losingTradesCount', label: 'Losing Trades', category: 'Consistency', value: String(losing_trades_count), changeType: 'neutral' },
        breakevenTradesCount: { key: 'breakevenTradesCount', label: 'Breakeven Trades', category: 'Consistency', value: String(breakeven_trades_count), changeType: 'neutral' },
        longsCount: { key: 'longsCount', label: 'Longs', category: 'Consistency', value: String(longs_count), changeType: 'neutral' },
        shortsCount: { key: 'shortsCount', label: 'Shorts', category: 'Consistency', value: String(shorts_count), changeType: 'neutral' },

        // Other
        averageHoldTime: { key: 'averageHoldTime', label: 'Avg. Hold Time', category: 'Other', value: `${average_hold_time.toFixed(0)} min`, changeType: 'neutral' },
        skewness: { key: 'skewness', label: 'Skewness', category: 'Other', value: `${skewness.toFixed(2)}`, changeType: 'neutral' },
        kurtosis: { key: 'kurtosis', label: 'Kurtosis', category: 'Other', value: `${kurtosis.toFixed(2)}`, changeType: 'neutral' },
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
      { key: 'symbol', text: 'Ticker' },
      { key: 'direction', text: 'Side' },
      { key: 'p_l', text: 'Net P&L' },
      { key: 'entry_timestamp', text: 'Date' },
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

      // Usa sempre i filtri globali dello store
      const _startDate = filterStore.startDate;
      const _endDate = filterStore.endDate;
      const _strategy = filterStore.selectedStrategy;

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
        user_id: userId,
        start_date: toYYYYMMDD(_startDate),
        end_date: toYYYYMMDD(_endDate),
        user_timezone: userTimezone,
      };

      if (_strategy && _strategy.toLowerCase() !== 'all') {
        params.setups = [_strategy];
      }

      try {
        const response = await apiClient.get('/api/v1/trades/', { params });
        this.trades = response.data.map(mapBackendTradeToFrontend);
      } catch (error) {
        console.error('Errore nel recupero dei trade:', error);
        this.trades = [];
      } finally {
        this.isLoading = false;
      }
    },

    async fetchTradeSummary(dateRange) {
      this.isSummaryLoading = true;
      this.activeSummary = null;

      const authStore = useAuthStore();
      const filterStore = useFilterStore();
      const userId = authStore.user?.id;
      if (!userId) {
        console.error("Utente non autenticato per il riepilogo.");
        this.isSummaryLoading = false;
        return;
      }

      const toYYYYMMDD = (date) => {
        if (!date) return null;
        const d = new Date(date);
        return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
      };

      const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
      const params = {
        user_id: userId,
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
          apiClient.get('/api/v1/trades/summary', { params }),
          apiClient.get('/api/v1/trades/', { params })
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
      const authStore = useAuthStore();
      const filterStore = useFilterStore();
      const userId = authStore.user?.id;

      if (!userId) {
        console.error('User not authenticated, cannot fetch dashboard stats.');
        return;
      }

      const params = {
        user_id: userId,
        start_date: filterStore.startDate?.toISOString().split('T')[0],
        end_date: filterStore.endDate?.toISOString().split('T')[0],
      };

      if (filterStore.selectedStrategy && filterStore.selectedStrategy.toLowerCase() !== 'all') {
        params.setups = [filterStore.selectedStrategy];
      }

      try {
        const response = await apiClient.get('/api/v1/trades/performance/metrics', { params });
        this.dashboardStats = response.data;
      } catch (error) {
        console.error('Error fetching dashboard stats:', error);
      }
    },

    async fetchCalendarData() {
      const authStore = useAuthStore();
      const filterStore = useFilterStore();
      const userId = authStore.user?.id;

      if (!userId) {
        console.error('User not authenticated, cannot fetch calendar data.');
        return;
      }

      // Rileva il fuso orario IANA del browser dell'utente.
      const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

      const params = {
        user_id: userId,
        start_date: filterStore.startDate?.toISOString().split('T')[0],
        end_date: filterStore.endDate?.toISOString().split('T')[0],
        user_timezone: userTimezone, // Aggiungi il fuso orario alla richiesta
      };

      if (filterStore.selectedStrategy && filterStore.selectedStrategy.toLowerCase() !== 'all') {
        params.setups = [filterStore.selectedStrategy];
      }

      try {
        const response = await apiClient.get('/api/v1/trades/calendar/data', { params });
        this.calendarData = response.data;
      } catch (error) {
        console.error('Error fetching calendar data:', error);
      }
    },

    async fetchVantageScore() {
      const authStore = useAuthStore();
      const filterStore = useFilterStore();
      const userId = authStore.user?.id;
      if (!userId) return;

      const params = {
        user_id: userId,
        start_date: filterStore.startDate?.toISOString().split('T')[0],
        end_date: filterStore.endDate?.toISOString().split('T')[0],
      };
      if (filterStore.selectedStrategy && filterStore.selectedStrategy.toLowerCase() !== 'all') {
        params.setups = [filterStore.selectedStrategy];
      }

      try {
        const response = await apiClient.get('/api/v1/trades/vantage-score', { params });
        this.vantageScore = response.data;
      } catch (error) {
        console.error('Error fetching vantage score:', error);
        this.vantageScore = null;
      }
    },

    async addTrade(tradeData) {
      this.isLoading = true;
      try {
        const authStore = useAuthStore();
        const userId = authStore.user?.id;

        if (!userId) {
          console.error('User not authenticated, cannot add trade.');
          throw new Error('User not authenticated');
        }

        // Mappa i dati dal form al payload atteso dal backend
        const payload = {
          symbol: tradeData.ticker,
          p_l: tradeData.pnl,
          setup: tradeData.setup,
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
          mistakes: tradeData.mistakes,
          tags: tradeData.tags,
        };

        // Rimuovi le chiavi con valori null o undefined per non inviarle al backend
        Object.keys(payload).forEach(key => {
          if (payload[key] === null || payload[key] === undefined || payload[key] === '') {
            delete payload[key];
          }
        });

        // L'URL ora termina con una slash per evitare il redirect 307 di FastAPI
        const response = await apiClient.post(
          `/api/v1/trades/?user_id=${userId}`,
          payload
        );

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
      const authStore = useAuthStore();
      const filterStore = useFilterStore();
      const userId = authStore.user?.id;
      if (!userId) return;

      const params = {
        user_id: userId,
        start_date: filterStore.startDate?.toISOString().split('T')[0],
        end_date: filterStore.endDate?.toISOString().split('T')[0],
      };
      if (filterStore.selectedStrategy && filterStore.selectedStrategy.toLowerCase() !== 'all') {
        params.setups = [filterStore.selectedStrategy];
      }

      try {
        const response = await apiClient.get('/api/v1/trades/processed-stats', { params });
        this.processedStats = response.data;
      } catch (error) {
        console.error('Error fetching processed stats:', error);
        this.processedStats = null;
      }
    },

    async fetchEquityCurve() {
      const authStore = useAuthStore();
      const filterStore = useFilterStore();
      const userId = authStore.user?.id;
      if (!userId) return;

      const params = {
        user_id: userId,
        start_date: filterStore.startDate?.toISOString().split('T')[0],
        end_date: filterStore.endDate?.toISOString().split('T')[0],
      };
      if (filterStore.selectedStrategy && filterStore.selectedStrategy.toLowerCase() !== 'all') {
        params.setups = [filterStore.selectedStrategy];
      }

      try {
        const response = await apiClient.get('/api/v1/trades/equity-curve', { params });
        this.equityCurve = response.data;
      } catch (error) {
        console.error('Error fetching equity curve:', error);
        this.equityCurve = null;
      }
    },

    /**
     * Azione master per caricare tutti i dati della dashboard in parallelo.
     */
    async fetchAllDataForDashboard() {
      this.isLoading = true;
      try {
        await Promise.allSettled([
          this.fetchTrades(),
          this.fetchDashboardStats(),
          this.fetchCalendarData(),
          this.fetchProcessedStats(),
          this.fetchEquityCurve(),
          this.fetchSetups(),
          this.fetchVantageScore(),
        ]);
      } finally {
        this.isLoading = false;
      }
    },
  },
});
