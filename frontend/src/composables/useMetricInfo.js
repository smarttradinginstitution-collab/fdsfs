import { computed } from 'vue';

const metricInfo = {
  netPnl: {
    title: 'Net P&L',
    description: 'The Net Profit and Loss (P&L) represents the total profitability of all trades within the selected period, after accounting for any commissions or fees. It is the most direct measure of your trading performance.'
  },
  winRate: {
    title: 'Win Rate',
    description: 'The Win Rate is the percentage of trades that were profitable out of the total number of trades. It is calculated as (Number of Winning Trades / Total Number of Trades) * 100. A higher win rate indicates a greater frequency of successful trades.'
  },
  trades: {
    title: 'Total Trades',
    description: 'This is the total number of trades executed within the selected period. It includes all winning, losing, and break-even trades.'
  },
  profitFactor: {
    title: 'Profit Factor',
    description: 'The Profit Factor is the ratio of gross profit to gross loss. It is calculated as (Total Profit from Winning Trades / Total Loss from Losing Trades). A value greater than 1 indicates profitability. A high profit factor is a strong indicator of a profitable system.'
  },
  avgWin: {
    title: 'Average Win',
    description: 'This metric shows the average profit from all winning trades. It is calculated by dividing the total gross profit by the number of winning trades. It helps you understand the typical size of your successful trades.'
  },
  avgLoss: {
    title: 'Average Loss',
    description: 'This metric shows the average loss from all losing trades. It is calculated by dividing the total gross loss by the number of losing trades. It is crucial for risk management to keep this value in check.'
  },
  expectancy: {
    title: 'Expectancy',
    description: 'Expectancy is the average amount you can expect to win or lose per trade. It is calculated as (Win Rate * Average Win) - (Loss Rate * Average Loss). A positive expectancy suggests a profitable trading strategy over the long term.'
  },
  avgTradePnl: {
    title: 'Avg. Trade P&L',
    description: 'The Average Trade P&L is the average profit or loss per trade, including winning, losing, and break-even trades. It is calculated by dividing the Net P&L by the total number of trades.'
  },
  largestProfit: {
    title: 'Largest Profit',
    description: 'This is the largest single profit from a winning trade in the selected period. It can highlight the potential of your strategy but also the presence of outliers.'
  },
  largestLoss: {
    title: 'Largest Loss',
    description: 'This is the largest single loss from a losing trade in the selected period. This metric is critical for understanding and managing risk.'
  },
  maxConsecutiveWins: {
    title: 'Max Consecutive Wins',
    description: 'This metric shows the longest streak of consecutive winning trades. It can be an indicator of strategy consistency during favorable market conditions.'
  },
  maxConsecutiveLosses: {
    title: 'Max Consecutive Losses',
    description: 'This metric shows the longest streak of consecutive losing trades. Understanding this can help you prepare psychologically and financially for drawdowns.'
  },
  avgRealizedRr: {
    title: 'Avg. Realized R:R',
    description: 'The Average Realized Risk/Reward ratio compares the average profit on winning trades to the average loss on losing trades. It is calculated as (Average Win / Average Loss). A ratio greater than 1 means your average wins are larger than your average losses.'
  },
  maxDrawdownAbs: {
    title: 'Max Drawdown',
    description: 'Maximum Drawdown is the largest peak-to-trough decline in your account equity during the selected period. It is a key measure of risk, representing the worst-case loss from a single high point.'
  },
  sharpeRatio: {
    title: 'Sharpe Ratio',
    description: 'The Sharpe Ratio measures the risk-adjusted return of your strategy. It is calculated by dividing the average return by the standard deviation of returns (volatility). A higher Sharpe Ratio indicates a better performance for the amount of risk taken.'
  },
  averageHoldTime: {
    title: 'Avg. Hold Time',
    description: 'This is the average duration of all your trades, from entry to exit. It helps you understand if you are a short-term or long-term trader and can be used to optimize your strategy.'
  }
};

export function useMetricInfo(statKey) {
  const info = computed(() => metricInfo[statKey] || {
    title: 'Info not available',
    description: 'A description for this metric has not been defined yet.'
  });

  return {
    info
  };
}