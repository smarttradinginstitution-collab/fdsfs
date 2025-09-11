<script setup>
import { computed, ref, onMounted } from 'vue';
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
import IconButton from '../ui/IconButton.vue';
import MoreHorizontalIcon from '../icons/MoreHorizontalIcon.vue';

function openMenu() {
  console.log('Menu button clicked');
}

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
const tooltipColors = ref({
  backgroundColor: '#ffffff',
  titleColor: '#000000',
  bodyColor: '#666666',
  borderColor: '#dddddd',
});

onMounted(() => {
  const style = getComputedStyle(document.documentElement);
  tooltipColors.value = {
    backgroundColor: style.getPropertyValue('--semantic-color-surface-primary').trim(),
    titleColor: style.getPropertyValue('--semantic-color-text-primary').trim(),
    bodyColor: style.getPropertyValue('--semantic-color-text-secondary').trim(),
    borderColor: style.getPropertyValue('--semantic-color-border-default').trim(),
  };
});

// Applica la logica di ridimensionamento al nostro grafico
useChartResize(chartRef);

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
      backgroundColor: tooltipColors.value.backgroundColor,
      titleColor: tooltipColors.value.titleColor,
      bodyColor: tooltipColors.value.bodyColor,
      borderColor: tooltipColors.value.borderColor,
      borderWidth: 1,
      cornerRadius: 8,
      padding: 12,
      displayColors: false,
      callbacks: {
        label: function(context) {
          let label = context.dataset.label || '';
          if (label) {
            label += ': ';
          }
          if (context.parsed.y !== null) {
            label += new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(context.parsed.y);
          }
          return label;
        }
      }
    },
  },
}));
</script>

<template>
  <div class="widget-card">
    <div class="widget-header">
      <h4 class="widget-title">Daily net cumulative P&L</h4>
      <IconButton aria-label="More options" @click="openMenu">
        <MoreHorizontalIcon />
      </IconButton>
    </div>
    <div class="widget-separator"></div>
    <div class="widget-content">
      <div class="chart-container">
        <Line v-if="isReady" ref="chartRef" :data="chartData" :options="chartOptions" />
      </div>
    </div>
  </div>
</template>

<style scoped>
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.widget-card {
  animation: fadeIn 0.5s ease-in-out forwards;
  background-color: var(--semantic-color-surface-primary);
  border-radius: var(--semantic-border-radius-surface);
  border: 1px solid var(--semantic-color-border-default);
  box-shadow: var(--semantic-effect-shadow-elevation-low);
  padding: var(--semantic-size-inset-lg);
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-md);
  height: 100%;
  min-width: 0; /*  CRUCIALE: Permette al flex item di restringersi oltre la larghezza del suo contenuto. */
}

.widget-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.widget-title {
  font: var(--semantic-font-style-heading-lg);
  color: var(--semantic-color-text-secondary);
}

.widget-separator {
  height: 1px;
  background-color: var(--semantic-color-border-default);
  width: 100%;
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
