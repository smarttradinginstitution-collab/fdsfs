<!--
// =============================================================================
// FILE: components/analytics/PerformanceByDayChart.vue
// DESCRIZIONE: Un widget che visualizza la performance del trading (P&L)
// suddivisa per giorno della settimana, utilizzando un grafico a barre.
// =============================================================================
-->
<script setup>
import { computed } from 'vue';
import { useTradesStore } from '../../stores/trades';
import BaseBarChart from '../charts/BaseBarChart.vue';
import BaseWidget from '../layout/BaseWidget.vue';

// Utilizziamo uno schema di colori predefinito. In futuro, questo potrebbe
// provenire da un composable che legge i token di design del tema.
const positiveColor = 'rgba(75, 192, 192, 0.5)';
const negativeColor = 'rgba(255, 99, 132, 0.5)';

const tradesStore = useTradesStore();

const chartData = computed(() => {
  const performanceData = tradesStore.performanceByDayOfWeek;

  // Garantisce un ordine coerente dei giorni, indipendentemente dai dati ricevuti.
  const dayLabels = ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato', 'Domenica'];

  const pnlValues = dayLabels.map(day => {
    // Cerca il giorno nei dati; se non c'è, il P&L è 0.
    const dayData = performanceData[day];
    return dayData ? dayData.total_pnl : 0;
  });

  return {
    labels: dayLabels,
    datasets: [
      {
        label: 'Net P&L',
        data: pnlValues,
        // Assegna dinamicamente il colore di ogni barra in base al P&L
        backgroundColor: pnlValues.map(pnl => (pnl >= 0 ? positiveColor : negativeColor)),
        borderColor: pnlValues.map(pnl => (pnl >= 0 ? 'rgba(75, 192, 192, 1)' : 'rgba(255, 99, 132, 1)')),
        borderWidth: 1,
      },
    ],
  };
});

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false, // La legenda non è necessaria, il colore della barra è sufficiente
    },
    title: {
      display: false, // Il titolo è ora gestito dal BaseWidget
    },
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: {
        // Formatta i tick dell'asse Y per mostrare il simbolo della valuta
        callback: function (value) {
          return '$' + value;
        },
      },
    },
  },
};
</script>

<template>
  <BaseWidget>
    <template #header>
      <h3 class="widget-title">Performance by Day</h3>
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
  height: 250px; /* Altezza specifica per il contenitore del grafico */
  position: relative;
}
</style>
