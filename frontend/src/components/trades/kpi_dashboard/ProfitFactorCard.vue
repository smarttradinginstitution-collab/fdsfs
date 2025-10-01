<script setup>
import { computed } from 'vue';
import { useMetricInfo } from '@/composables/useMetricInfo';

// Component imports
import BaseWidget from '@/components/layout/BaseWidget.vue';
import HeaderInfoButton from '@/components/ui/HeaderInfoButton.vue';
import GaugeChart from './GaugeChart.vue'; // This will be created next

// --- PROPS ---
const props = defineProps({
  stats: { type: Object, required: true },
});

// --- COMPOSABLES ---
const { info } = useMetricInfo('profitFactor');

// --- COMPUTED ---
const profitFactor = computed(() => props.stats.profit_factor ?? 0);
const profitFactorLabel = computed(() => {
    if (props.stats.profit_factor === null) return '∞';
    if (props.stats.profit_factor === 0 && props.stats.gross_loss === 0) return 'N/A';
    return profitFactor.value.toFixed(2);
});

</script>

<template>
  <BaseWidget class="kpi-card">
    <template #header>
      <div class="header-content">
        <span>Profit Factor</span>
        <HeaderInfoButton :title="info.title" :text="info.description" />
      </div>
    </template>

    <div class="widget-main-content">
      <p class="stat-value">{{ profitFactorLabel }}</p>
      <div class="chart-container">
        <GaugeChart :value="profitFactor" :max-value="5" />
      </div>
    </div>
  </BaseWidget>
</template>

<style scoped>
/* Reusable styles for the simple KPI cards */
.kpi-card :deep(.widget-content) {
  padding: 0;
  padding-top: var(--semantic-size-inset-lg);
}
.kpi-card :deep(.widget-header) {
    min-height: auto;
    padding: var(--semantic-size-inset-md);
    border-bottom: none; /* No border for these cards */
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
}

.widget-main-content {
  padding: var(--semantic-size-inset-md);
  padding-top: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--semantic-size-gutter-md);
}

.stat-value {
  font: var(--semantic-font-style-metric-display);
  color: var(--semantic-color-text-primary);
}

.chart-container {
  width: 80px; /* Fixed width for gauge charts */
  height: 40px; /* Half height for semi-circle */
}
</style>