<template>
  <div class="relative">
    <Doughnut :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { Doughnut } from 'vue-chartjs';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend);

const props = defineProps({
  clustersSummary: {
    type: Object,
    required: true,
  },
});

const chartData = computed(() => {
  const labels = Object.keys(props.clustersSummary);
  const data = labels.map(label => props.clustersSummary[label].trade_count);
  const backgroundColors = labels.map(label => {
    switch (label) {
      case 'A': return 'var(--semantic-color-feedback-positive-default)';
      case 'B': return 'var(--semantic-color-feedback-warning-default)';
      case 'C': return 'var(--semantic-color-feedback-neutral-default)';
      case 'D': return 'var(--semantic-color-feedback-negative-default)';
      case 'E': return 'var(--semantic-color-background-neutral-subtle)';
      default: return 'var(--semantic-color-background-neutral-subtle)';
    }
  });

  return {
    labels: labels.map(label => `Cluster ${label}`),
    datasets: [
      {
        backgroundColor: backgroundColors,
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
    },
    tooltip: {
      callbacks: {
        label: function(context) {
          let label = context.label || '';
          if (label) {
            label += ': ';
          }
          if (context.parsed !== null) {
            const total = context.dataset.data.reduce((acc, value) => acc + value, 0);
            const percentage = ((context.raw / total) * 100).toFixed(2);
            label += `${context.raw} trades (${percentage}%)`;
          }
          return label;
        }
      }
    }
  },
};
</script>
