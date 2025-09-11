<script setup>
import { computed, ref, watch } from 'vue';
import { Bar } from 'vue-chartjs';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { useTradesStore } from '../../stores/trades';
import { useUiStore } from '../../stores/uiStore';
import { useChartColors } from '../../composables/useChartColors';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const uiStore = useUiStore();
const chartKey = ref(0);

watch(() => uiStore.isSidebarCollapsed, () => {
  chartKey.value++;
});

const tradesStore = useTradesStore();
const { feedbackColors, gridColors, isReady } = useChartColors();

const rrDistributionData = computed(() => tradesStore.getRrDistributionData);

const chartData = computed(() => {
  if (!rrDistributionData.value || !isReady.value) {
    return { labels: [], datasets: [] };
  }

  const data = rrDistributionData.value.datasets[0].data;
  const labels = rrDistributionData.value.labels;

  // I primi 3 bucket sono negativi, gli altri positivi
  const backgroundColors = [
    ...Array(3).fill(feedbackColors.value.negative),
    ...Array(3).fill(feedbackColors.value.positive),
  ];

  return {
    labels,
    datasets: [
      {
        data,
        backgroundColor: backgroundColors,
        borderRadius: 4,
        barPercentage: 0.8,
        categoryPercentage: 0.7,
      },
    ],
  };
});

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    y: {
      beginAtZero: true,
      ticks: {
        // Mostra solo interi sull'asse Y
        precision: 0,
        color: gridColors.value?.ticks || '#909093',
      },
      grid: {
        // Disegna solo le griglie orizzontali
        drawOnChartArea: true,
        drawTicks: false,
        color: gridColors.value?.line || '#d8d8d9',
      },
    },
    x: {
      ticks: {
        color: gridColors.value?.ticks || '#909093',
      },
      grid: {
        // Nasconde le griglie verticali
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
      callbacks: {
        label: function (context) {
          let label = context.dataset.label || '';
          if (label) {
            label += ': ';
          }
          if (context.parsed.y !== null) {
            label += `${context.parsed.y} trades`;
          }
          return label;
        },
      },
    },
  },
}));
</script>

<template>
  <div class="widget-card">
    <div class="widget-header">
      <h3 class="widget-title">RR Distribution</h3>
      <!-- IconButton placeholder -->
    </div>
    <div class="widget-content">
      <div class="chart-container">
        <Bar v-if="isReady" :data="chartData" :options="chartOptions" :key="chartKey" />
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
  min-height: 250px; /* Altezza minima per garantire leggibilità */
}
</style>
