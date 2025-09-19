<!--
// =============================================================================
// FILE: components/analytics/PerformanceByHourChart.vue
// DESCRIZIONE: Widget che visualizza la performance (P&L) suddivisa per
// ora del giorno, utilizzando un grafico a barre.
// =============================================================================
-->
<script setup>
import { computed } from 'vue';
import { useTradesStore } from '../../stores/trades';
import BaseBarChart from '../charts/BaseBarChart.vue';
import BaseWidget from '../layout/BaseWidget.vue';

const tradesStore = useTradesStore();

// Il nuovo getter `performanceByHourData` fornisce già i dati nel formato corretto
// per Chart.js, inclusi etichette e dataset con colori dinamici.
const chartData = computed(() => tradesStore.performanceByHourData);

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false,
    },
    title: {
      display: false, // Il titolo è gestito dal BaseWidget
    },
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: {
        color: '#8A8A8E', // Colore dei tick da rendere dinamico con i token in futuro
        callback: function (value) {
          return '$' + value.toLocaleString();
        },
      },
      grid: {
        color: '#333333', // Colore della griglia da rendere dinamico
      },
    },
    x: {
      ticks: {
        color: '#8A8A8E',
      },
      grid: {
        display: false,
      },
    },
  },
}));
</script>

<template>
  <BaseWidget>
    <template #header>
      <h3 class="widget-title">Performance by Hour</h3>
    </template>
    <div class="chart-container">
      <BaseBarChart :chart-data="chartData" :chart-options="chartOptions" />
    </div>
  </BaseWidget>
</template>

<style scoped>
.widget-title {
  font: var(--semantic-font-style-heading-md);
  color: var(--semantic-color-text-primary);
}

.chart-container {
  height: 250px;
  position: relative;
}
</style>
