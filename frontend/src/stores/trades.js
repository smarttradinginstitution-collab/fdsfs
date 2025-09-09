// =============================================================================
// FILE: stores/trades.js
// DESCRIZIONE: Store dei trade, refattorizzato per massima efficienza.
// =============================================================================

import { defineStore } from 'pinia';
import { useFilterStore } from './filterStore';
import { useAuthStore } from './auth';
import apiClient from '../services/api';
import { localDateTimeStringToUTCISO } from '@/utils/date.js';

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
    isSummaryLoading: false,
    activeSummary: null,
  }),

  getters: {
    allStrategies(state) {
      // Ora usa l'elenco dei setup caricato dal backend.
      return ['All', ...state.setups];
    },

    filteredTrades: (state) => {
      const filterStore = useFilterStore();
      let trades = state.trades;
      if (filterStore.startDate && filterStore.endDate) {
        const start = new Date(filterStore.startDate).setHours(0, 0, 0, 0);
        const end = new Date(filterStore.endDate).setHours(23, 59, 59, 999);
        trades = trades.filter(trade => {
          const tradeDate = new Date(trade.date);
          return tradeDate >= start && tradeDate <= end;
        });
      }
      if (filterStore.selectedStrategy && filterStore.selectedStrategy !== 'all') {
        trades = trades.filter(trade => trade.strategy === filterStore.selectedStrategy);
      }
      return trades;
    },

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
        // Usiamo i componenti della data locale per creare la chiave,
        // in modo che un trade delle 00:05 del 9 settembre (ora locale)
        // venga correttamente raggruppato sotto il 9 settembre, anche se in UTC
        // potrebbe essere ancora l'8 settembre.
        const year = tradeDate.getFullYear();
        const month = String(tradeDate.getMonth() + 1).padStart(2, '0');
        const day = String(tradeDate.getDate()).padStart(2, '0');
        const dayKey = `${year}-${month}-${day}`;

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
        };
      }

      const stats = this.dashboardStats.stats;
      const totalPnl = parseFloat(stats.total_pl);
      const tradeCount = stats.trade_count;
      const winningTrades = stats.winning_trades_count;
      const losingTrades = stats.losing_trades_count;
      const breakEvenTrades = stats.breakeven_trades_count;
      const winRate = parseFloat(stats.win_rate);
      const profitFactor = parseFloat(stats.profit_factor);
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

      return {
        netPnl: { key: 'netPnl', label: 'Net P&L', category: 'Profitability', value: `${totalPnl >= 0 ? '+' : ''}$${totalPnl.toFixed(2)}`, changeType: totalPnl >= 0 ? 'positive' : 'negative' },
        avgWin: { key: 'avgWin', label: 'Avg. Win', category: 'Profitability', value: `$${avgWin.toFixed(2)}`, changeType: 'neutral' },
        avgLoss: { key: 'avgLoss', label: 'Avg. Loss', category: 'Profitability', value: `$${avgLoss.toFixed(2)}`, changeType: 'neutral' },
        avgTradePnl: { key: 'avgTradePnl', label: 'Avg. Trade P&L', category: 'Profitability', value: `$${avgTradePnl.toFixed(2)}`, changeType: 'neutral' },
        largestProfit: { key: 'largestProfit', label: 'Largest Profit', category: 'Profitability', value: `$${largestProfit.toFixed(2)}`, changeType: 'neutral' },
        largestLoss: { key: 'largestLoss', label: 'Largest Loss', category: 'Profitability', value: `$${largestLoss.toFixed(2)}`, changeType: 'neutral' },

        winRate: { key: 'winRate', label: 'Win Rate', category: 'Ratios & Efficiency', value: `${winRate.toFixed(1)}%`, wins: winningTrades, losses: losingTrades, breakevens: breakEvenTrades, changeType: 'neutral' },
        profitFactor: { key: 'profitFactor', label: 'Profit Factor', category: 'Ratios & Efficiency', value: profitFactor === Infinity ? '∞' : profitFactor.toFixed(2), changeType: 'neutral' },
        expectancy: { key: 'expectancy', label: 'Expectancy', category: 'Ratios & Efficiency', value: `$${expectancy.toFixed(2)}`, changeType: 'neutral' },
        avgRealizedRr: { key: 'avgRealizedRr', label: 'Avg. Realized R:R', category: 'Ratios & Efficiency', value: `${avgRealizedRr.toFixed(2)}`, changeType: 'neutral' },
        sharpeRatio: { key: 'sharpeRatio', label: 'Sharpe Ratio', category: 'Ratios & Efficiency', value: `${sharpeRatio.toFixed(2)}`, changeType: 'neutral' },

        maxDrawdownAbs: { key: 'maxDrawdownAbs', label: 'Max Drawdown', category: 'Risk Management', value: `$${maxDrawdownAbs.toFixed(2)}`, changeType: 'neutral' },

        trades: { key: 'trades', label: 'Trades', category: 'Consistency', value: String(tradeCount), changeType: 'neutral' },
        maxConsecutiveWins: { key: 'maxConsecutiveWins', label: 'Max Consec. Wins', category: 'Consistency', value: String(maxConsecutiveWins), changeType: 'neutral' },
        maxConsecutiveLosses: { key: 'maxConsecutiveLosses', label: 'Max Consec. Losses', category: 'Consistency', value: String(maxConsecutiveLosses), changeType: 'neutral' },

        averageHoldTime: { key: 'averageHoldTime', label: 'Avg. Hold Time', category: 'Other', value: `${averageHoldTime.toFixed(0)} min`, changeType: 'neutral' },
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

      // Aggiungi giorni placeholder all'inizio
      for (let i = 0; i < offset; i++) {
        calendarDays.push({ isPlaceholder: true, key: `ph-start-${i}` });
      }

      // Aggiungi i giorni del mese
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

      // Completa l'ultima settimana con placeholder
      while (calendarDays.length % 7 !== 0) {
        calendarDays.push({ isPlaceholder: true, key: `ph-end-${calendarDays.length}` });
      }

      const weeksOfDays = [];
      const weeklySummaries = [];
      for (let i = 0; i < calendarDays.length; i += 7) {
        const weekChunk = calendarDays.slice(i, i + 7);
        weeksOfDays.push(weekChunk);

        const weeklyPnl = weekChunk.reduce((sum, day) => sum + (day.dailyData?.totalPnl || 0), 0);
        const tradingDaysCount = weekChunk.filter(day => !day.isPlaceholder && day.dailyData.tradeCount > 0).length;

        weeklySummaries.push({
          weekNumber: (i / 7) + 1,
          totalPnl: weeklyPnl,
          tradingDaysCount: tradingDaysCount,
        });
      }

      return { weeksOfDays, weeklySummaries };
    },

    strategyPerformanceData() {
      const rawData = this.processedData.performanceByStrategy;
      if (Object.keys(rawData).length === 0) return [];
      const maxPnl = Math.max(...Object.values(rawData).map(stat => Math.abs(stat.totalPnl)));
      return Object.entries(rawData).map(([strategy, stats]) => {
        const winRate = stats.tradeCount > 0 ? (stats.winningTrades / stats.tradeCount) * 100 : 0;
        return {
          label: strategy,
          value: `${stats.tradeCount} trades | ${winRate.toFixed(0)}% WR | $${stats.totalPnl.toFixed(2)}`,
          barWidth: maxPnl > 0 ? `${(Math.abs(stats.totalPnl) / maxPnl) * 100}%` : '0%',
          isPositive: stats.totalPnl >= 0,
        };
      });
    },

    performanceByDayOfWeek() {
        return this.processedData.performanceByDayOfWeek;
    },

    winLossDays(state) {
      if (!this.processedData.winLossDaysStats) {
        return { winningDays: 0, losingDays: 0, breakEvenDays: 0 };
      }
      return this.processedData.winLossDaysStats;
    },

    equityCurveData(state) {
      if (this.filteredTrades.length === 0) return { labels: [], data: [] };
      const sortedTrades = [...this.filteredTrades].sort((a, b) => new Date(a.date) - new Date(b.date));
      let cumulativePnl = 0;
      const dataPoints = sortedTrades.map(trade => {
        cumulativePnl += trade.pnl;
        return { date: trade.date, pnl: cumulativePnl };
      });
      return { labels: dataPoints.map(p => p.date), data: dataPoints.map(p => p.pnl) };
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

      if (isNaN(viewDate.getTime())) return { monthLabel: 'Invalid Date', monthlyPnl: 0 };

      const monthLabel = viewDate.toLocaleString('en-US', { month: 'long', year: 'numeric' });
      let monthlyPnl = 0;
      for (const trade of this.filteredTrades) {
        const tradeDate = new Date(trade.date);
        if (tradeDate.getFullYear() === viewDate.getFullYear() && tradeDate.getMonth() === viewDate.getMonth()) {
          monthlyPnl += trade.pnl;
        }
      }
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
    async fetchTrades(dateRange = null) {
      // Se è una richiesta per un intervallo specifico, usa isSummaryLoading, altrimenti isLoading.
      if (dateRange) {
        this.isSummaryLoading = true;
        this.activeSummary = null;
      } else {
        this.isLoading = true;
      }

      const authStore = useAuthStore();
      const filterStore = useFilterStore();
      const userId = authStore.user?.id;

      if (!userId) {
        console.error("Utente non autenticato.");
        this.isLoading = false;
        this.isSummaryLoading = false;
        return;
      }

      // Determina quali filtri usare: quelli passati come argomento o quelli globali
      const _startDate = dateRange ? dateRange.startDate : filterStore.startDate;
      const _endDate = dateRange ? dateRange.endDate : filterStore.endDate;

      // Applica il filtro per strategia solo se non stiamo chiedendo un intervallo di date specifico
      const _strategy = dateRange ? null : filterStore.selectedStrategy;

      const params = {
        user_id: userId,
        start_date: _startDate?.toISOString(),
        end_date: _endDate?.toISOString(),
      };

      if (_strategy && _strategy.toLowerCase() !== 'all') {
        params.setups = [_strategy];
      }

      try {
        const response = await apiClient.get('/api/v1/trades/', { params });
        const fetchedTrades = response.data.map(mapBackendTradeToFrontend);

        if (dateRange) {
          // Se la richiesta era per un intervallo specifico, calcola il riepilogo per quel periodo.
          const summary = {
            startDate: dateRange.startDate,
            endDate: dateRange.endDate,
            trades: fetchedTrades,
            stats: {
              netPnl: 0,
              tradeCount: 0,
              winningTrades: 0,
              losingTrades: 0,
              profitFactor: 0,
              grossProfit: 0,
              grossLoss: 0,
            },
            cumulativePnlForChart: { labels: ['Start'], data: [0] }
          };

          if (fetchedTrades.length > 0) {
            let cumulativePnl = 0;
            for (const trade of fetchedTrades) {
              const pnl = trade.pnl || 0;
              summary.stats.netPnl += pnl;
              summary.stats.tradeCount++;
              if (pnl > 0) {
                summary.stats.winningTrades++;
                summary.stats.grossProfit += pnl;
              } else if (pnl < 0) {
                summary.stats.losingTrades++;
                summary.stats.grossLoss += Math.abs(pnl);
              }
              cumulativePnl += pnl;
              summary.cumulativePnlForChart.data.push(cumulativePnl);
              summary.cumulativePnlForChart.labels.push(trade.ticker);
            }
            summary.stats.profitFactor = summary.stats.grossLoss > 0
              ? summary.stats.grossProfit / summary.stats.grossLoss
              : (summary.stats.grossProfit > 0 ? Infinity : 0);
          }
          this.activeSummary = summary;

        } else {
          // Altrimenti, aggiorna la lista principale dei trade per la dashboard
          this.trades = fetchedTrades;
        }

      } catch (error) {
        console.error('Errore nel recupero dei trade:', error);
        if (dateRange) {
          this.activeSummary = { error: 'Failed to load summary.' };
        } else {
          this.trades = [];
        }
      } finally {
        this.isLoading = false;
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
        start_date: filterStore.startDate?.toISOString(),
        end_date: filterStore.endDate?.toISOString(),
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

      const params = {
        user_id: userId,
        start_date: filterStore.startDate?.toISOString(),
        end_date: filterStore.endDate?.toISOString(),
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
          entry_timestamp: localDateTimeStringToUTCISO(tradeData.entry_timestamp),
          exit_timestamp: localDateTimeStringToUTCISO(tradeData.exit_timestamp),
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
  },
});
