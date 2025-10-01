<script setup>
import { computed } from 'vue';
import { useMetricInfo } from '@/composables/useMetricInfo';
import { formatCurrency } from '@/services/formatters';

// Component imports
import BaseWidget from '@/components/layout/BaseWidget.vue';
import HeaderInfoButton from '@/components/ui/HeaderInfoButton.vue';

// --- PROPS ---
const props = defineProps({
  stats: { type: Object, required: true },
});

// --- COMPOSABLES ---
const { info } = useMetricInfo('avgRealizedRr');

// --- COMPUTED ---
const avgRR = computed(() => props.stats.avg_realized_rr?.toFixed(2) ?? '0.00');
const avgWin = computed(() => props.stats.avg_win ?? 0);
const avgLoss = computed(() => props.stats.avg_loss ?? 0);

const formattedAvgWin = computed(() => formatCurrency(avgWin.value));
const formattedAvgLoss = computed(() => formatCurrency(avgLoss.value));

const total = computed(() => avgWin.value + avgLoss.value);

const winPercentage = computed(() => {
  if (total.value === 0) return 50; // Default to 50/50 if no data
  return (avgWin.value / total.value) * 100;
});

const lossPercentage = computed(() => {
  if (total.value === 0) return 50;
  return (avgLoss.value / total.value) * 100;
});

</script>

<template>
  <BaseWidget class="kpi-card">
    <template #header>
      <div class="header-content">
        <span>Avg win/loss trade</span>
        <HeaderInfoButton :title="info.title" :text="info.description" />
      </div>
    </template>

    <div class="widget-main-content">
      <p class="stat-value">{{ avgRR }}</p>
      <div class="bar-and-labels">
        <div class="bar-container">
          <div class="bar-segment win-bar" :style="{ width: winPercentage + '%' }"></div>
          <div class="bar-segment loss-bar" :style="{ width: lossPercentage + '%' }"></div>
        </div>
        <div class="labels-container">
          <span class="label win-label">{{ formattedAvgWin }}</span>
          <span class="label loss-label">{{ formattedAvgLoss }}</span>
        </div>
      </div>
    </div>
  </BaseWidget>
</template>

<style scoped>
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
  flex-direction: column;
  gap: var(--semantic-size-stack-md);
}

.stat-value {
  font: var(--semantic-font-style-metric-display);
  color: var(--semantic-color-text-primary);
}

.bar-and-labels {
    display: flex;
    flex-direction: column;
    gap: var(--semantic-size-stack-xs);
}

.bar-container {
  display: flex;
  width: 100%;
  height: 8px;
  border-radius: var(--semantic-border-radius-pill);
  overflow: hidden;
}

.bar-segment {
  height: 100%;
  transition: width 0.3s ease-in-out;
}

.win-bar {
  background-color: var(--semantic-color-chart-profit);
}

.loss-bar {
  background-color: var(--semantic-color-chart-loss);
}

.labels-container {
  display: flex;
  justify-content: space-between;
}

.label {
  font: var(--semantic-font-style-body-sm);
}
.win-label {
    color: var(--semantic-color-feedback-positive-text);
}
.loss-label {
    color: var(--semantic-color-feedback-negative-text);
}
</style>