// =============================================================================
// FILE: stores/trades.js
// DESCRIZIONE: Store dei trade, refattorizzato per massima efficienza.
// Utilizza un unico getter memoizzato (`processedData`) per calcolare tutte
// le statistiche in un singolo ciclo, migliorando drasticamente le performance.
// =============================================================================

import { defineStore } from 'pinia';
import { useFilterStore } from './filterStore'; // Verrà creato nel prossimo step

export const useTradesStore = defineStore('trades', {
  state: () => ({
    trades: [
      // Dati di esempio
      { id: 1, ticker: 'AAPL', type: 'Long', pnl: 150.75, date: '2025-08-28', strategy: 'Breakout', risk: 50 },
      { id: 2, ticker: 'TSLA', type: 'Short', pnl: -75.20, date: '2025-08-28', strategy: 'Reversal', risk: 50 },
      { id: 3, ticker: 'NVDA', type: 'Long', pnl: 278.40, date: '2025-08-27', strategy: 'Breakout', risk: 100 },
      { id: 4, ticker: 'GOOG', type: 'Long', pnl: 121.00, date: '2025-08-20', strategy: 'Momentum', risk: 60 },
      { id: 5, ticker: 'MSFT', type: 'Long', pnl: 88.50, date: '2025-08-15', strategy: 'Reversal', risk: 40 },
      { id: 6, ticker: 'AMD', type: 'Short', pnl: -42.10, date: '2025-08-10', strategy: 'Breakout', risk: 40 },
      { id: 7, ticker: 'META', type: 'Long', pnl: 210.00, date: '2025-07-30', strategy: 'Momentum', risk: 70 },
    ],
  }),

  getters: {
    /**
     * Estrae un elenco di tutte le strategie uniche da tutti i trade.
     * Utile per popolare i menu a tendina dei filtri.
     */
    allStrategies(state) {
      const strategies = new Set(state.trades.map(trade => trade.strategy).filter(Boolean));
      // Restituiamo un array con "All" come prima opzione, per permettere di deselezionare il filtro.
      return ['All', ...Array.from(strategies)];
    },

    // 1. Il primo getter filtra i trade in base allo store dei filtri.
    filteredTrades: (state) => {
      const filterStore = useFilterStore();

      // Iniziamo con tutti i trade
      let trades = state.trades;

      // 1. Applichiamo il filtro per data
      // Accesso diretto alle proprietà dello store per garantire la reattività.
      // Pinia unwrappa automaticamente i .value all'interno dei getters.
      if (filterStore.startDate && filterStore.endDate) {
        const start = new Date(filterStore.startDate).setHours(0, 0, 0, 0);
        const end = new Date(filterStore.endDate).setHours(23, 59, 59, 999);
        trades = trades.filter(trade => {
          const tradeDate = new Date(trade.date);
          return tradeDate >= start && tradeDate <= end;
        });
      }

      // 2. Applichiamo il filtro per strategia
      if (filterStore.selectedStrategy && filterStore.selectedStrategy !== 'all') {
        trades = trades.filter(trade => trade.strategy === filterStore.selectedStrategy);
      }

      return trades;
    },

    // 2. IL GETTER "MASTER": Esegue un singolo ciclo per calcolare tutto.
    processedData(state) {
      const trades = this.filteredTrades;
      const filterStore = useFilterStore();
      const viewDateForCalendar = new Date(filterStore.endDate);

      // Inizializziamo gli accumulatori
      const stats = {
        totalPnl: 0,
        tradeCount: 0,
        winningTrades: 0,
        losingTrades: 0,
        breakEvenTrades: 0,
        grossProfit: 0,
        grossLoss: 0,
        totalRisk: 0,
      };
      const dailyDataForCalendar = {};
      const performanceByStrategy = {};
      const performanceByDayOfWeek = {};
      const pnlByDay = {}; // <-- Nuovo accumulatore
      const daysOfWeek = ['Domenica', 'Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato'];
      daysOfWeek.forEach(day => {
        performanceByDayOfWeek[day] = { totalPnl: 0, tradeCount: 0, winningTrades: 0 };
      });

      // Singolo ciclo sui trade filtrati
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

        // --- NUOVA LOGICA: Calcolo P&L per giorno (per il report Win/Loss Days) ---
        if (!pnlByDay[dayKey]) {
          pnlByDay[dayKey] = 0;
        }
        pnlByDay[dayKey] += trade.pnl;

        // Calcoli per il calendario heatmap
        if (tradeDate.getFullYear() === viewDateForCalendar.getFullYear() && tradeDate.getMonth() === viewDateForCalendar.getMonth()) {
          if (!dailyDataForCalendar[dayKey]) {
            dailyDataForCalendar[dayKey] = { totalPnl: 0, tradeCount: 0, winningTrades: 0 };
          }
          dailyDataForCalendar[dayKey].totalPnl += trade.pnl;
          dailyDataForCalendar[dayKey].tradeCount++;
          if (trade.pnl > 0) dailyDataForCalendar[dayKey].winningTrades++;
        }

        // Raggruppamento per strategia
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

      // --- NUOVA LOGICA: Post-elaborazione per il report Win/Loss Days ---
      const winLossDaysStats = { winningDays: 0, losingDays: 0, breakEvenDays: 0 };
      for (const dayPnl of Object.values(pnlByDay)) {
        if (dayPnl > 0) {
          winLossDaysStats.winningDays++;
        } else if (dayPnl < 0) {
          winLossDaysStats.losingDays++;
        } else {
          winLossDaysStats.breakEvenDays++;
        }
      }

      return {
        stats,
        dailyDataForCalendar,
        performanceByStrategy,
        performanceByDayOfWeek,
        winLossDaysStats,
        recentTrades: trades.slice(0, 4),
      };
    },

    // 3. I getter successivi diventano semplici "selettori" dei dati già processati.

    recentTrades() {
      return this.processedData.recentTrades;
    },

    allDashboardStats() {
      const { stats, winLossDaysStats } = this.processedData;
      const { totalPnl, tradeCount, winningTrades, losingTrades, breakEvenTrades, grossProfit, grossLoss } = stats;

      if (tradeCount === 0) {
        // Ritorna lo stato di default
        return {
          netPnl: { key: 'netPnl', label: 'Net P&L', value: '$0.00', changeType: 'neutral' },
          winRate: { key: 'winRate', label: 'Win Rate', value: 'N/A', wins: 0, losses: 0, breakevens: 0, changeType: 'neutral' },
          trades: { key: 'trades', label: 'Trades', value: '0', changeType: 'neutral' },
          profitFactor: { key: 'profitFactor', label: 'Profit Factor', value: 'N/A', changeType: 'neutral' },
          avgWin: { key: 'avgWin', label: 'Avg. Win', value: '$0.00', changeType: 'neutral' },
          avgLoss: { key: 'avgLoss', label: 'Avg. Loss', value: '$0.00', changeType: 'neutral' },
          expectancy: { key: 'expectancy', label: 'Expectancy', value: '$0.00', changeType: 'neutral' },
        };
      }

      const winRate = (winningTrades / tradeCount) * 100;
      const lossRate = 1 - (winRate / 100);
      const profitFactor = grossLoss > 0 ? grossProfit / grossLoss : Infinity;
      const avgWin = winningTrades > 0 ? grossProfit / winningTrades : 0;
      const avgLoss = (tradeCount - winningTrades) > 0 ? grossLoss / (tradeCount - winningTrades) : 0;
      const expectancy = (winRate / 100 * avgWin) - (lossRate * avgLoss);

      return {
        netPnl: { key: 'netPnl', label: 'Net P&L', value: `${totalPnl >= 0 ? '+' : ''}$${totalPnl.toFixed(2)}`, changeType: totalPnl >= 0 ? 'positive' : 'negative' },
        winRate: {
          key: 'winRate',
          label: 'Win Rate',
          value: `${winRate.toFixed(1)}%`,
          wins: winningTrades,
          losses: losingTrades,
          breakevens: breakEvenTrades,
          changeType: 'positive'
        },
        trades: { key: 'trades', label: 'Trades', value: String(tradeCount), changeType: 'neutral' },
        profitFactor: { key: 'profitFactor', label: 'Profit Factor', value: profitFactor === Infinity ? '∞' : profitFactor.toFixed(2), changeType: profitFactor > 1 ? 'positive' : 'negative' },
        avgWin: { key: 'avgWin', label: 'Avg. Win', value: `$${avgWin.toFixed(2)}`, changeType: 'positive' },
        avgLoss: { key: 'avgLoss', label: 'Avg. Loss', value: `$${avgLoss.toFixed(2)}`, changeType: 'negative' },
        expectancy: { key: 'expectancy', label: 'Expectancy', value: `$${expectancy.toFixed(2)}`, changeType: expectancy > 0 ? 'positive' : 'negative' },
      };
    },

    calendarDataByMonth() {
      const { dailyDataForCalendar } = this.processedData;
      const filterStore = useFilterStore();
      const viewDate = new Date(filterStore.endDate);
      const year = viewDate.getFullYear();
      const month = viewDate.getMonth();

      const daysInMonth = new Date(year, month + 1, 0).getDate();
      const firstDayOfWeek = new Date(year, month, 1).getDay();
      const calendarDays = [];
      const offset = (firstDayOfWeek === 0) ? 6 : firstDayOfWeek - 1;
      for (let i = 0; i < offset; i++) {
        calendarDays.push({ isPlaceholder: true, key: `ph-start-${i}` });
      }

      for (let i = 1; i <= daysInMonth; i++) {
        const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(i).padStart(2, '0')}`;
        calendarDays.push({
          date: i,
          fullDate: dateStr,
          dailyData: dailyDataForCalendar[dateStr] || { totalPnl: 0, tradeCount: 0, winningTrades: 0 },
          isPlaceholder: false,
          key: dateStr,
        });
      }

      // Pad the end of the array to make it a multiple of 7
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
        // Questo getter ora restituisce semplicemente i dati pre-calcolati.
        return this.processedData.performanceByDayOfWeek;
    },

    winLossDays(state) {
      // Se i dati non sono pronti, restituisce uno stato di default.
      if (!this.processedData.winLossDaysStats) {
        return { winningDays: 0, losingDays: 0, breakEvenDays: 0 };
      }
      return this.processedData.winLossDaysStats;
    },

    /**
     * Restituisce un riepilogo completo per una singola giornata.
     * Questo getter restituisce una funzione che può essere chiamata con una data.
     * @param {Object} state - Lo stato di Pinia.
     * @returns {Function} Una funzione che accetta una data (es. '2025-08-28') e restituisce i dati di riepilogo.
     */
    getDailySummary(state) {
      return (date) => {
        if (!date) return null;

        // Filtra i trade per la data specificata.
        const dailyTrades = state.trades.filter(t => t.date === date);

        if (dailyTrades.length === 0) {
          return {
            date,
            trades: [],
            stats: {
              netPnl: 0,
              tradeCount: 0,
              winningTrades: 0,
              losingTrades: 0,
              breakEvenTrades: 0,
              grossProfit: 0,
              grossLoss: 0,
              winRate: 0,
              avgWin: 0,
              avgLoss: 0,
            },
            cumulativePnlForChart: { labels: [], data: [] }
          };
        }

        // Ordiniamo i trade per ID per avere un ordine (ipoteticamente cronologico)
        const sortedDailyTrades = [...dailyTrades].sort((a, b) => a.id - b.id);

        // Calcolo delle statistiche giornaliere
        const stats = {
          netPnl: 0,
          tradeCount: 0,
          winningTrades: 0,
          losingTrades: 0,
          breakEvenTrades: 0,
          grossProfit: 0,
          grossLoss: 0,
        };

        let cumulativePnl = 0;
        const cumulativeData = [];

        for (const trade of sortedDailyTrades) {
          stats.netPnl += trade.pnl;
          stats.tradeCount++;
          if (trade.pnl > 0) {
            stats.winningTrades++;
            stats.grossProfit += trade.pnl;
          } else if (trade.pnl < 0) {
            stats.losingTrades++;
            stats.grossLoss += Math.abs(trade.pnl);
          } else {
            stats.breakEvenTrades++;
          }

          cumulativePnl += trade.pnl;
          cumulativeData.push(cumulativePnl);
        }

        stats.winRate = stats.tradeCount > 0 ? (stats.winningTrades / stats.tradeCount) * 100 : 0;
        stats.avgWin = stats.winningTrades > 0 ? stats.grossProfit / stats.winningTrades : 0;
        stats.avgLoss = stats.losingTrades > 0 ? stats.grossLoss / stats.losingTrades : 0;

        // Dati per il grafico
        const chartLabels = sortedDailyTrades.map((trade, index) => `Trade ${index + 1}`);

        return {
          date,
          trades: sortedDailyTrades,
          stats,
          cumulativePnlForChart: {
            labels: chartLabels,
            data: cumulativeData,
          },
        };
      };
    },

    /**
     * Calcola i dati per il grafico della curva di equity.
     * Ordina i trade per data e calcola il P&L cumulativo.
     */
    equityCurveData(state) {
      if (this.filteredTrades.length === 0) {
        return { labels: [], data: [] };
      }

      // Ordiniamo i trade per data, dal più vecchio al più recente.
      const sortedTrades = [...this.filteredTrades].sort((a, b) => new Date(a.date) - new Date(b.date));

      let cumulativePnl = 0;
      const dataPoints = sortedTrades.map(trade => {
        cumulativePnl += trade.pnl;
        return {
          date: trade.date,
          pnl: cumulativePnl,
        };
      });

      // Formattiamo i dati per la libreria di grafici.
      return {
        labels: dataPoints.map(p => p.date),
        data: dataPoints.map(p => p.pnl),
      };
    },

    tradeHeaders: () => [
      { key: 'ticker', text: 'Ticker' },
      { key: 'type', text: 'Type' },
      { key: 'pnl', text: 'Net P&L' },
      { key: 'date', text: 'Date' },
    ],

    calendarControlsData() {
      const filterStore = useFilterStore();
      const viewDate = new Date(filterStore.endDate);

      if (isNaN(viewDate.getTime())) {
        return { monthLabel: 'Invalid Date', monthlyPnl: 0 };
      }

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
    addTrade(newTrade) {
      this.trades.unshift({ ...newTrade, id: Date.now(), date: new Date().toISOString().split('T')[0] });
    },
  },
});
