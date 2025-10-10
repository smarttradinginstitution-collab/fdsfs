<template>
  <div class="chart-container">
    <h3 class="title">Comparative Equity Curve</h3>
    <Line :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { Line } from 'vue-chartjs';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const props = defineProps({
  equityCurveData: {
    type: Object,
    required: true,
  },
});

const chartData = computed(() => {
  const filteredSeries = props.equityCurveData.filtered_series;
  const baselineSeries = props.equityCurveData.baseline_series;

  // Use the labels from the longest series to ensure the x-axis is complete
  const labels = filteredSeries.labels.length > baselineSeries.labels.length
    ? filteredSeries.labels
    : baselineSeries.labels;

  return {
    labels: labels,
    datasets: [
      {
        label: 'Filtered Selection',
        backgroundColor: 'rgba(75, 192, 192, 0.5)',
        borderColor: 'rgba(75, 192, 192, 1)',
        data: filteredSeries.data,
        fill: true,
        tension: 0.1,
      },
      {
        label: 'Baseline (All Other Trades)',
        backgroundColor: 'rgba(128, 128, 128, 0.2)',
        borderColor: 'rgba(128, 128, 128, 0.5)',
        data: baselineSeries.data,
        fill: false,
        tension: 0.1,
        borderDash: [5, 5],
      },
    ],
  };
});

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    y: {
      beginAtZero: false,
    },
  },
  plugins: {
    legend: {
      position: 'top',
    },
  },
};
</script>

<style scoped>
.chart-container {
  background-color: var(--semantic-color-surface-primary);
  border-radius: var(--semantic-border-radius-surface);
  padding: var(--semantic-size-inset-lg);
  height: 400px; /* Or any desired height */
}

.title {
  font: var(--semantic-font-style-heading-lg);
  margin-bottom: var(--semantic-size-stack-md);
}
</style>