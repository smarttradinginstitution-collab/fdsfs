<script setup>
import { computed } from 'vue';
import { Doughnut } from 'vue-chartjs';
import { Chart as ChartJS, ArcElement, Tooltip } from 'chart.js';

ChartJS.register(ArcElement, Tooltip);

// --- PROPS ---
const props = defineProps({
  winRate: {
    type: Number,
    required: true,
  },
});

// --- CHART DATA & OPTIONS ---
const chartData = computed(() => {
  const wr = Math.max(0, Math.min(props.winRate, 100));
  const lossRate = 100 - wr;

  return {
    datasets: [
      {
        data: [wr, lossRate],
        backgroundColor: [
          '#22c55e', // Hardcoded color for win portion (green-500)
          '#ef4444',   // Hardcoded color for loss portion (red-500)
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
  circumference: 360, // Full circle
  cutout: '75%', // Adjust thickness
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