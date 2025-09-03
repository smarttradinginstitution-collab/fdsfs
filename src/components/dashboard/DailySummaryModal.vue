<script setup>
import { computed } from 'vue';
import { useUiStore } from '@/stores/uiStore';
import { useTradesStore } from '@/stores/trades';
import BaseModal from '@/components/ui/BaseModal.vue';
import BaseButton from '@/components/ui/BaseButton.vue';
import IconButton from '@/components/ui/IconButton.vue';
import SparkleIcon from '@/components/icons/SparkleIcon.vue';
import DailyPnlChart from './DailyPnlChart.vue';
import BasePill from '@/components/ui/BasePill.vue';

const uiStore = useUiStore();
const tradesStore = useTradesStore();

const dailyData = computed(() => {
  if (!uiStore.selectedDate) return null;
  return tradesStore.getDailySummary(uiStore.selectedDate);
});

const handleClose = () => {
  uiStore.closeDailySummaryModal();
};

const pnlClass = (pnl) => {
  if (pnl === 0 || pnl === null || pnl === undefined) return 'pnl--neutral';
  return pnl > 0 ? 'pnl--positive' : 'pnl--negative';
};

const formattedDate = computed(() => {
  if (!dailyData.value) return '';
  const date = new Date(dailyData.value.date + 'T00:00:00');
  return date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' });
});

const formattedPnl = (pnl) => {
    if (pnl === null || pnl === undefined) return '$0.00';
    const sign = pnl >= 0 ? '+' : '-';
    return `${sign}$${Math.abs(pnl).toFixed(2)}`;
};

const statsGrid = computed(() => {
    if (!dailyData.value) return null;
    const stats = dailyData.value.stats;
    return {
        col1: [
            { label: 'Total Trades', value: stats.tradeCount },
            { label: 'Winrate', value: `${(stats.winningTrades / (stats.tradeCount || 1) * 100).toFixed(1)}%` },
        ],
        col2: [
            { label: 'Winners', value: stats.winningTrades },
            { label: 'Losers', value: stats.losingTrades },
        ],
        col3: [
            { label: 'Commissions', value: `$${stats.totalCommission.toFixed(2)}` },
        ],
        col4: [
            { label: 'Profit Factor', value: stats.profitFactor.toFixed(2) },
        ]
    };
});

const tradeTableHeaders = computed(() => [
    { key: 'openTime', text: 'Open Time' },
    { key: 'ticker', text: 'Ticker' },
    { key: 'type', text: 'Side' },
    { key: 'instrument', text: 'Instrument' },
    { key: 'pnl', text: 'Net P&L' },
    { key: 'netROI', text: 'Net ROI' },
    { key: 'rMultiple', text: 'Realized R' },
    { key: 'playbook', text: 'Playbook' },
    { key: 'ticks', text: 'Ticks' },
    { key: 'bestExit', text: 'Best Exit' },
    { key: 'commission', text: 'Commission' },
]);
</script>

