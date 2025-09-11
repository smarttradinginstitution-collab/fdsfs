// =============================================================================
// FILE: composables/useChartResize.js
// DESCRIZIONE: Composable di Vue per gestire il ridimensionamento di un'istanza
// di Chart.js in risposta al collasso della sidebar.
// =============================================================================
import { watch } from 'vue';
import { useUiStore } from '../stores/uiStore';
import { useDebounceFn } from '@vueuse/core';

/**
 * Gestisce il ridimensionamento di un grafico Chart.js quando la sidebar cambia stato.
 * @param {import('vue').Ref<any>} chartRef - Il ref del componente vue-chartjs.
 */
export function useChartResize(chartRef) {
  const uiStore = useUiStore();

  // La transizione CSS della sidebar dura 300ms. Aspettiamo un po' di più
  // per essere sicuri che l'animazione sia finita prima di ridisegnare il grafico.
  // Usiamo useDebounceFn per evitare chiamate multiple e garantire performance.
  const debouncedResize = useDebounceFn(() => {
    if (chartRef.value?.chart) {
      chartRef.value.chart.resize();
    }
  }, 350); // 300ms (transizione) + 50ms (margine)

  // Osserviamo lo stato di collasso della sidebar.
  watch(() => uiStore.isSidebarCollapsed, () => {
    debouncedResize();
  });
}
