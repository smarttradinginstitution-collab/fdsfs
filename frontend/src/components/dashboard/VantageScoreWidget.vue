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
import { useTradesStore } from '../../stores/trades';
import { useChartColors } from '../../composables/useChartColors';
import { useChartResize } from '../../composables/useChartResize';
import HeaderInfoOverlay from './HeaderInfoOverlay.vue';

ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
);

const tradesStore = useTradesStore();
const { radarColors } = useChartColors();
const chartRef = ref(null);

// Applica la logica di ridimensionamento al nostro grafico
useChartResize(chartRef);

const vantageScoreData = computed(() => tradesStore.getVantageScoreData);

const chartData = computed(() => {
  if (!vantageScoreData.value) return { labels: [], datasets: [] };

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
  <div class="widget-card">
    <div class="widget-header">
      <HeaderInfoOverlay
        title="Vantage Score"
        infoText="The Vantage Score is a proprietary score that measures your trading performance based on a variety of factors."
      />
    </div>
    <div class="widget-content">
      <div class="chart-container">
        <Radar ref="chartRef" :data="chartData" :options="chartOptions" />
      </div>
    </div>
    <div class="widget-footer">
      <div class="score-container">
        <span class="score-label">Your Vantage Score</span>
        <span class="score-value">{{ score.toFixed(2) }}</span>
        <div class="progress-bar-container">
          <div class="progress-bar" :style="{ width: `${score}%` }"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.widget-card {
  background-color: var(--semantic-color-surface-primary);
  border-radius: var(--semantic-border-radius-surface);
  border: 1px solid var(--semantic-color-border-default);
  box-shadow: var(--semantic-effect-shadow-elevation-low);
  padding: var(--semantic-size-inset-lg);
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-xs);
  height: 100%;
  min-width: 0;
}

.widget-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: var(--semantic-size-inset-md);
  border-bottom: 1px solid var(--semantic-color-border-default);
  min-height: 48px; /* Altezza standard per l'header */
}

.widget-title {
  font: var(--semantic-font-style-heading-xl);
  color: var(--semantic-color-text-primary);
}

.widget-content {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  justify-content: center; /* Centra il grafico */
  min-height: 200px; /* Assicura che il grafico abbia spazio */
}

.chart-container {
  position: relative;
  width: 100%;
  height: 100%;
}

.widget-footer {
  padding-top: var(--semantic-size-inset-md);
}

.score-container {
  display: grid;
  grid-template-areas:
    'label value'
    'bar bar';
  grid-template-columns: auto 1fr;
  align-items: baseline;
  gap: var(--semantic-size-stack-xs) var(--semantic-size-stack-sm);
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
</style>
