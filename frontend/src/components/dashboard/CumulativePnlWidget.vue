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
import InfoPopover from '../ui/InfoPopover.vue';

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
        callback: function(value) {
          if (value >= 1000 || value <= -1000) {
            const thousands = value / 1000;
            // Format to max 2 decimal places, and remove trailing .00 or .0
            return thousands.toFixed(2).replace(/\.00$/, '').replace(/(\.\d)0$/, '$1') + 'k';
          }
          return value;
        }
      },
      grid: {
        color: gridColors.value?.line,
      },
    },
    x: {
      ticks: {
        color: gridColors.value?.ticks,
        callback: function(value) {
          // 'this' refers to the scale instance
          const label = this.getLabelForValue(value);
          if (typeof label === 'string') {
            // Assuming label format is 'YYYY-MM-DD HH:MM'
            return label.slice(5, 10); // Extracts 'MM-DD'
          }
          return label;
        }
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
  interaction: {
    mode: 'index',
    intersect: false,
  },
}));
</script>

<template>
  <div class="widget-card">
    <div class="widget-header">
      <div class="widget-title-container">
        <h3 class="widget-title">Daily net cumulative P&L</h3>
        <InfoPopover>
          <p>This chart shows the daily running total of your net profit and loss.</p>
          <p>It provides a visual representation of your trading performance over time.</p>
        </InfoPopover>
      </div>
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
  min-width: 0; /*  CRUCIALE: Permette al flex item di restringersi oltre la larghezza del suo contenuto. */
}

.widget-header {
  display: flex;
  align-items: center;
  padding-bottom: var(--semantic-size-stack-xs);
  border-bottom: 1px solid var(--semantic-color-border-default);
}

.widget-title-container {
  display: flex;
  align-items: center;
  gap: var(--semantic-size-stack-sm);
}

.widget-title {
  font: var(--semantic-font-style-heading-sm);
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
