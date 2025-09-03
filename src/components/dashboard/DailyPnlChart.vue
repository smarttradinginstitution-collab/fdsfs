<script setup>
import { computed } from 'vue';
import { Line } from 'vue-chartjs';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Filler,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Filler,
  Legend
);

const props = defineProps({
  chartData: {
    type: Object,
    required: true,
    default: () => ({ labels: [], data: [] })
  }
});

const data = computed(() => {
  // The last point in the data array is the final cumulative P&L
  const isPositive = props.chartData.data.length > 0 ? props.chartData.data[props.chartData.data.length - 1] >= 0 : true;

  // These are approximations. In a real scenario, we'd use a plugin to get CSS variables.
  const positiveColor = 'rgba(16, 185, 129, 0.2)';
  const positiveBorder = 'rgb(16, 185, 129)';
  const negativeColor = 'rgba(239, 68, 68, 0.2)';
  const negativeBorder = 'rgb(239, 68, 68)';

  return {
    labels: props.chartData.labels,
    datasets: [
      {
        label: 'Cumulative P&L',
        backgroundColor: isPositive ? positiveColor : negativeColor,
        borderColor: isPositive ? positiveBorder : negativeBorder,
        data: props.chartData.data,
        tension: 0.3,
        fill: true,
        pointRadius: 0,
        pointHoverRadius: 5,
        borderWidth: 2,
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
      display: false,
    },
    y: {
      display: false,
    },
  },
};

const hasData = computed(() => {
  return props.chartData && props.chartData.data.length > 0;
});
</script>

<template>
  <div class="chart-container">
    <Line v-if="hasData" :data="data" :options="chartOptions" />
    <div v-else class="chart-placeholder">
      <p>No trades to display.</p>
    </div>
  </div>
</template>

<style scoped>
.chart-container {
  position: relative;
  height: 100%;
  min-height: 150px;
}
.chart-placeholder {
  width: 100%;
  height: 100%;
  display: grid;
  place-items: center;
  border-radius: var(--semantic-border-radius-interactive);
  background-color: var(--semantic-color-surface-page);
  color: var(--semantic-color-text-tertiary);
  font: var(--semantic-font-style-body-sm);
}
</style>
