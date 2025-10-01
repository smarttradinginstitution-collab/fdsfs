<script setup>
import { computed } from 'vue';
import { useMetricInfo } from '@/composables/useMetricInfo';
import { formatCurrency } from '@/services/formatters';

// Component imports
import BaseWidget from '@/components/layout/BaseWidget.vue';
import HeaderInfoOverlay from '@/components/ui/HeaderInfoOverlay.vue';
import PnlLineChart from './PnlLineChart.vue';

// --- PROPS ---
const props = defineProps({
  stats: { type: Object, required: true },
  pnlData: { type: Object, required: true },
});

// --- COMPOSABLES ---
const { info } = useMetricInfo('netPnl');

// --- COMPUTED ---
const formattedPnl = computed(() => formatCurrency(props.stats.net_pnl));
const pnlIsPositive = computed(() => props.stats.net_pnl >= 0);

const chartData = computed(() => ({
  labels: props.pnlData.labels,
  datasets: [
    {
      data: props.pnlData.data,
      borderColor: 'rgba(34, 197, 94, 1)',
      backgroundColor: 'rgba(34, 197, 94, 0.1)',
      fill: true,
      tension: 0.4,
      pointRadius: 0,
      borderWidth: 1.5,
    },
  ],
}));

</script>

<template>
  <div class="stat-card-container">
    <div class="header">
        <div class="title-group">
            <span class="title">Net Cumulative P&L</span>
            <span class="badge">{{ stats.trade_count }}</span>
        </div>
         <HeaderInfoOverlay :aria-label="`Learn more about ${info.title}`">
            <template #content>
                <h4 class="info-overlay-title">{{ info.title }}</h4>
                <p class="info-overlay-text">{{ info.description }}</p>
            </template>
        </HeaderInfoOverlay>
    </div>

    <div class="content">
        <p class="value">{{ formattedPnl }}</p>
        <div class="chart-wrapper">
            <PnlLineChart v-if="pnlData && pnlData.labels.length > 1" :chart-data="chartData" />
        </div>
    </div>
  </div>
</template>

<style scoped>
.stat-card-container {
  background-color: var(--semantic-color-surface-primary);
  border: 1px solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-surface);
  padding: var(--semantic-size-inset-md);
  display: grid;
  grid-template-rows: auto 1fr; /* Header auto, content 1fr */
  height: 100%;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  margin-bottom: var(--semantic-size-stack-sm);
}

.title-group {
  display: flex;
  align-items: center;
  gap: var(--semantic-size-stack-xs);
}

.title {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
}

.badge {
  font: var(--semantic-font-style-body-xxs);
  background-color: var(--semantic-color-surface-sunken);
  color: var(--semantic-color-text-secondary);
  padding: var(--semantic-size-badge-padding-y) var(--semantic-size-badge-padding-x);
  border-radius: var(--semantic-border-radius-tag);
}

.content {
    display: grid;
    grid-template-columns: auto 1fr; /* Value auto, chart 1fr */
    align-items: flex-end; /* Align items to the bottom */
    gap: var(--semantic-size-gutter-md);
    height: 100%;
}

.value {
  font: var(--semantic-font-style-metric-display);
  color: var(--semantic-color-text-primary);
  line-height: 1; /* Adjust line height to prevent extra space */
}

.chart-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 60px; /* Give chart a minimum height */
}

/* Info Overlay Styling */
.info-overlay-title {
  font: var(--semantic-font-style-label-md);
  color: var(--semantic-color-text-primary);
}

.info-overlay-text {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
  line-height: var(--base-font-line-height-tight);
}
</style>