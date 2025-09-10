<!--
// =============================================================================
// FILE: components/dashboard/EquityCurveChart.vue
// DESCRIZIONE: Implementazione del grafico della curva di equity.
// Utilizza Chart.js e vue-chartjs per renderizzare i dati passati tramite props.
// Questo componente è progettato per essere inserito dentro un ChartWidget.
// =============================================================================
-->

<script setup>
import { computed } from 'vue';
import { Line } from 'vue-chartjs';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';

// Registriamo i componenti di Chart.js che useremo.
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

// Definiamo le props che il componente riceverà.
const props = defineProps({
  chartData: {
    type: Object,
    required: true,
    default: () => ({ labels: [], datasets: [] }),
  },
});

// Usiamo una computed property per formattare i dati per Chart.js
const dataForChart = computed(() => {
  return {
    labels: props.chartData.labels,
    datasets: [
      {
        label: 'Cumulative P&L',
        // Colori che usano i token semantici come da blueprint
        backgroundColor: 'var(--semantic-color-feedback-positive-surface)',
        borderColor: 'var(--semantic-color-feedback-positive-text)',
        data: props.chartData.data,
        tension: 0.1,
        fill: true,
      },
    ],
  };
});

// Opzioni di configurazione per il grafico.
const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      mode: 'index',
      intersect: false,
    },
  },
  scales: {
    x: {
      grid: {
        color: 'var(--semantic-color-border-default)',
      },
      ticks: {
        color: 'var(--semantic-color-text-tertiary)',
      },
    },
    y: {
      grid: {
        color: 'var(--semantic-color-border-default)',
      },
      ticks: {
        color: 'var(--semantic-color-text-tertiary)',
        callback: function(value) {
          // Potremmo voler rendere la valuta dinamica in futuro
          return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);
        }
      },
    },
  },
}));

// Verifichiamo se ci sono dati validi da mostrare.
const hasData = computed(() => {
  return props.chartData && props.chartData.data && props.chartData.data.length > 0;
});
</script>

<template>
  <div class="chart-container">
    <Line v-if="hasData" :data="dataForChart" :options="chartOptions" />
    <div v-else class="chart-placeholder">
      <p class="placeholder-text">No trading data available for the selected period.</p>
    </div>
  </div>
</template>

<style scoped>
/*
  Diamo un'altezza fissa al contenitore del grafico per evitare che
  il layout cambi durante il caricamento dei dati.
*/
.chart-container {
  position: relative;
  height: 280px; /* Altezza leggermente ridotta per adattarsi meglio al widget */
}

.chart-placeholder {
  width: 100%;
  height: 100%;
  display: grid;
  place-items: center;
  border-radius: var(--semantic-border-radius-interactive);
  background-color: var(--semantic-color-surface-page);
}
.placeholder-text {
    color: var(--semantic-color-text-tertiary);
    font: var(--semantic-font-style-body-md);
}
</style>
