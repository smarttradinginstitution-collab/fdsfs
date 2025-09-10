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
import { useChartColors } from '../../composables/useChartColors';

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

const { colors, isReady } = useChartColors();

const hexToRgba = (hex, alpha = 1) => {
  if (!hex || typeof hex !== 'string') return `rgba(0,0,0,${alpha})`;
  const bigint = parseInt(hex.slice(1), 16);
  const r = (bigint >> 16) & 255;
  const g = (bigint >> 8) & 255;
  const b = bigint & 255;
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
};

const chartData = computed(() => {
  const labels = Object.keys(props.scores);
  const data = Object.values(props.scores);

  return {
    labels,
    datasets: [
      {
        label: 'Vantage Score',
        data,
        backgroundColor: hexToRgba(colors.value.neutral, 0.2),
        borderColor: colors.value.neutral,
        pointBackgroundColor: colors.value.neutral,
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: colors.value.neutral,
      },
    ],
  };
});

const chartOptions = computed(() => ({
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
        color: hexToRgba(colors.value.textTertiary, 0.2),
      },
      grid: {
        color: hexToRgba(colors.value.textTertiary, 0.2),
      },
      pointLabels: {
        color: colors.value.textTertiary,
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
}));
</script>

<template>
  <div class="radar-chart-container">
    <Radar v-if="isReady" :data="chartData" :options="chartOptions" />
  </div>
</template>

<style scoped>
.radar-chart-container {
  position: relative;
  height: 280px; /* Adjust height for better spacing */
}
</style>
