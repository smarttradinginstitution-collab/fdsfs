<script setup>
import { computed } from 'vue';
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
import { useChartColors } from '../../composables/useChartColors';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const props = defineProps({
  plannedRr: {
    type: Number,
    required: true,
    default: 0,
  },
  realizedRr: {
    type: Number,
    required: true,
    default: 0,
  },
});

const { colors, isReady } = useChartColors();

const chartData = computed(() => ({
  labels: ['Planned RR', 'Realized RR'],
  datasets: [
    {
      label: 'Average R:R',
      data: [props.plannedRr, props.realizedRr],
      backgroundColor: [
        colors.value.neutral, // Color for Planned RR
        colors.value.positive, // Color for Realized RR
      ],
      borderRadius: 4,
      barThickness: 30,
    },
  ],
}));

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  indexAxis: 'y', // Horizontal bar chart
  plugins: {
    legend: {
      display: false,
    },
  },
  scales: {
    x: {
      beginAtZero: true,
      grid: {
        color: 'var(--semantic-color-border-default)',
      },
      ticks: {
        color: 'var(--semantic-color-text-tertiary)',
      },
    },
    y: {
      grid: {
        display: false,
      },
      ticks: {
        color: 'var(--semantic-color-text-primary)',
        font: {
          weight: '600',
        },
      },
    },
  },
}));
</script>

<template>
  <div class="bar-chart-container">
    <Bar v-if="isReady" :data="chartData" :options="chartOptions" />
  </div>
</template>

<style scoped>
.bar-chart-container {
  position: relative;
  height: 200px;
}
</style>
