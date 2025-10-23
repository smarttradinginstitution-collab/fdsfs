<template>
  <div class="relative w-full h-48 md:h-full flex items-center justify-center">
    <Doughnut :data="chartData" :options="chartOptions" />
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
  /**
   * The cluster summary object from the SOA analysis.
   * Keys are cluster labels (e.g., 'A'), and values are objects
   * containing cluster metrics, including 'trade_count'.
   * @type {Object}
   */
  clustersSummary: {
    type: Object,
    required: true,
  },
});

const chartData = computed(() => {
  const labels = Object.keys(props.clustersSummary);
  const data = labels.map(label => props.clustersSummary[label].trade_count);

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
        data: data,
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
