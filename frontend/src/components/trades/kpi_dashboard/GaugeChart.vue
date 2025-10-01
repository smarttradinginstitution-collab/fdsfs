<script setup>
import { computed } from 'vue';
import { Doughnut } from 'vue-chartjs';
import { Chart as ChartJS, ArcElement, Tooltip } from 'chart.js';

ChartJS.register(ArcElement, Tooltip);

// --- PROPS ---
const props = defineProps({
  value: {
    type: Number,
    required: true,
  },
  maxValue: {
    type: Number,
    default: 5, // Default max for Profit Factor
  },
});

// --- CHART DATA & OPTIONS ---
const chartData = computed(() => {
  const safeValue = Math.max(0, Math.min(props.value, props.maxValue));
  const remaining = props.maxValue - safeValue;

  return {
    datasets: [
      {
        data: [safeValue, remaining],
        backgroundColor: [
          'var(--semantic-color-chart-profit)', // Color for the value
          'var(--semantic-color-surface-sunken)', // Color for the remainder
        ],
        borderColor: 'transparent',
        borderWidth: 0,
      },
    ],
  };
});

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  rotation: -90, // Start from the top
  circumference: 180, // Make it a semi-circle
  cutout: '75%', // Adjust thickness of the gauge
  plugins: {
    tooltip: {
      enabled: false, // Disable tooltips
    },
  },
};
</script>

<template>
  <Doughnut :data="chartData" :options="chartOptions" />
</template>