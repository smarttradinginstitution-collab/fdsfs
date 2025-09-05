<script setup>
import { computed } from 'vue';
import GaugeChart from './GaugeChart.vue';
import WinLossDonutChart from './WinLossDonutChart.vue';

// --- PROPS ---
const props = defineProps({
  stat: { type: Object, required: true },
});

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

const isProfitFactor = computed(() => props.stat.key === 'profitFactor');
const isWinRate = computed(() => props.stat.key === 'winRate');

</script>

<template>
  <div class="stat-card" :class="{ 'stat-card--with-chart': isProfitFactor || isWinRate }">

    <!-- Layout per Win Rate -->
    <template v-if="isWinRate">
        <div class="text-content">
            <div class="win-rate-label">
                <span class="stat-label">Win %</span>
                <div class="badges">
                    <span class="badge win">{{ stat.wins }}</span>
                    <span class="badge loss">{{ stat.losses }}</span>
                </div>
            </div>
            <p :class="valueClasses">{{ stat.value }}</p>
        </div>
        <div class="chart-content">
            <WinLossDonutChart :wins="stat.wins" :losses="stat.losses" :breakevens="stat.breakevens" />
        </div>
    </template>

    <!-- Layout per Profit Factor -->
    <template v-else-if="isProfitFactor">
        <div class="text-content">
            <p class="stat-label">{{ stat.label }}</p>
            <p :class="valueClasses">{{ stat.value }}</p>
        </div>
        <div class="chart-content">
            <GaugeChart :value="numericValue" />
        </div>
    </template>

    <!-- Layout di default per tutte le altre card -->
    <div v-else class="text-content-default">
      <p class="stat-label">{{ stat.label }}</p>
      <p :class="valueClasses">{{ stat.value }}</p>
    </div>
  </div>
</template>

<style scoped>
/* Stili di base della card */
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

/* Layout di default (verticale) */
.text-content-default {
    display: flex;
    flex-direction: column;
    gap: var(--semantic-size-stack-xs);
}

/* Layout per card con grafici (2 colonne) */
.stat-card--with-chart {
    justify-content: space-between;
    align-items: center;
    gap: var(--semantic-size-stack-md);
}

/* Stili per il testo */
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
.stat-value {
  font: var(--semantic-font-style-heading-xl);
  color: var(--semantic-color-text-primary);
}
.stat-value--positive {
  color: var(--semantic-color-feedback-positive-text);
}
.stat-value--negative {
  color: var(--semantic-color-feedback-negative-text);
}

/* Stili specifici per Win Rate Card */
.win-rate-label {
    display: flex;
    align-items: center;
    gap: var(--semantic-size-stack-sm);
}
.badges {
    display: flex;
    gap: var(--semantic-size-stack-xs);
}
.badge {
    font-size: 0.75rem;
    padding: 0.1rem 0.4rem;
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
    width: 60px; /* Defines a consistent size for the chart container */
}

/* Responsive Stacking per Win Rate Card */
@media (max-width: var(--base-layout-breakpoint-xs)) {
    .stat-card--with-chart {
        flex-direction: column;
        align-items: flex-start;
        gap: var(--semantic-size-stack-md);
    }
}
</style>
