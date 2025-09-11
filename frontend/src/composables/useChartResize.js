// =============================================================================
// FILE: composables/useChartResize.js
// DESCRIZIONE: Composable di Vue per gestire il ridimensionamento di un'istanza
// di Chart.js utilizzando un ResizeObserver per rilevare cambiamenti di
// dimensione del suo contenitore.
// =============================================================================
import { watch } from 'vue';
import { useResizeObserver, useDebounceFn } from '@vueuse/core';

/**
 * Gestisce il ridimensionamento di un grafico Chart.js osservando il suo contenitore.
 * @param {import('vue').Ref<any>} chartRef - Il ref del componente vue-chartjs.
 */
export function useChartResize(chartRef) {
  // Creiamo una funzione di ridimensionamento "debounced" per evitare di chiamarla
  // troppe volte in rapida successione durante un'animazione, ottimizzando le performance.
  const debouncedResize = useDebounceFn(() => {
    if (chartRef.value?.chart) {
      chartRef.value.chart.resize();
    }
  }, 100);

  // Osserviamo il ref del grafico. Non appena il componente del grafico
  // viene montato e il ref è disponibile...
  watch(chartRef, (newChartRef) => {
    if (newChartRef) {
      // ...identifichiamo l'elemento contenitore del grafico.
      // `newChartRef.$el` è l'elemento <canvas> stesso. Vogliamo osservare
      // il suo genitore diretto, che è il <div> con classe "chart-container".
      const chartContainer = newChartRef.$el?.parentElement;
      if (chartContainer) {
        // ...e iniziamo a osservare quel contenitore. Ogni volta che la sua
        // dimensione cambia, la nostra funzione `debouncedResize` verrà chiamata.
        useResizeObserver(chartContainer, debouncedResize);
      }
    }
  });
}
