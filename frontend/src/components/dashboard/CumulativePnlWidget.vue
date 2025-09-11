<script setup>
import { computed, ref, onMounted, watch } from 'vue';
import { useTradesStore } from '../../stores/trades';
import { Line } from 'vue-chartjs';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Filler, Legend } from 'chart.js';
import IconButton from '../ui/IconButton.vue';
import InfoIcon from '../icons/InfoIcon.vue';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Filler, Legend);

const tradesStore = useTradesStore();
const chartRef = ref(null);

const equityCurve = computed(() => tradesStore.equityCurveData);

// This function creates the gradient. It needs the chart's context.
const createGradient = (context) => {
  const chart = context.chart;
  const { ctx, chartArea } = chart;
  if (!chartArea) {
    // This case happens on initial render or if the chart is not visible.
    return null;
  }

  // Colore derivato da --base-color-green-600-rgb (22, 163, 74)
  const green_rgb = '22, 163, 74';

  const gradient = ctx.createLinearGradient(0, chartArea.bottom, 0, chartArea.top);
  gradient.addColorStop(0, `rgba(${green_rgb}, 0)`);
  gradient.addColorStop(1, `rgba(${green_rgb}, 0.5)`); // Opacità al 50% in alto
  return gradient;
};

const chartData = computed(() => {
  const labels = equityCurve.value?.labels || [];
  const data = equityCurve.value?.data || [];
  return {
    labels: labels,
    datasets: [
      {
        label: 'Cumulative P&L',
        borderColor: 'var(--color-border-positive-strong)',
        borderWidth: 2,
        pointRadius: 0,
        tension: 0.1, // Makes the line slightly curved
        data: data,
        fill: true,
        backgroundColor: (context) => createGradient(context),
      },
    ],
  };
});

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      mode: 'index',
      intersect: false,
    },
  },
  scales: {
    x: {
      grid: {
        display: false,
      },
      ticks: {
        color: 'var(--color-text-secondary)',
        font: { size: 12 },
        maxRotation: 0,
        autoSkip: true,
        maxTicksLimit: 6, // Limit the number of visible ticks
      },
    },
    y: {
      border: {
        display: false,
      },
      grid: {
        color: 'var(--color-border-subtle)',
      },
      ticks: {
        color: 'var(--color-text-secondary)',
        font: { size: 12 },
        // Format to '10k', '20k' etc.
        callback: function(value) {
          if (value === 0) return '$0';
          return '$' + (value / 1000) + 'k';
        },
      },
    },
  },
};

// We need to watch for the chartRef to be available and then update the gradient
// Rimosso il watch, Chart.js v4+ può gestire una funzione per backgroundColor
// che viene chiamata al momento del rendering, garantendo che il contesto sia disponibile.
</script>

<template>
  <div class="cumulative-pnl-widget card">
    <div class="card-header">
      <h3 class="widget-title">Daily Net Cumulative P&L</h3>
      <IconButton>
        <InfoIcon />
      </IconButton>
    </div>
    <div class="chart-container">
      <Line v-if="equityCurve?.data?.length > 0" ref="chartRef" :data="chartData" :options="chartOptions" />
      <div v-else class="loading-placeholder">Loading Chart Data...</div>
    </div>
  </div>
</template>

<style scoped>
.card {
  background-color: var(--color-background-card-primary);
  border: 1px solid var(--color-border-card-primary);
  border-radius: var(--semantic-border-radius-lg);
  box-shadow: var(--effect-shadow-small);
  padding: var(--semantic-size-inset-lg);
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-md);
  color: var(--color-text-primary);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.widget-title {
  font: var(--typography-style-heading-h5);
}

.chart-container {
  position: relative;
  height: 280px; /* Adjusted height */
}

.loading-placeholder {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: var(--color-text-secondary);
}
</style>
