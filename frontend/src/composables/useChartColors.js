// src/composables/useChartColors.js
import { onMounted, ref, computed } from 'vue';

/**
 * Un composable riutilizzabile per recuperare i colori semantici dal foglio di stile principale.
 * Fornisce un oggetto reattivo con i colori necessari per i grafici.
 */
export function useChartColors() {
  const isReady = ref(false);

  // Definiamo una struttura dati più organizzata per i colori, con fallback.
  const colors = ref({
    radar: {
      backgroundColor: 'rgba(37, 99, 235, 0.2)',
      borderColor: '#2563eb',
      gridColor: '#d8d8d9',
      pointLabelColor: '#5d5d61',
      tickColor: '#909093',
    },
    feedback: {
        positive: '#16a34a',
        negative: '#dc2626',
    }
  });

  onMounted(() => {
    try {
      const style = getComputedStyle(document.documentElement);

      const fetchedColors = {
        interactivePrimaryRgb: style.getPropertyValue('--semantic-color-interactive-primary-rgb').trim(),
        interactivePrimaryDefault: style.getPropertyValue('--semantic-color-interactive-primary-default').trim(),
        borderSubtle: style.getPropertyValue('--semantic-color-border-subtle').trim(),
        textSecondary: style.getPropertyValue('--semantic-color-text-secondary').trim(),
        textTertiary: style.getPropertyValue('--semantic-color-text-tertiary').trim(),
        feedbackPositive: style.getPropertyValue('--semantic-color-feedback-positive-text').trim(),
        feedbackNegative: style.getPropertyValue('--semantic-color-feedback-negative-text').trim(),
      };

      // Se il recupero ha successo, aggiorniamo i valori.
      if (fetchedColors.interactivePrimaryDefault) {
        colors.value = {
          radar: {
            backgroundColor: `rgba(${fetchedColors.interactivePrimaryRgb}, 0.2)`,
            borderColor: fetchedColors.interactivePrimaryDefault,
            gridColor: fetchedColors.borderSubtle,
            pointLabelColor: fetchedColors.textSecondary,
            tickColor: fetchedColors.textTertiary,
          },
          feedback: {
            positive: fetchedColors.feedbackPositive,
            negative: fetchedColors.feedbackNegative,
          }
        };
      }
    } catch (error) {
      console.error('Failed to fetch chart colors from CSS variables:', error);
      // I colori di fallback verranno usati in caso di errore.
    } finally {
      isReady.value = true;
    }
  });

  // Restituiamo un computed ref per accedere direttamente ai colori del radar
  // Questo semplifica l'utilizzo nel componente.
  const radarColors = computed(() => colors.value.radar);

  return {
    radarColors,
    isReady,
  };
}
