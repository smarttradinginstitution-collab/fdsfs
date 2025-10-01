<script setup>
import { computed } from 'vue';
import { useMetricInfo } from '@/composables/useMetricInfo';
import { formatPercentage } from '@/services/formatters';

// Component imports
import BaseWidget from '@/components/layout/BaseWidget.vue';
import HeaderInfoButton from '@/components/ui/HeaderInfoButton.vue';
import WinRateGauge from './WinRateGauge.vue'; // This will be created next

// --- PROPS ---
const props = defineProps({
  stats: { type: Object, required: true },
});

// --- COMPOSABLES ---
const { info } = useMetricInfo('winRate');

// --- COMPUTED ---
const winRate = computed(() => props.stats.win_rate ?? 0);
const formattedWinRate = computed(() => formatPercentage(winRate.value));

</script>

<template>
  <BaseWidget class="kpi-card">
    <template #header>
      <div class="header-content">
        <span>Win %</span>
        <HeaderInfoButton :title="info.title" :text="info.description" />
      </div>
    </template>

    <div class="widget-main-content">
      <p class="stat-value">{{ formattedWinRate }}</p>
      <div class="chart-container">
        <WinRateGauge :win-rate="winRate" />
      </div>
    </div>
  </BaseWidget>
</template>

<style scoped>
/* Reusing styles from ProfitFactorCard.vue for consistency */
.kpi-card :deep(.widget-content) {
  padding: 0;
  padding-top: var(--semantic-size-inset-lg);
}
.kpi-card :deep(.widget-header) {
    min-height: auto;
    padding: var(--semantic-size-inset-md);
    border-bottom: none;
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
  width: 80px;
  height: 40px;
}
</style>