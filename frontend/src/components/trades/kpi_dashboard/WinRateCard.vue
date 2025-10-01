<script setup>
import { computed } from 'vue';
import { useMetricInfo } from '@/composables/useMetricInfo';
import { formatPercentage } from '@/services/formatters';
import HeaderInfoOverlay from '@/components/ui/HeaderInfoOverlay.vue';
import WinRateGauge from './WinRateGauge.vue';

const props = defineProps({
  stats: { type: Object, required: true },
});

const { info } = useMetricInfo('winRate');

const winRate = computed(() => props.stats.win_rate ?? 0);
const formattedWinRate = computed(() => formatPercentage(winRate.value));
</script>

<template>
  <div class="stat-card">
    <div class="header">
      <span class="title">Win %</span>
       <HeaderInfoOverlay :aria-label="`Learn more about ${info.title}`">
        <template #content>
            <h4 class="info-overlay-title">{{ info.title }}</h4>
            <p class="info-overlay-text">{{ info.description }}</p>
        </template>
      </HeaderInfoOverlay>
    </div>
    <div class="content">
      <p class="value">{{ formattedWinRate }}</p>
      <div class="chart-wrapper">
        <WinRateGauge :win-rate="winRate" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.stat-card {
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
  margin-bottom: var(--semantic-size-stack-xs);
}

.title {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
  white-space: nowrap;
}

.content {
  display: flex;
  justify-content: space-between;
  align-items: flex-end; /* Align to bottom */
  flex-grow: 1;
  gap: var(--semantic-size-gutter-md);
}

.value {
  font: var(--semantic-font-style-heading-xl);
  color: var(--semantic-color-text-primary);
  line-height: 1.1;
}

.chart-wrapper {
  width: 60px;
  height: 60px;
  flex-shrink: 0;
}

.info-overlay-title, .info-overlay-text {
  text-align: left;
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