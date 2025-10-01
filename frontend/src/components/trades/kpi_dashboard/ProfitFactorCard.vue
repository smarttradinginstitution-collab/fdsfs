<script setup>
import { computed } from 'vue';
import { useMetricInfo } from '@/composables/useMetricInfo';

// Component imports
import HeaderInfoOverlay from '@/components/ui/HeaderInfoOverlay.vue';
import GaugeChart from './GaugeChart.vue';

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
  <div class="stat-card-container">
    <div class="header">
        <span class="title">Profit Factor</span>
        <HeaderInfoOverlay :aria-label="`Learn more about ${info.title}`">
            <template #content>
                <h4 class="info-overlay-title">{{ info.title }}</h4>
                <p class="info-overlay-text">{{ info.description }}</p>
            </template>
        </HeaderInfoOverlay>
    </div>

    <div class="content">
      <p class="value">{{ profitFactorLabel }}</p>
      <div class="chart-wrapper">
        <GaugeChart :value="profitFactor" :max-value="5" />
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
  justify-content: space-between;
  align-items: center;
  flex-grow: 1; /* Make content take up available space */
}

.value {
  font: var(--semantic-font-style-metric-display);
  color: var(--semantic-color-text-primary);
  line-height: 1;
}

.chart-wrapper {
  width: 90px;
  height: 45px; /* Half of width for semi-circle */
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