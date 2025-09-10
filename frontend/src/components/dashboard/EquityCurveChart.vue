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
import { useChartColors } from '../../composables/useChartColors';

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

// Recuperiamo i colori risolti dal DOM
const { colors, isReady } = useChartColors();

/**
 * Converte un colore HEX in formato RGBA.
 * @param {string} hex - Il colore in formato esadecimale (es. #RRGGBB).
 * @param {number} alpha - Il valore del canale alpha (0-1).
 * @returns {string} Il colore in formato rgba().
 */
const hexToRgba = (hex, alpha = 1) => {
  const bigint = parseInt(hex.slice(1), 16);
  const r = (bigint >> 16) & 255;
  const g = (bigint >> 8) & 255;
  const b = bigint & 255;
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
};

// Usiamo una computed property per formattare i dati per Chart.js
const dataForChart = computed(() => {
  // Rimuoviamo l'orario dalle etichette dell'asse X per una visualizzazione più pulita
  const formattedLabels = props.chartData.labels.map(label => label.split(' ')[0]);

  return {
    labels: formattedLabels,
    datasets: [
      {
        label: 'Cumulative P&L',
        backgroundColor: hexToRgba(colors.value.positive, 0.1), // Usiamo il colore risolto con opacità
        borderColor: colors.value.positive, // Usiamo il colore risolto
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
        color: hexToRgba(colors.value.textTertiary, 0.2),
      },
      ticks: {
        color: colors.value.textTertiary,
      },
    },
    y: {
      grid: {
        color: hexToRgba(colors.value.textTertiary, 0.2),
      },
      ticks: {
        color: colors.value.textTertiary,
        callback: function(value) {
          // Formattatore per abbreviare i numeri grandi
          if (Math.abs(value) >= 1e6) {
            return '$' + (value / 1e6).toFixed(1) + 'M';
          }
          if (Math.abs(value) >= 1e3) {
            return '$' + (value / 1e3).toFixed(1) + 'k';
          }
          return '$' + value;
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
    <Line v-if="hasData && isReady" :data="dataForChart" :options="chartOptions" />
    <div v-else class="chart-placeholder">
      <!-- Potremmo mostrare uno spinner qui se i dati ci sono ma i colori non sono pronti -->
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
