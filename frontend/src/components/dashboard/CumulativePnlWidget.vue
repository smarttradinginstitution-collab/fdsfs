<script setup>
import { computed, ref } from 'vue';
import { Line } from 'vue-chartjs';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from 'chart.js';
import { useTradesStore } from '../../stores/trades';
import { useChartColors } from '../../composables/useChartColors';
import { useChartResize } from '../../composables/useChartResize';
import HeaderInfoOverlay from '../ui/HeaderInfoOverlay.vue';
import BaseWidget from '../layout/BaseWidget.vue';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
);

const tradesStore = useTradesStore();
const { feedbackColors, gridColors, isReady } = useChartColors();
const chartRef = ref(null);

useChartResize(chartRef);

const equityCurveData = computed(() => tradesStore.equityCurveData);

const chartData = computed(() => {
  if (!equityCurveData.value || !chartRef.value || !isReady.value) {
    return { labels: [], datasets: [] };
  }
  const labels = equityCurveData.value.labels || [];
  const data = equityCurveData.value.data || [];
  const ctx = chartRef.value?.chart?.ctx;
  let gradient = 'rgba(22, 163, 74, 0.1)';
  if (ctx && feedbackColors.value.positiveRgb) {
    gradient = ctx.createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, `rgba(${feedbackColors.value.positiveRgb}, 0.25)`);
    gradient.addColorStop(1, `rgba(${feedbackColors.value.positiveRgb}, 0)`);
  }
  return {
    labels,
    datasets: [
      {
        label: 'Cumulative P&L',
        data,
        fill: true,
        borderColor: feedbackColors.value.positive,
        backgroundColor: gradient,
        tension: 0.3,
        pointRadius: 0,
        pointHoverRadius: 5,
      },
    ],
  };
});

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    y: {
      beginAtZero: false,
      ticks: {
        color: gridColors.value?.ticks,
        callback: function(value) {
          if (value >= 1000 || value <= -1000) {
            return (value / 1000).toFixed(2).replace(/\.00$/, '').replace(/(\.\d)0$/, '$1') + 'k';
          }
          return value;
        }
      },
      grid: { color: gridColors.value?.line },
    },
    x: {
      ticks: {
        color: gridColors.value?.ticks,
        callback: function(value) {
          const label = this.getLabelForValue(value);
          if (typeof label === 'string') {
            return label.slice(5, 10);
          }
          return label;
        }
      },
      grid: { display: false },
    },
  },
  plugins: {
    legend: { display: false },
    tooltip: { enabled: true },
  },
  interaction: {
    mode: 'index',
    intersect: false,
  },
}));
</script>

<template>
  <BaseWidget>
    <template #header>
      <HeaderInfoOverlay aria-label="View information about the Daily net cumulative P&L chart">
        <template #title>
          <h3 class="widget-title">Daily net cumulative P&L</h3>
        </template>
        <template #content>
          <h4 class="info-overlay-title">About this Chart</h4>
          <p class="info-overlay-text">
            The Cumulative P&L chart tracks the running total of your net profit and loss over the selected period. Each point on the line represents the sum of all previous profits and losses, providing a clear visual trend of your trading performance.
          </p>
        </template>
      </HeaderInfoOverlay>
    </template>

    <div class="chart-container">
      <Line v-if="isReady" ref="chartRef" :data="chartData" :options="chartOptions" />
    </div>
  </BaseWidget>
</template>

<style scoped>
/* Only styles specific to this widget's internal content remain. */
.widget-title {
  font: var(--semantic-font-style-heading-md);
  color: var(--semantic-color-text-primary);
}

.chart-container {
  position: relative;
  width: 100%;
  height: 100%; /* Take up all available space in the content slot */
  min-height: 250px;
}

/* These styles are for the content passed into the HeaderInfoOverlay */
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