<template>
  <BaseModal
    :show="uiStore.isDailySummaryModalOpen"
    @close="handleClose"
    :show-close-button="false"
    class="daily-summary-modal"
  >
    <template #header>
      <div class="header-content">
        <div class="header-left">
          <span class="date">{{ formattedDate }}</span>
          <span class="pnl" :class="pnlClass(dailyData?.stats.netPnl)">Net P&L {{ formattedPnl(dailyData?.stats.netPnl) }}</span>
        </div>
        <div class="header-right">
          <BaseButton variant="secondary">Add Note</BaseButton>
          <IconButton aria-label="AI Assistant">
            <SparkleIcon />
          </IconButton>
        </div>
      </div>
    </template>

    <template #default>
      <div v-if="dailyData" class="modal-body-content">
        <div class="top-section">
          <div class="chart-section">
            <DailyPnlChart :chart-data="dailyData.cumulativePnlForChart" />
          </div>
          <div class="stats-section">
            <div class="stat-col">
                <div v-for="stat in statsGrid.col1" :key="stat.label" class="stat-cell stacked">
                    <span class="stat-label">{{ stat.label }}</span>
                    <span class="stat-value">{{ stat.value }}</span>
                </div>
            </div>
            <div class="stat-col">
                <div v-for="stat in statsGrid.col2" :key="stat.label" class="stat-cell stacked">
                    <span class="stat-label">{{ stat.label }}</span>
                    <span class="stat-value">{{ stat.value }}</span>
                </div>
            </div>
            <div class="stat-col">
                <div v-for="stat in statsGrid.col3" :key="stat.label" class="stat-cell">
                    <span class="stat-label">{{ stat.label }}</span>
                    <span class="stat-value">{{ stat.value }}</span>
                </div>
            </div>
            <div class="stat-col">
                <div v-for="stat in statsGrid.col4" :key="stat.label" class="stat-cell">
                    <span class="stat-label">{{ stat.label }}</span>
                    <span class="stat-value">{{ stat.value }}</span>
                </div>
            </div>
          </div>
        </div>

        <div class="table-wrapper">
          <table>
            <thead>
              <tr>
                <th v-for="header in tradeTableHeaders" :key="header.key">{{ header.text }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="dailyData.trades.length > 0" v-for="trade in dailyData.trades" :key="trade.id">
                <td>{{ trade.openTime }}</td>
                <td>{{ trade.ticker }}</td>
                <td>{{ trade.type }}</td>
                <td>{{ trade.instrument }}</td>
                <td :class="pnlClass(trade.pnl)">{{ formattedPnl(trade.pnl) }}</td>
                <td>{{ trade.netROI.toFixed(2) }}%</td>
                <td>{{ trade.rMultiple.toFixed(2) }}</td>
                <td><BasePill>{{ trade.strategy }}</BasePill></td>
                <td>{{ trade.ticks }}</td>
                <td>{{ trade.bestExit.toFixed(2) }}</td>
                <td>${{ trade.commission.toFixed(2) }}</td>
              </tr>
              <tr v-else>
                <td :colspan="tradeTableHeaders.length" class="no-trades-cell">No trades for this day.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
       <div v-else class="loading-state">
        Loading data...
      </div>
    </template>

    <template #footer>
      <div class="footer-content">
        <BaseButton variant="secondary" @click="handleClose">Cancel</BaseButton>
        <BaseButton variant="primary">View Details</BaseButton>
      </div>
    </template>
  </BaseModal>
</template>

<style scoped>
/* Header Styles */
.header-content { display: flex; justify-content: space-between; align-items: center; width: 100%; }
.header-left { display: flex; flex-direction: column; gap: var(--base-size-spacing-1); }
.date { font: var(--semantic-font-style-body-sm); color: var(--semantic-color-text-secondary); }
.pnl { font: var(--semantic-font-style-heading-sm); font-weight: 600; }
.pnl--positive { color: var(--semantic-color-text-positive); }
.pnl--negative { color: var(--semantic-color-text-negative); }
.pnl--neutral { color: var(--semantic-color-text-primary); }
.header-right { display: flex; align-items: center; gap: var(--base-size-spacing-2); }

/* Body Styles */
.modal-body-content {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-lg);
  flex-grow: 1;
  min-height: 0;
}
.top-section {
  display: grid;
  grid-template-columns: 1fr 1.5fr;
  gap: var(--semantic-size-gap-xl);
  align-items: stretch;
  flex-shrink: 0;
}
.chart-section { min-height: 150px; }

/* New Stats Section Styles */
.stats-section {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    border-left: var(--base-border-width-1) solid var(--semantic-color-border-default);
}
.stat-col {
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: var(--semantic-size-stack-lg);
    border-right: var(--base-border-width-1) solid var(--semantic-color-border-default);
    padding: 0 var(--semantic-size-inset-lg);
}
.stat-cell { display: flex; flex-direction: column; justify-content: center; gap: var(--base-size-spacing-1); }
.stat-label { font: var(--semantic-font-style-body-sm); color: var(--semantic-color-text-secondary); }
.stat-value { font: var(--semantic-font-style-heading-xs); color: var(--semantic-color-text-primary); font-weight: 600; }
.loading-state { text-align: center; padding: var(--semantic-size-inset-xl); color: var(--semantic-color-text-secondary); }

/* Table Styles */
.table-wrapper {
  flex-grow: 1;
  min-height: 0;
  overflow-y: auto;
  overflow-x: auto;
}
table { width: 100%; border-collapse: collapse; }
th, td { padding: var(--semantic-size-inset-md) var(--semantic-size-inset-sm); text-align: left; white-space: nowrap; border-bottom: var(--base-border-width-1) solid var(--semantic-color-border-default); }
th { font: var(--semantic-font-style-label-md); font-weight: 500; color: var(--semantic-color-text-secondary); text-transform: uppercase; position: sticky; top: 0; background-color: var(--semantic-color-surface-primary); }
tbody tr:hover { background-color: var(--semantic-color-surface-secondary); }
.no-trades-cell { text-align: center; color: var(--semantic-color-text-secondary); font-style: italic; padding: var(--semantic-size-inset-xl) 0; }

/* Footer Styles */
.footer-content { width: 100%; display: flex; justify-content: flex-end; gap: var(--semantic-size-gap-sm); padding-top: var(--semantic-size-inset-lg); border-top: var(--base-border-width-1) solid var(--semantic-color-border-default); }
</style>

<style>
.daily-summary-modal .modal-card {
  max-width: 800px;
  width: 95%;
  max-height: 90vh;
  gap: var(--semantic-size-stack-lg);
}
</style>
