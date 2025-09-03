// =============================================================================
// FILE: stores/trades.js
// DESCRIZIONE: Store dei trade, refattorizzato per massima efficienza.
// =============================================================================

import { defineStore } from 'pinia';
import { useFilterStore } from './filterStore';

export const useTradesStore = defineStore('trades', {
  state: () => ({
    trades: [
      // Dati di esempio con i nuovi campi
      { id: 1, ticker: 'AAPL', type: 'Long', pnl: 150.75, date: '2025-08-28', strategy: 'Breakout', risk: 50, openTime: '09:30:15', instrument: 'Stocks', commission: 4.50, netROI: 1.5, rMultiple: 3.01, ticks: 60, bestExit: 151.00 },
      { id: 2, ticker: 'TSLA', type: 'Short', pnl: -75.20, date: '2025-08-28', strategy: 'Reversal', risk: 50, openTime: '10:05:40', instrument: 'Stocks', commission: 4.50, netROI: -0.75, rMultiple: -1.50, ticks: -30, bestExit: 249.50 },
      { id: 3, ticker: 'NVDA', type: 'Long', pnl: 278.40, date: '2025-08-27', strategy: 'Breakout', risk: 100, openTime: '11:15:00', instrument: 'Stocks', commission: 6.20, netROI: 1.39, rMultiple: 2.78, ticks: 110, bestExit: 450.00 },
      { id: 4, ticker: 'GOOG', type: 'Long', pnl: 121.00, date: '2025-08-20', strategy: 'Momentum', risk: 60, openTime: '14:00:05', instrument: 'Stocks', commission: 3.80, netROI: 1.0, rMultiple: 2.01, ticks: 48, bestExit: 135.00 },
      { id: 5, ticker: 'MSFT', type: 'Long', pnl: 88.50, date: '2025-08-28', strategy: 'Reversal', risk: 40, openTime: '14:30:00', instrument: 'Stocks', commission: 4.50, netROI: 1.1, rMultiple: 2.21, ticks: 35, bestExit: 330.00 },
      { id: 6, ticker: 'AMD', type: 'Short', pnl: -42.10, date: '2025-08-10', strategy: 'Breakout', risk: 40, openTime: '09:45:10', instrument: 'Stocks', commission: 2.10, netROI: -0.52, rMultiple: -1.05, ticks: -21, bestExit: 109.00 },
      { id: 7, ticker: 'META', type: 'Long', pnl: 210.00, date: '2025-07-30', strategy: 'Momentum', risk: 70, openTime: '10:10:10', instrument: 'Stocks', commission: 5.00, netROI: 1.5, rMultiple: 3.00, ticks: 84, bestExit: 315.00 },
    ],
  }),

  getters: {
    allStrategies(state) {
      const strategies = new Set(state.trades.map(trade => trade.strategy).filter(Boolean));
      return ['All', ...Array.from(strategies)];
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

      const stats = { totalPnl: 0, tradeCount: 0, winningTrades: 0, losingTrades: 0, breakEvenTrades: 0, grossProfit: 0, grossLoss: 0, totalRisk: 0, };
      const dailyDataForCalendar = {};
      const performanceByStrategy = {};
      const pnlByDay = {};

      for (const trade of trades) {
        stats.totalPnl += trade.pnl;
        stats.tradeCount++;
        if (trade.pnl > 0) { stats.winningTrades++; stats.grossProfit += trade.pnl; }
        else if (trade.pnl < 0) { stats.losingTrades++; stats.grossLoss += Math.abs(trade.pnl); }
        else { stats.breakEvenTrades++; }

        const dayKey = trade.date;
        if (!pnlByDay[dayKey]) pnlByDay[dayKey] = 0;
        pnlByDay[dayKey] += trade.pnl;

        const tradeDate = new Date(trade.date);
        if (tradeDate.getFullYear() === viewDateForCalendar.getFullYear() && tradeDate.getMonth() === viewDateForCalendar.getMonth()) {
          if (!dailyDataForCalendar[dayKey]) dailyDataForCalendar[dayKey] = { totalPnl: 0, tradeCount: 0, winningTrades: 0 };
          dailyDataForCalendar[dayKey].totalPnl += trade.pnl;
          dailyDataForCalendar[dayKey].tradeCount++;
          if (trade.pnl > 0) dailyDataForCalendar[dayKey].winningTrades++;
        }
      }

      const winLossDaysStats = { winningDays: 0, losingDays: 0, breakEvenDays: 0 };
      for (const dayPnl of Object.values(pnlByDay)) {
        if (dayPnl > 0) winLossDaysStats.winningDays++;
        else if (dayPnl < 0) winLossDaysStats.losingDays++;
        else winLossDaysStats.breakEvenDays++;
      }

      return { stats, dailyDataForCalendar, winLossDaysStats };
    },

    getDailySummary(state) {
      return (date) => {
        if (!date) return null;

        const dailyTrades = state.trades.filter(t => t.date === date);
        const sortedDailyTrades = [...dailyTrades].sort((a, b) => a.id - b.id);

        const summary = {
          date,
          trades: sortedDailyTrades,
          stats: {
            netPnl: 0,
            tradeCount: 0,
            winningTrades: 0,
            losingTrades: 0,
            totalCommission: 0,
            profitFactor: 0,
          },
          cumulativePnlForChart: { labels: ['Start'], data: [0] }
        };

        if (dailyTrades.length === 0) return summary;

        let grossProfit = 0;
        let grossLoss = 0;
        let cumulativePnl = 0;

        for (const trade of sortedDailyTrades) {
          summary.stats.netPnl += trade.pnl;
          summary.stats.tradeCount++;
          summary.stats.totalCommission += trade.commission;

          if (trade.pnl > 0) {
            summary.stats.winningTrades++;
            grossProfit += trade.pnl;
          } else if (trade.pnl < 0) {
            summary.stats.losingTrades++;
            grossLoss += Math.abs(trade.pnl);
          }

          cumulativePnl += trade.pnl;
          summary.cumulativePnlForChart.data.push(cumulativePnl);
          summary.cumulativePnlForChart.labels.push(trade.ticker);
        }

        summary.stats.profitFactor = grossLoss > 0 ? grossProfit / grossLoss : (grossProfit > 0 ? Infinity : 0);

        return summary;
      };
    },

    // Other getters can be simplified if they are not used, for now we keep them
    // ...
  },

  actions: {
    addTrade(newTrade) {
      const fullTrade = {
        ...newTrade,
        id: Date.now(),
        date: new Date().toISOString().split('T')[0],
        openTime: new Date().toLocaleTimeString(),
        instrument: 'Stocks',
        commission: 5.00,
        netROI: Math.random() * 2,
        rMultiple: Math.random() * 3,
        ticks: Math.floor(Math.random() * 100),
        bestExit: newTrade.pnl * 1.1
      };
      this.trades.unshift(fullTrade);
    },
  },
});
