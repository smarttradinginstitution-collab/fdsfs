<script setup>
import { computed } from 'vue';
import { useMetricInfo } from '@/composables/useMetricInfo';
import { formatCurrency } from '@/services/formatters';

// Component imports
import BaseWidget from '@/components/layout/BaseWidget.vue';
import HeaderInfoButton from '@/components/ui/HeaderInfoButton.vue';
import PnlLineChart from './PnlLineChart.vue'; // This will be created next

// --- PROPS ---
const props = defineProps({
  stats: { type: Object, required: true },
  pnlData: { type: Object, required: true },
});

// --- COMPOSABLES ---
// Using a static key 'netPnl' to fetch the correct description
const { info } = useMetricInfo('netPnl');

// --- COMPUTED ---
const formattedPnl = computed(() => formatCurrency(props.stats.net_pnl));
const pnlIsPositive = computed(() => props.stats.net_pnl >= 0);

const chartData = computed(() => ({
  labels: props.pnlData.labels,
  datasets: [
    {
      data: props.pnlData.data,
      borderColor: pnlIsPositive.value ? 'var(--semantic-color-chart-profit)' : 'var(--semantic-color-chart-loss)',
      backgroundColor: pnlIsPositive.value ? 'var(--semantic-color-chart-profit-transparent)' : 'var(--semantic-color-chart-loss-transparent)',
      fill: true,
      tension: 0.4,
      pointRadius: 0, // Hide points
      borderWidth: 2,
    },
  ],
}));

</script>

<template>
  <BaseWidget class="net-pnl-card">
    <template #header>
      <div class="header-content">
        <div class="title-group">
          <span>Net Cumulative P&L</span>
          <span class="trade-count-badge">{{ stats.trade_count }}</span>
        </div>
        <HeaderInfoButton :title="info.title" :text="info.description" />
      </div>
    </template>

    <div class="widget-main-content">
      <p class="pnl-value" :class="{ 'positive': pnlIsPositive, 'negative': !pnlIsPositive }">
        {{ formattedPnl }}
      </p>
      <div class="chart-container">
        <PnlLineChart v-if="pnlData.labels.length > 1" :chart-data="chartData" />
      </div>
    </div>
  </BaseWidget>
</template>

<style scoped>
.net-pnl-card :deep(.widget-content) {
  padding: 0;
  display: flex;
  flex-direction: column;
  justify-content: flex-end; /* Align content to the bottom */
}
.net-pnl-card :deep(.widget-header) {
    min-height: auto;
    padding: var(--semantic-size-inset-md);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
}

.title-group {
  display: flex;
  align-items: center;
  gap: var(--semantic-size-stack-sm);
}

.trade-count-badge {
  font: var(--semantic-font-style-body-xxs);
  background-color: var(--semantic-color-surface-sunken);
  color: var(--semantic-color-text-secondary);
  padding: var(--semantic-size-badge-padding-y) var(--semantic-size-badge-padding-x);
  border-radius: var(--semantic-border-radius-tag);
}

.widget-main-content {
  padding: var(--semantic-size-inset-md);
  padding-top: 0;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.pnl-value {
  font: var(--semantic-font-style-metric-display);
  color: var(--semantic-color-text-primary);
  margin-bottom: var(--semantic-size-stack-sm);
}
.pnl-value.positive {
  color: var(--semantic-color-feedback-positive-text);
}
.pnl-value.negative {
  color: var(--semantic-color-feedback-negative-text);
}

.chart-container {
  flex-grow: 1;
  min-height: 80px; /* Ensure chart has some space */
  position: relative;
}
</style>