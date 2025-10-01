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
    default: 5,
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
          '#22c55e', // Hardcoded color for profit (green-500)
          '#e9e9ea', // Hardcoded color for remainder (gray-100)
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
  rotation: -90,
  circumference: 180,
  cutout: '75%',
  plugins: {
    tooltip: {
      enabled: false,
    },
  },
};
</script>

<template>
  <Doughnut :data="chartData" :options="chartOptions" />
</template>