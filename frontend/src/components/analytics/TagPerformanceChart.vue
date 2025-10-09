<template>
  <div class="chart-container">
    <Bar v-if="chartData.datasets.length" :data="chartData" :options="chartOptions" />
    <p v-else>No data available for chart.</p>
  </div>
</template>

<script setup>
import { computed, defineProps } from 'vue';
import { Bar } from 'vue-chartjs';
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
} from 'chart.js';
import { formatCurrency } from '@/services/formatters';

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale);

const props = defineProps({
  stats: {
    type: Array,
    required: true,
  },
});

const chartData = computed(() => {
  const labels = props.stats.map(s => s.tag_name);
  const data = props.stats.map(s => s.total_pnl);
  const backgroundColors = props.stats.map(s => s.tag_color);

  return {
    labels,
    datasets: [
      {
        label: 'Total P&L',
        data,
        backgroundColor: backgroundColors,
        borderColor: backgroundColors,
        borderWidth: 1,
      },
    ],
  };
});

const chartOptions = {
  indexAxis: 'x', // Vertical bar chart
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      callbacks: {
        label: function (context) {
          let label = context.dataset.label || '';
          if (label) {
            label += ': ';
          }
          if (context.parsed.x !== null) {
            label += formatCurrency(context.parsed.x);
          }
          return label;
        },
      },
    },
  },
  scales: {
    x: {
      ticks: {
        callback: function (value) {
          return formatCurrency(value);
        },
      },
    },
  },
};
</script>

<style scoped>
.chart-container {
  position: relative;
  height: 400px;
}
</style>