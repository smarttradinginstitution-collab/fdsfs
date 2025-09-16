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
          netPnl: { ...emptyStat('netPnl', 'Net P&L', 'Profitability', '$0.00'), changeType: 'neutral' },
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
          maxDrawdownAbs: emptyStat('maxDrawdownAbs', 'Max Drawdown', 'Risk Management', '$0.00'),
          sharpeRatio: emptyStat('sharpeRatio', 'Sharpe Ratio', 'Ratios & Efficiency'),
          averageHoldTime: emptyStat('averageHoldTime', 'Avg. Hold Time', 'Other', '0 min'),
          recoveryFactor: emptyStat('recoveryFactor', 'Recovery Factor', 'Risk Management'),
          sortinoRatio: emptyStat('sortinoRatio', 'Sortino Ratio', 'Ratios & Efficiency'),
          calmarRatio: emptyStat('calmarRatio', 'Calmar Ratio', 'Ratios & Efficiency'),
          maxDrawdownPct: emptyStat('maxDrawdownPct', 'Max Drawdown %', 'Risk Management', '0.00%'),
          avgSellEfficiency: emptyStat('avgSellEfficiency', 'Avg. Sell Efficiency', 'Ratios & Efficiency', '0.0%'),
          avgTotalEfficiency: emptyStat('avgTotalEfficiency', 'Avg. Total Efficiency', 'Ratios & Efficiency', '0.0%'),
          avgPlannedRr: emptyStat('avgPlannedRr', 'Avg. Planned R:R', 'Ratios & Efficiency'),
          skewness: emptyStat('skewness', 'Skewness', 'Ratios & Efficiency'),
          kurtosis: emptyStat('kurtosis', 'Kurtosis', 'Ratios & Efficiency'),
          var95: emptyStat('var95', 'VaR 95%', 'Risk Management'),
          cvar95: emptyStat('cvar95', 'CVaR 95%', 'Risk Management'),
          averageDrawdown: emptyStat('averageDrawdown', 'Avg. Drawdown', 'Risk Management'),
          longestTradeDuration: emptyStat('longestTradeDuration', 'Longest Trade', 'Other'),
          currentTradeStreak: emptyStat('currentTradeStreak', 'Current Streak', 'Consistency'),
          longsWinPercentage: emptyStat('longsWinPercentage', 'Longs Win %', 'Ratios & Efficiency'),
          shortsWinPercentage: emptyStat('shortsWinPercentage', 'Shorts Win %', 'Ratios & Efficiency'),
        };
      }

      const stats = this.dashboardStats.stats;
      const totalPnl = parseFloat(stats.total_pl);
      const tradeCount = stats.trade_count;
      const winningTrades = stats.winning_trades_count;
      const losingTrades = stats.losing_trades_count;
      const breakEvenTrades = stats.breakeven_trades_count;
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
      const sharpeRatio = parseFloat(stats.sharpe_ratio);
      const averageHoldTime = parseFloat(stats.average_hold_time);
      const recoveryFactor = parseFloat(stats.recovery_factor);
      const sortinoRatio = parseFloat(stats.sortino_ratio);
      const calmarRatio = parseFloat(stats.calmar_ratio);
      const maxDrawdownPct = parseFloat(stats.max_drawdown_pct);
      const avgSellEfficiency = parseFloat(stats.avg_sell_efficiency);
      const avgTotalEfficiency = parseFloat(stats.avg_total_efficiency);
      const avgPlannedRr = parseFloat(stats.avg_planned_rr);
      const skewness = parseFloat(stats.skewness);
      const kurtosis = parseFloat(stats.kurtosis);
      const var95 = parseFloat(stats.var_95);
      const cvar95 = parseFloat(stats.cvar_95);
      const averageDrawdown = parseFloat(stats.average_drawdown);
      const longestTradeDuration = parseFloat(stats.longest_trade_duration);
      const longsWinPercentage = parseFloat(stats.longs_win_percentage);
      const shortsWinPercentage = parseFloat(stats.shorts_win_percentage);

      return {
        netPnl: { key: 'netPnl', label: 'Net P&L', category: 'Profitability', value: `${totalPnl >= 0 ? '+' : ''}$${totalPnl.toFixed(2)}`, changeType: totalPnl >= 0 ? 'positive' : 'negative' },
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
        sortinoRatio: { key: 'sortinoRatio', label: 'Sortino Ratio', category: 'Ratios & Efficiency', value: `${sortinoRatio.toFixed(2)}`, changeType: 'neutral' },
        calmarRatio: { key: 'calmarRatio', label: 'Calmar Ratio', category: 'Ratios & Efficiency', value: `${calmarRatio.toFixed(2)}`, changeType: 'neutral' },
        avgSellEfficiency: { key: 'avgSellEfficiency', label: 'Avg. Sell Efficiency', category: 'Ratios & Efficiency', value: `${avgSellEfficiency.toFixed(1)}%`, changeType: 'neutral' },
        avgTotalEfficiency: { key: 'avgTotalEfficiency', label: 'Avg. Total Efficiency', category: 'Ratios & Efficiency', value: `${avgTotalEfficiency.toFixed(1)}%`, changeType: 'neutral' },
        avgPlannedRr: { key: 'avgPlannedRr', label: 'Avg. Planned R:R', category: 'Ratios & Efficiency', value: `${avgPlannedRr.toFixed(2)}`, changeType: 'neutral' },
        skewness: { key: 'skewness', label: 'Skewness', category: 'Ratios & Efficiency', value: `${skewness.toFixed(2)}`, changeType: 'neutral' },
        kurtosis: { key: 'kurtosis', label: 'Kurtosis', category: 'Ratios & Efficiency', value: `${kurtosis.toFixed(2)}`, changeType: 'neutral' },
        longsWinPercentage: { key: 'longsWinPercentage', label: 'Longs Win %', category: 'Ratios & Efficiency', value: `${longsWinPercentage.toFixed(1)}%`, changeType: 'neutral' },
        shortsWinPercentage: { key: 'shortsWinPercentage', label: 'Shorts Win %', category: 'Ratios & Efficiency', value: `${shortsWinPercentage.toFixed(1)}%`, changeType: 'neutral' },

        maxDrawdownAbs: { key: 'maxDrawdownAbs', label: 'Max Drawdown', category: 'Risk Management', value: `$${maxDrawdownAbs.toFixed(2)}`, changeType: 'neutral' },
        maxDrawdownPct: { key: 'maxDrawdownPct', label: 'Max Drawdown %', category: 'Risk Management', value: `${maxDrawdownPct.toFixed(2)}%`, changeType: 'neutral' },
        recoveryFactor: { key: 'recoveryFactor', label: 'Recovery Factor', category: 'Risk Management', value: `${recoveryFactor.toFixed(2)}`, changeType: 'neutral' },
        var95: { key: 'var95', label: 'VaR 95%', category: 'Risk Management', value: `$${var95.toFixed(2)}`, changeType: 'neutral' },
        cvar95: { key: 'cvar95', label: 'CVaR 95%', category: 'Risk Management', value: `$${cvar95.toFixed(2)}`, changeType: 'neutral' },
        averageDrawdown: { key: 'averageDrawdown', label: 'Avg. Drawdown', category: 'Risk Management', value: `$${averageDrawdown.toFixed(2)}`, changeType: 'neutral' },

        trades: { key: 'trades', label: 'Trades', category: 'Consistency', value: String(tradeCount), changeType: 'neutral' },
        maxConsecutiveWins: { key: 'maxConsecutiveWins', label: 'Max Consec. Wins', category: 'Consistency', value: String(maxConsecutiveWins), changeType: 'neutral' },
        maxConsecutiveLosses: { key: 'maxConsecutiveLosses', label: 'Max Consec. Losses', category: 'Consistency', value: String(maxConsecutiveLosses), changeType: 'neutral' },
        currentTradeStreak: { key: 'currentTradeStreak', label: 'Current Streak', category: 'Consistency', value: String(stats.current_trade_streak), changeType: 'neutral' },

        averageHoldTime: { key: 'averageHoldTime', label: 'Avg. Hold Time', category: 'Other', value: `${averageHoldTime.toFixed(0)} min`, changeType: 'neutral' },
        longestTradeDuration: { key: 'longestTradeDuration', label: 'Longest Trade', category: 'Other', value: `${longestTradeDuration.toFixed(0)} min`, changeType: 'neutral' },
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
