<script setup>
import { computed, ref, onMounted } from 'vue';
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

// --- REFS ---
const chartBackgroundColor = ref('transparent');
const chartBorderColor = ref('transparent');

// --- LIFECYCLE HOOKS ---
onMounted(() => {
  // This code runs only on the client, after the component is mounted
  // and has access to the DOM and computed styles.
  const style = getComputedStyle(document.documentElement);

  // FIX: Use the correct CSS variable for the RGB values.
  const profitRgb = style.getPropertyValue('--semantic-color-feedback-positive-background-rgb').trim();

  // Set the border color (fully opaque)
  chartBorderColor.value = `rgba(${profitRgb}, 1)`;

  // Create the gradient for the background fill
  const ctx = document.createElement('canvas').getContext('2d');
  const gradient = ctx.createLinearGradient(0, 0, 0, 80); // Gradient height
  gradient.addColorStop(0, `rgba(${profitRgb}, 0.3)`);
  gradient.addColorStop(1, `rgba(${profitRgb}, 0)`);

  // Set the background color to the created gradient
  chartBackgroundColor.value = gradient;
});


// --- CHART DATA & OPTIONS ---
const chartData = computed(() => {
  const labels = props.series.map(p => p.trade_order);
  const data = props.series.map(p => p.cumulative_pnl);

  return {
    labels: labels,
    datasets: [
      {
        data: data,
        borderColor: chartBorderColor.value,
        backgroundColor: chartBackgroundColor.value,
        tension: 0.4,
        fill: true,
        pointRadius: 0,
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
    <!-- v-if ensures the chart only renders after the colors have been calculated on mount -->
    <Line v-if="chartBackgroundColor !== 'transparent'" :data="chartData" :options="chartOptions" />
  </div>
</template>

<style scoped>
.mini-chart-container {
  width: 100%;
  height: 60px;
  position: relative;
}
</style>