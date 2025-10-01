<script setup>
import { Line } from 'vue-chartjs';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Filler,
} from 'chart.js';

// Register the necessary components with Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Filler
);

// --- PROPS ---
defineProps({
  chartData: {
    type: Object,
    required: true,
  },
});

// --- CHART OPTIONS ---
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    x: {
      display: false, // Hide X-axis labels and grid
    },
    y: {
      display: false, // Hide Y-axis labels and grid
      beginAtZero: false,
    },
  },
  plugins: {
    legend: {
      display: false, // Hide the legend
    },
    tooltip: {
      enabled: false, // Disable tooltips on hover
    },
  },
  elements: {
    line: {
      tension: 0.4, // Makes the line smooth
    },
    point: {
      radius: 0, // Hides the points on the line
    },
  },
  layout: {
    padding: {
      top: 5, // Add some padding to prevent clipping at the top
    }
  }
};
</script>

<template>
  <Line :data="chartData" :options="chartOptions" />
</template>