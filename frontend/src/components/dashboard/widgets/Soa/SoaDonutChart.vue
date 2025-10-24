<template>
  <div class="relative w-full h-48 md:h-full flex items-center justify-center">
    <Doughnut v-if="chartData.datasets.length > 0 && chartData.datasets[0].data.length > 0" :data="chartData" :options="chartOptions" />
    <p v-else class="text-gray-400">No cluster data available.</p>
  </div>
</template>

<script setup>
/**
 * @file SoaDonutChart.vue
 * @description
 * Renders a Doughnut chart to visualize the distribution of trades across
 * different SOA clusters.
 */
import { computed } from 'vue';
import { Doughnut } from 'vue-chartjs';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend);

const props = defineProps({
  data: {
    type: Object,
    default: () => ({}),
  },
});

const chartData = computed(() => {
  if (!props.data || Object.keys(props.data).length === 0) {
    return { labels: [], datasets: [] };
  }

  const labels = Object.keys(props.data);
  const chartValues = Object.values(props.data);

  return {
    labels: labels,
    datasets: [
      {
        backgroundColor: [
          '#4A90E2', // Blue
          '#F5A623', // Orange
          '#BD10E0', // Purple
          '#7ED321', // Green
          '#D0021B', // Red
        ],
        data: chartValues,
      },
    ],
  };
});

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'right',
      labels: {
        color: '#FFFFFF', // White text for legend
      },
    },
  },
};
</script>
