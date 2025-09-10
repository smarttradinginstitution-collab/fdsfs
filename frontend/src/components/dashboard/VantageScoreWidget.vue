<script setup>
import { computed } from 'vue';
import ChartWidget from './ChartWidget.vue';
import VantageScoreSpiderChart from './VantageScoreSpiderChart.vue';

const props = defineProps({
  scores: {
    type: Object,
    required: true,
  },
  finalScore: {
    type: Number,
    required: true,
  }
});

const indicatorStyle = computed(() => ({
  left: `${props.finalScore}%`,
}));
</script>

<template>
  <ChartWidget title="Vantage Score">
    <div class="widget-content">
      <VantageScoreSpiderChart :scores="scores" />

      <footer class="widget-footer">
        <div class="score-display">
          <span class="score-text">Your Vantage Score</span>
          <span class="score-value">{{ finalScore.toFixed(2) }}</span>
        </div>
        <div class="linear-gauge">
          <div class="gauge-bar">
            <div class="gauge-indicator" :style="indicatorStyle"></div>
          </div>
          <div class="gauge-labels">
            <span>0</span>
            <span>20</span>
            <span>40</span>
            <span>60</span>
            <span>80</span>
            <span>100</span>
          </div>
        </div>
      </footer>
    </div>
  </ChartWidget>
</template>

<style scoped>
.widget-content {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-md);
}

.widget-footer {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-sm);
  border-top: var(--base-border-width-1) solid var(--semantic-color-border-default);
  padding-top: var(--semantic-size-inset-md);
}

.score-display {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.score-text {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
}

.score-value {
  font: var(--semantic-font-style-heading-2xl);
  color: var(--semantic-color-text-primary);
}

.linear-gauge {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-xs);
}

.gauge-bar {
  position: relative;
  width: 100%;
  height: 8px;
  background: linear-gradient(to right, #ef4444, #f59e0b, #84cc16);
  border-radius: var(--semantic-border-radius-pill);
}

.gauge-indicator {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 16px;
  height: 16px;
  background-color: #fff;
  border: 2px solid var(--semantic-color-interactive-primary-default);
  border-radius: 50%;
  box-shadow: var(--semantic-effect-shadow-elevation-medium);
}

.gauge-labels {
  display: flex;
  justify-content: space-between;
  font: var(--semantic-font-style-body-xs);
  color: var(--semantic-color-text-tertiary);
}
</style>
