// src/composables/useChartColors.js
import { onMounted, ref, computed } from 'vue';

/**
 * Un composable riutilizzabile per recuperare i colori semantici dal foglio di stile principale.
 * Fornisce oggetti reattivi per i colori dei grafici, mantenendo la compatibilità con i componenti esistenti.
 */
export function useChartColors() {
  const isReady = ref(false);

  // Struttura dati flat per i colori, con fallback, per la compatibilità.
  const allColors = ref({
    // Feedback
    positive: '#16a34a',
    positiveRgb: '22, 163, 74',
    negative: '#dc2626',
    // Neutri e di testo
    neutral: '#3b82f6',
    textTertiary: '#909093',
    textSecondary: '#5d5d61',
    // Superfici e bordi
    surfaceSecondary: '#E5E7EB',
    borderSubtle: '#d8d8d9',
    // Colori specifici per Radar
    interactivePrimaryRgb: '37, 99, 235',
    interactivePrimaryDefault: '#2563eb',
  });

  onMounted(() => {
    try {
      const style = getComputedStyle(document.documentElement);

      const fetchedColors = {
        positive: style.getPropertyValue('--semantic-color-feedback-positive-text').trim(),
        positiveRgb: style.getPropertyValue('--semantic-color-feedback-positive-background-rgb').trim(),
        negative: style.getPropertyValue('--semantic-color-feedback-negative-text').trim(),
        neutral: style.getPropertyValue('--semantic-color-text-interactive').trim(),
        textTertiary: style.getPropertyValue('--semantic-color-text-tertiary').trim(),
        textSecondary: style.getPropertyValue('--semantic-color-text-secondary').trim(),
        surfaceSecondary: style.getPropertyValue('--semantic-color-surface-secondary').trim(),
        borderSubtle: style.getPropertyValue('--semantic-color-border-subtle').trim(),
        interactivePrimaryRgb: style.getPropertyValue('--semantic-color-interactive-primary-rgb').trim(),
        interactivePrimaryDefault: style.getPropertyValue('--semantic-color-interactive-primary-default').trim(),
      };

      if (fetchedColors.neutral) {
        allColors.value = fetchedColors;
      }
    } catch (error) {
      console.error('Failed to fetch chart colors from CSS variables:', error);
    } finally {
      isReady.value = true;
    }
  });

  // --- Exports per compatibilità ---
  const colors = computed(() => ({
    positive: allColors.value.positive,
    negative: allColors.value.negative,
    neutral: allColors.value.neutral,
    textTertiary: allColors.value.textTertiary,
    surfaceSecondary: allColors.value.surfaceSecondary,
  }));

  // --- Exports strutturati per i nuovi componenti ---
  const radarColors = computed(() => ({
    backgroundColor: `rgba(${allColors.value.interactivePrimaryRgb}, 0.2)`,
    borderColor: allColors.value.interactivePrimaryDefault,
    gridColor: allColors.value.borderSubtle,
    pointLabelColor: allColors.value.textSecondary,
    tickColor: allColors.value.textTertiary,
  }));

  const feedbackColors = computed(() => ({
    positive: allColors.value.positive,
    positiveRgb: allColors.value.positiveRgb,
    negative: allColors.value.negative,
  }));

  const gridColors = computed(() => ({
    line: allColors.value.borderSubtle,
    ticks: allColors.value.textTertiary,
  }));

  return {
    isReady,
    colors, // Per compatibilità all'indietro
    radarColors,
    feedbackColors,
    gridColors,
  };
}
