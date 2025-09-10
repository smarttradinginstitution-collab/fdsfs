<script setup>
import { computed } from 'vue';
import { Doughnut } from 'vue-chartjs';
import { Chart as ChartJS, ArcElement, Tooltip } from 'chart.js';
import { useChartColors } from '../../composables/useChartColors';

ChartJS.register(ArcElement, Tooltip);

const props = defineProps({
  score: {
    type: Number,
    required: true,
    default: 0,
  },
});

const { colors, isReady } = useChartColors();

const chartData = computed(() => {
  // A gauge chart is a doughnut chart where we only show the top half.
  // The score is the first value, and the remainder is the second value.
  const scoreValue = Math.max(0, Math.min(100, props.score)); // Clamp score between 0-100
  const remainder = 100 - scoreValue;

  return {
    datasets: [
      {
        data: [scoreValue, remainder],
        backgroundColor: [
          colors.value.positive, // Color for the score
          '#E5E7EB', // A neutral color for the remainder
        ],
        borderColor: [
          colors.value.positive,
          '#E5E7EB',
        ],
        borderWidth: 0,
        circumference: 180, // Half circle
        rotation: -90, // Start from the left
      },
    ],
  };
});

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: '70%', // Adjust for thickness of the gauge
  plugins: {
    tooltip: {
      enabled: false, // Disable tooltips for a cleaner look
    },
  },
};
</script>

<template>
  <div class="gauge-container">
    <Doughnut v-if="isReady" :data="chartData" :options="chartOptions" />
    <div class="gauge-label">
      <span class="score-value">{{ score.toFixed(0) }}</span>
      <span class="score-text">Vantage Score</span>
    </div>
  </div>
</template>

<style scoped>
.gauge-container {
  position: relative;
  height: 200px; /* Adjust height as needed */
  display: flex;
  justify-content: center;
  align-items: center;
}
.gauge-label {
  position: absolute;
  top: 65%; /* Adjust to center vertically inside the gauge arc */
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}
.score-value {
  display: block;
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--semantic-color-text-primary);
}
.score-text {
  display: block;
  font-size: 0.875rem;
  color: var(--semantic-color-text-secondary);
}
</style>
