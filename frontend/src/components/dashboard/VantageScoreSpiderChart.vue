<script setup>
import { computed } from 'vue';
import { Radar } from 'vue-chartjs';
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
);

const props = defineProps({
  scores: {
    type: Object,
    required: true,
    default: () => ({
      'Win %': 0,
      'Profit factor': 0,
      'Avg win/loss': 0,
      'Recovery factor': 0,
      'Max drawdown': 0,
      'Consistency': 0,
    }),
  },
});

const chartData = computed(() => {
  const labels = Object.keys(props.scores);
  const data = Object.values(props.scores);

  return {
    labels,
    datasets: [
      {
        label: 'Vantage Score',
        data,
        backgroundColor: 'rgba(37, 99, 235, 0.2)',
        borderColor: 'var(--semantic-color-interactive-primary-default)',
        pointBackgroundColor: 'var(--semantic-color-interactive-primary-default)',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'var(--semantic-color-interactive-primary-default)',
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
  },
  scales: {
    r: {
      angleLines: {
        color: 'var(--semantic-color-border-default)',
      },
      grid: {
        color: 'var(--semantic-color-border-default)',
      },
      pointLabels: {
        color: 'var(--semantic-color-text-secondary)',
        font: {
          size: 12,
        },
      },
      ticks: {
        display: false, // Hide the radial axis numbers for a cleaner look
        stepSize: 20,
      },
      suggestedMin: 0,
      suggestedMax: 100,
    },
  },
};
</script>

<template>
  <div class="radar-chart-container">
    <Radar :data="chartData" :options="chartOptions" />
  </div>
</template>

<style scoped>
.radar-chart-container {
  position: relative;
  height: 280px; /* Adjust height for better spacing */
}
</style>
