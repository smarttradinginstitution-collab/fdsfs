export const predefinedLayouts = [
  {
    id: 'performance_analyst',
    name: 'Analista di Performance',
    widgets: [
      { i: 'cumulativePnl', x: 0, y: 0, w: 8, h: 4 },
      { i: 'vantageScore', x: 8, y: 0, w: 4, h: 4 },
      { i: 'rrDistribution', x: 0, y: 4, w: 4, h: 4 },
      { i: 'calendar', x: 4, y: 4, w: 8, h: 4 },
      { i: 'recentTrades', x: 0, y: 8, w: 12, h: 5 },
    ],
  },
  {
    id: 'aggressive_trader',
    name: 'Trader Aggressivo',
    widgets: [
      { i: 'recentTrades', x: 0, y: 0, w: 12, h: 5 },
      { i: 'cumulativePnl', x: 0, y: 5, w: 6, h: 4 },
      { i: 'vantageScore', x: 6, y: 5, w: 6, h: 4 },
      { i: 'rrDistribution', x: 0, y: 9, w: 6, h: 4 },
      { i: 'calendar', x: 6, y: 9, w: 6, h: 4 },
    ],
  },
];
