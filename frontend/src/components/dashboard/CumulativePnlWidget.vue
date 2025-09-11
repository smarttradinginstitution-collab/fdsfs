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

const equityCurveData = computed(() => tradesStore.equityCurveData);

const chartData = computed(() => {
  if (!equityCurveData.value || !chartRef.value || !isReady.value) {
    return { labels: [], datasets: [] };
  }

  const labels = equityCurveData.value.labels || [];
  const data = equityCurveData.value.data || [];
  const ctx = chartRef.value?.chart?.ctx;

  let gradient = 'rgba(22, 163, 74, 0.1)'; // Fallback
  if (ctx && feedbackColors.value.positiveRgb) {
    gradient = ctx.createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, `rgba(${feedbackColors.value.positiveRgb}, 0.5)`);
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
      },
      grid: {
        color: gridColors.value?.line,
      },
    },
    x: {
      ticks: {
        color: gridColors.value?.ticks,
      },
      grid: {
        display: false,
      },
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
</script>

<template>
  <div class="widget-card">
    <div class="widget-header">
      <h3 class="widget-title">Daily net cumulative P&L</h3>
      <!-- IconButton placeholder -->
    </div>
    <div class="widget-content">
      <div class="chart-container">
        <Line v-if="isReady" ref="chartRef" :data="chartData" :options="chartOptions" />
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
  gap: var(--semantic-size-stack-md);
  height: 100%;
}

.widget-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.widget-title {
  font: var(--semantic-font-style-heading-xl);
  color: var(--semantic-color-text-primary);
}

.widget-content {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.chart-container {
  position: relative;
  width: 100%;
  flex-grow: 1;
  min-height: 250px;
}
</style>
