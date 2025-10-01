<script setup>
import { computed } from 'vue';
import { Line } from 'vue-chartjs';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Filler } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Filler);

// --- PROPS ---
const props = defineProps({
  series: {
    type: Array,
    required: true,
    default: () => [],
  },
});

// --- CHART DATA & OPTIONS ---
const chartData = computed(() => {
  const labels = props.series.map(p => p.trade_order);
  const data = props.series.map(p => p.cumulative_pnl);

  // Create a gradient for the background fill
  const ctx = document.createElement('canvas').getContext('2d');
  const gradient = ctx.createLinearGradient(0, 0, 0, 80); // Adjust gradient height
  gradient.addColorStop(0, `rgba(var(--semantic-color-chart-profit-rgb), 0.3)`);
  gradient.addColorStop(1, `rgba(var(--semantic-color-chart-profit-rgb), 0)`);


  return {
    labels: labels,
    datasets: [
      {
        data: data,
        borderColor: 'var(--semantic-color-chart-profit)',
        backgroundColor: gradient,
        tension: 0.4,
        fill: true,
        pointRadius: 0, // No points on the line
        borderWidth: 2,
      },
    ],
  };
});

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: { enabled: false },
  },
  scales: {
    x: { display: false },
    y: { display: false },
  },
  elements: {
    line: {
      borderCapStyle: 'round',
    },
  },
};
</script>

<template>
  <div class="mini-chart-container">
    <Line :data="chartData" :options="chartOptions" />
  </div>
</template>

<style scoped>
.mini-chart-container {
  /* Set a specific height and width for the chart area */
  width: 100%;
  height: 60px; /* Adjust height as needed */
  position: relative;
}
</style>