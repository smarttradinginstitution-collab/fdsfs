<script setup>
import { computed } from 'vue';
import { useMetricInfo } from '@/composables/useMetricInfo';
import { formatCurrency } from '@/services/formatters';

// Component imports
import HeaderInfoOverlay from '@/components/ui/HeaderInfoOverlay.vue';

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
const formattedAvgLoss = computed(() => `-${formatCurrency(avgLoss.value)}`);

const total = computed(() => avgWin.value + avgLoss.value);

const winPercentage = computed(() => {
  if (total.value === 0) return 50;
  return (avgWin.value / total.value) * 100;
});

</script>

<template>
  <div class="stat-card-container">
    <div class="header">
        <span class="title">Avg win/loss trade</span>
        <HeaderInfoOverlay :aria-label="`Learn more about ${info.title}`">
            <template #content>
                <h4 class="info-overlay-title">{{ info.title }}</h4>
                <p class="info-overlay-text">{{ info.description }}</p>
            </template>
        </HeaderInfoOverlay>
    </div>

    <div class="content">
      <p class="value">{{ avgRR }}</p>
      <div class="bar-area">
        <div class="bar-container">
          <div class="win-bar" :style="{ width: winPercentage + '%' }"></div>
        </div>
        <div class="labels-container">
          <span class="label-win">{{ formattedAvgWin }}</span>
          <span class="label-loss">{{ formattedAvgLoss }}</span>
        </div>
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
  display: flex;
  flex-direction: column;
  height: 100%;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  margin-bottom: var(--semantic-size-stack-sm);
}

.title {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
}

.content {
  display: flex;
  flex-direction: column;
  justify-content: center; /* Center content vertically */
  flex-grow: 1;
  gap: var(--semantic-size-stack-xs);
}

.value {
  font: var(--semantic-font-style-metric-display);
  color: var(--semantic-color-text-primary);
  line-height: 1;
}

.bar-area {
    display: flex;
    flex-direction: column;
    gap: var(--semantic-size-stack-xxs);
}

.bar-container {
  width: 100%;
  height: 8px;
  background-color: var(--semantic-color-chart-loss);
  border-radius: var(--semantic-border-radius-pill);
  overflow: hidden;
}

.win-bar {
  height: 100%;
  background-color: var(--semantic-color-chart-profit);
  border-radius: var(--semantic-border-radius-pill);
  transition: width 0.4s ease-out;
}

.labels-container {
  display: flex;
  justify-content: space-between;
}

.label-win, .label-loss {
  font: var(--semantic-font-style-body-xs);
}
.label-win {
  color: var(--semantic-color-feedback-positive-text);
}
.label-loss {
  color: var(--semantic-color-feedback-negative-text);
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