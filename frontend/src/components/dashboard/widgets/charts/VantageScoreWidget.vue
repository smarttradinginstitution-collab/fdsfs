<script setup>
import { computed, ref } from 'vue';
import { Radar } from 'vue-chartjs';
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from 'chart.js';
import { useTradesStore } from '../../../../stores/trades';
import { useChartColors } from '../../../../composables/useChartColors';
import { useChartResize } from '../../../../composables/useChartResize';
import BaseWidget from '../../../layout/BaseWidget.vue';
import HeaderInfoOverlay from '../../../ui/HeaderInfoOverlay.vue';

ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
);

const tradesStore = useTradesStore();
const { radarColors, isReady } = useChartColors();
const chartRef = ref(null);

useChartResize(chartRef);

const vantageScoreData = computed(() => tradesStore.getVantageScoreData);

const chartData = computed(() => {
  if (!vantageScoreData.value || !isReady.value) return { labels: [], datasets: [] };

  const labels = Object.keys(vantageScoreData.value.metrics);
  const data = Object.values(vantageScoreData.value.metrics);

  return {
    labels,
    datasets: [
      {
        label: 'Zella Score',
        backgroundColor: radarColors.value.backgroundColor,
        borderColor: radarColors.value.borderColor,
        pointBackgroundColor: radarColors.value.borderColor,
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: radarColors.value.borderColor,
        data,
      },
    ],
  };
});

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    r: {
      angleLines: {
        color: radarColors.value.gridColor,
      },
      grid: {
        color: radarColors.value.gridColor,
      },
      pointLabels: {
        color: radarColors.value.pointLabelColor,
        font: {
          family: 'var(--font-family-sans)',
          size: 12,
        },
      },
      ticks: {
        color: radarColors.value.tickColor,
        backdropColor: 'transparent',
        stepSize: 20,
        font: {
            size: 10,
        }
      },
      min: 0,
      max: 100,
    },
  },
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      enabled: true,
    },
  },
}));

const score = computed(() => vantageScoreData.value?.score || 0);
</script>

<template>
  <BaseWidget>
    <template #header>
      <HeaderInfoOverlay aria-label="View information about the Zella Score">
        <template #title>
          <h3 class="widget-title">Vantage Score</h3>
        </template>
        <template #content>
          <h4 class="info-overlay-title">About this Chart</h4>
          <p class="info-overlay-text">
            The Vantage Score is a proprietary metric that evaluates your trading performance across five key dimensions: Profitability, Consistency, Risk Management, Win Rate, and Asset Allocation. A higher score indicates a more balanced and effective trading strategy.
          </p>
        </template>
      </HeaderInfoOverlay>
    </template>

    <div class="vantage-score-content">
      <div class="chart-container">
          <Radar v-if="isReady" ref="chartRef" :data="chartData" :options="chartOptions" />
      </div>
      <div class="score-container">
          <span class="score-label">Your Score</span>
          <span class="score-value">{{ score.toFixed(2) }}</span>
          <div class="progress-bar-container">
            <div class="progress-bar" :style="{ width: `${score}%` }"></div>
          </div>
      </div>
    </div>
  </BaseWidget>
</template>

<style scoped>
.widget-title {
  font: var(--semantic-font-style-heading-md);
  color: var(--semantic-color-text-primary);
}

.vantage-score-content {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  min-height: 0; /* Crucial for allowing content to shrink correctly in a flex container */
}

.chart-container {
  position: relative;
  flex-grow: 1;
  width: 100%;
  min-height: 0;
}

.score-container {
  display: grid;
  grid-template-areas:
    'label value'
    'bar bar';
  grid-template-columns: auto 1fr;
  align-items: baseline;
  gap: var(--semantic-size-stack-xs) var(--semantic-size-stack-sm);
  margin-top: 0;
  flex-shrink: 0; /* Prevent the score section from shrinking */
}

.score-label {
  grid-area: label;
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
}

.score-value {
  grid-area: value;
  font: var(--semantic-font-style-heading-2xl);
  color: var(--semantic-color-text-primary);
  justify-self: end;
}

.progress-bar-container {
  grid-area: bar;
  width: 100%;
  background-color: var(--semantic-color-surface-secondary);
  border-radius: var(--semantic-border-radius-pill);
  height: 8px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background-color: var(--semantic-color-interactive-primary-default);
  border-radius: var(--semantic-border-radius-pill);
  transition: width 0.5s ease-in-out;
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
