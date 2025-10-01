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

// Keys to determine layout variations
const isNetPnl = computed(() => props.stat.key === 'netCumulativePnl');
const isProfitFactor = computed(() => props.stat.key === 'profitFactor');
const isWinRate = computed(() => props.stat.key === 'winPercentage');
const isAvgWinLoss = computed(() => props.stat.key === 'avgWinLoss');

// Dynamic classes for applying different layouts
const cardLayoutClass = computed(() => ({
  'stat-card': true,
  'layout--pnl': isNetPnl.value,
  'layout--centered': isProfitFactor.value || isWinRate.value || isAvgWinLoss.value,
}));
</script>

<template>
  <div :class="cardLayoutClass">
    <!-- Default Layout: Centered side-by-side -->
    <template v-if="isProfitFactor || isWinRate || isAvgWinLoss">
      <div class="text-content">
        <HeaderInfoOverlay :aria-label="`Learn more about ${info.title}`">
            <template #title>
                <div v-if="isWinRate" class="win-rate-label">
                    <span class="stat-label">Win %</span>
                    <div class="badges">
                        <span class="badge win">{{ stat.wins }}</span>
                        <span class="badge loss">{{ stat.losses }}</span>
                    </div>
                </div>
                <p v-else class="stat-label">{{ stat.label }}</p>
            </template>
            <template #content>
                <h4 class="info-overlay-title">{{ info.title }}</h4>
                <p class="info-overlay-text">{{ info.description }}</p>
            </template>
        </HeaderInfoOverlay>
        <p :class="valueClasses">{{ stat.value }}</p>
      </div>
      <div class="chart-content">
        <WinLossDonutChart v-if="isWinRate" :wins="stat.wins" :losses="stat.losses" :breakevens="stat.breakevens" />
        <GaugeChart v-if="isProfitFactor" :value="numericValue" />
        <AvgWinLossBarChart v-if="isAvgWinLoss" :avgWin="stat.avgWin" :avgLoss="stat.avgLoss" />
      </div>
    </template>

    <!-- P&L Layout: Text on top, full-width chart below -->
    <template v-if="isNetPnl">
        <div class="text-content-full">
            <HeaderInfoOverlay :aria-label="`Learn more about ${info.title}`">
                <template #title><p class="stat-label">{{ stat.label }}</p></template>
                 <template #content>
                    <h4 class="info-overlay-title">{{ info.title }}</h4>
                    <p class="info-overlay-text">{{ info.description }}</p>
                </template>
            </HeaderInfoOverlay>
            <p :class="valueClasses">{{ stat.value }}</p>
        </div>
        <div class="chart-content-full">
            <MiniPnlLineChart :series="stat.series" />
        </div>
    </template>
  </div>
</template>

<style scoped>
.stat-card {
  background-color: var(--semantic-color-surface-primary);
  padding: var(--semantic-size-inset-md);
  border-radius: var(--semantic-border-radius-surface);
  border: var(--semantic-border-width-default) solid var(--semantic-color-border-default);
  box-shadow: var(--semantic-effect-shadow-elevation-low);
  display: flex;
  transition: box-shadow var(--semantic-animation-duration-interactive) var(--semantic-animation-easing-exit);
}
.stat-card:hover {
  box-shadow: var(--semantic-effect-shadow-elevation-medium);
}

/* --- Layout: Centered (for Gauge/Donut/AvgWinLoss) --- */
.layout--centered {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
}
.layout--centered .text-content {
    display: flex;
    flex-direction: column;
    gap: var(--semantic-size-stack-xs);
}
.layout--centered .chart-content {
    width: var(--semantic-size-component-stat-card-chart-width-desktop);
    flex-shrink: 0;
}

/* --- Layout: P&L --- */
.layout--pnl {
    flex-direction: column;
    justify-content: space-between;
}
.layout--pnl .text-content-full {
    width: 100%;
}
.layout--pnl .chart-content-full {
    width: 100%;
    margin-top: var(--semantic-size-stack-sm);
}

/* --- General Text Styles --- */
.stat-label {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
  white-space: nowrap;
}
.stat-value {
  font: var(--semantic-font-style-metric-display);
  color: var(--semantic-color-text-primary);
  line-height: 1;
}
.stat-value--positive {
  color: var(--semantic-color-feedback-positive-text);
}
.stat-value--negative {
  color: var(--semantic-color-feedback-negative-text);
}


/* --- Win Rate Badges --- */
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

/* --- Header Overlay --- */
:deep(.title-container) {
  align-items: center;
  justify-content: flex-start;
  gap: var(--semantic-size-stack-xxs);
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
</style>