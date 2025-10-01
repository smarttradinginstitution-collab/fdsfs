<script setup>
import { computed } from 'vue';
import GaugeChart from './StatCard/GaugeChart.vue';
import WinLossDonutChart from './StatCard/WinLossDonutChart.vue';
import MiniPnlLineChart from './StatCard/MiniPnlLineChart.vue';
import AvgWinLossBarChart from './StatCard/AvgWinLossBarChart.vue';
import HeaderInfoOverlay from '../../ui/HeaderInfoOverlay.vue';
import { useMetricInfo } from '../../../composables/useMetricInfo.js';

// --- PROPS ---
const props = defineProps({
  stat: { type: Object, required: true },
});

const { info } = useMetricInfo(props.stat.key);

// --- COMPUTED PROPERTIES ---
const valueClasses = computed(() => ({
  'stat-value': true,
  'stat-value--positive': props.stat.changeType === 'positive',
  'stat-value--negative': props.stat.changeType === 'negative',
}));

const numericValue = computed(() => {
    const cleanedValue = String(props.stat.value).replace(/[^\d.-]/g, '');
    return parseFloat(cleanedValue) || 0;
});

const isNetPnl = computed(() => props.stat.key === 'netCumulativePnl');
const isProfitFactor = computed(() => props.stat.key === 'profitFactor');
const isWinRate = computed(() => props.stat.key === 'winPercentage');
const isAvgWinLoss = computed(() => props.stat.key === 'avgWinLoss');

// Special layout for AvgWinLoss, as it doesn't have a main value.
const cardLayoutClass = computed(() => ({
  'stat-card': true,
  'stat-card--avg-win-loss': isAvgWinLoss.value,
}));

</script>

<template>
  <div :class="cardLayoutClass">
    <div class="text-content">
      <HeaderInfoOverlay :aria-label="`Learn more about ${info.title}`" class="header-overlay">
        <template #title>
           <!-- Custom label for Win Rate with badges -->
          <div v-if="isWinRate" class="win-rate-label">
            <span class="stat-label">Win %</span>
            <div class="badges">
              <span class="badge win">{{ stat.wins }}</span>
              <span class="badge loss">{{ stat.losses }}</span>
            </div>
          </div>
          <!-- Default label for other stats -->
          <p v-else class="stat-label">{{ stat.label }}</p>
        </template>
        <template #content>
          <h4 class="info-overlay-title">{{ info.title }}</h4>
          <p class="info-overlay-text">{{ info.description }}</p>
        </template>
      </HeaderInfoOverlay>

      <!-- Main stat value, hidden for AvgWinLoss -->
      <p v-if="!isAvgWinLoss" :class="valueClasses">{{ stat.value }}</p>
    </div>

    <!-- Chart container -->
    <div class="chart-content">
      <WinLossDonutChart v-if="isWinRate" :wins="stat.wins" :losses="stat.losses" :breakevens="stat.breakevens" />
      <GaugeChart v-if="isProfitFactor" :value="numericValue" />
      <MiniPnlLineChart v-if="isNetPnl" :series="stat.series" />
      <AvgWinLossBarChart v-if="isAvgWinLoss" :avgWin="stat.avgWin" :avgLoss="stat.avgLoss" />
    </div>
  </div>
</template>

<style scoped>
.stat-card {
  background-color: var(--semantic-color-surface-primary);
  padding: var(--semantic-size-inset-md);
  border-radius: var(--semantic-border-radius-surface);
  border: var(--semantic-border-width-default) solid var(--semantic-color-border-default);
  box-shadow: var(--semantic-effect-shadow-elevation-low);
  display: grid;
  grid-template-columns: 1fr auto;
  align-items: center;
  gap: var(--semantic-size-stack-fluid-stat-card-gap);
  transition: box-shadow var(--semantic-animation-duration-interactive) var(--semantic-animation-easing-exit);
  overflow: hidden; /* Prevents chart from overflowing card boundaries */
}
.stat-card:hover {
    box-shadow: var(--semantic-effect-shadow-elevation-medium);
}

/* Special grid layout for AvgWinLoss card to make the chart take full width */
.stat-card--avg-win-loss {
    grid-template-columns: auto 1fr; /* Label on left, chart takes rest of space */
    align-items: stretch; /* Stretch items to fill card height */
}
.stat-card--avg-win-loss .text-content {
    align-items: flex-start;
    justify-content: flex-start;
    padding-top: 4px; /* Align label better with chart */
}
.stat-card--avg-win-loss .chart-content {
    width: 100%;
}


.text-content {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-xs);
}
.stat-label {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
  white-space: nowrap;
}

.header-overlay :deep(.title-container) {
  align-items: center;
  justify-content: flex-start;
  gap: var(--semantic-size-stack-xxs);
}
.header-overlay :deep(.info-button) {
    margin-bottom: 0;
}

.info-overlay-title {
  font: var(--semantic-font-style-label-md);
  color: var(--semantic-color-text-primary);
}

.info-overlay-text {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
  line-height: var(--base-font-line-height-tight);
}

.stat-value {
  font: var(--semantic-font-style-metric-display);
  color: var(--semantic-color-text-primary);
}
.stat-value--positive {
  color: var(--semantic-color-feedback-positive-text);
}
.stat-value--negative {
  color: var(--semantic-color-feedback-negative-text);
}

.win-rate-label {
    display: flex;
    align-items: center;
    gap: var(--semantic-size-stack-sm);
}
.badges {
    display: flex;
    gap: var(--semantic-size-stack-xxs);
}
.badge {
    font: var(--semantic-font-style-body-xxs);
    padding: var(--semantic-size-badge-padding-y) var(--semantic-size-badge-padding-x);
    border-radius: var(--semantic-border-radius-tag);
}
.badge.win {
    background-color: var(--semantic-color-feedback-positive-surface);
    color: var(--semantic-color-feedback-positive-text);
}
.badge.loss {
    background-color: var(--semantic-color-feedback-negative-surface);
    color: var(--semantic-color-feedback-negative-text);
}

.chart-content {
    flex-shrink: 0;
    width: var(--semantic-size-component-stat-card-chart-width);
    display: flex;
    align-items: center;
    justify-content: center;
}
</style>