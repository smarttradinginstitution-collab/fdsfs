<script setup>
import { computed } from 'vue';
import { Bar } from 'vue-chartjs';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Tooltip } from 'chart.js';
import { formatCurrency } from '../../../../services/formatters.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip);

// --- PROPS ---
const props = defineProps({
  avgWin: { type: Number, required: true },
  avgLoss: { type: Number, required: true }, // Should be a negative number
});

// --- CHART DATA & OPTIONS ---
const chartData = computed(() => ({
  labels: ['Avg. Win', 'Avg. Loss'],
  datasets: [
    {
      data: [props.avgWin, props.avgLoss],
      backgroundColor: [
        'var(--semantic-color-chart-profit)',
        'var(--semantic-color-chart-loss)',
      ],
      borderColor: [
        'var(--semantic-color-chart-profit)',
        'var(--semantic-color-chart-loss)',
      ],
      borderWidth: 1,
      barThickness: 12, // Make bars slimmer
      borderRadius: 4,
    },
  ],
}));

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  indexAxis: 'y', // Horizontal bar chart
  plugins: {
    legend: { display: false },
    tooltip: {
      enabled: false, // Keep it simple, no tooltips
    },
  },
  scales: {
    x: {
      display: false, // Hide X axis
      grid: { display: false },
    },
    y: {
      display: false, // Hide Y axis
      grid: { display: false },
    },
  },
};
</script>

<template>
  <div class="avg-win-loss-container">
    <div class="chart-wrapper">
      <Bar :data="chartData" :options="chartOptions" />
    </div>
    <div class="values-wrapper">
      <span class="value win">{{ formatCurrency(avgWin) }}</span>
      <span class="value loss">{{ formatCurrency(avgLoss) }}</span>
    </div>
  </div>
</template>

<style scoped>
.avg-win-loss-container {
  display: flex;
  align-items: center;
  gap: var(--semantic-size-stack-sm);
  width: 100%;
  height: 60px;
}

.chart-wrapper {
  flex-grow: 1;
  height: 100%;
}

.values-wrapper {
  display: flex;
  flex-direction: column;
  justify-content: space-around;
  align-items: flex-start;
  height: 100%;
  flex-shrink: 0;
}

.value {
  font: var(--semantic-font-style-body-sm);
  font-weight: 500;
}

.value.win {
  color: var(--semantic-color-chart-profit);
}

.value.loss {
  color: var(--semantic-color-chart-loss);
}
</style>