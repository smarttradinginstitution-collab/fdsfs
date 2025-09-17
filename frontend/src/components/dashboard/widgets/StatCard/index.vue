<script setup>
import { computed } from 'vue';
import GaugeChart from './GaugeChart.vue';
import WinLossDonutChart from './WinLossDonutChart.vue';

// --- PROPS ---
const props = defineProps({
  stat: { type: Object, required: true },
});

// --- COMPUTED PROPERTIES ---
const valueClasses = computed(() => ({
  'stat-value': true,
  'stat-value--positive': props.stat.changeType === 'positive',
  'stat-value--negative': props.stat.changeType === 'negative',
}));

const numericValue = computed(() => {
    const cleanedValue = String(props.stat.value).replace(/[^\d.-]/g, '');
    return parseFloat(cleanedValue) || 0;
});

const isProfitFactor = computed(() => props.stat.key === 'profitFactor');
const isWinRate = computed(() => props.stat.key === 'winRate');

</script>

<template>
  <div class="stat-card">
    <!--
      Layout unificato basato su Grid.
      Questo semplifica la logica del template: non abbiamo più bisogno di `v-if`
      multipli per cambiare la struttura. Tutte le card condividono lo stesso layout,
      e il contenitore del grafico rimane semplicemente vuoto se non necessario.
    -->
    <div class="text-content">
      <!-- Gestione speciale per Win Rate con i badge -->
      <div v-if="isWinRate" class="win-rate-label">
        <span class="stat-label">Win %</span>
        <div class="badges">
          <span class="badge win">{{ stat.wins }}</span>
          <span class="badge loss">{{ stat.losses }}</span>
        </div>
      </div>
      <!-- Etichetta standard per tutte le altre card -->
      <p v-else class="stat-label">{{ stat.label }}</p>

      <!-- Valore della statistica -->
      <p :class="valueClasses">{{ stat.value }}</p>
    </div>

    <!-- Contenitore del grafico (vuoto se non c'è un grafico) -->
    <div class="chart-content">
      <WinLossDonutChart v-if="isWinRate" :wins="stat.wins" :losses="stat.losses" :breakevens="stat.breakevens" />
      <GaugeChart v-if="isProfitFactor" :value="numericValue" />
    </div>
  </div>
</template>

<style scoped>
/*
  BEST PRACTICE: Layout con CSS Grid
  Usiamo `display: grid` per il layout interno della card. È più robusto di Flexbox
  per questo tipo di layout a colonne. `grid-template-columns: 1fr auto;` dice alla
  griglia di dare tutto lo spazio disponibile alla prima colonna (testo) e solo
  lo spazio necessario alla seconda (grafico).
*/
.stat-card {
  background-color: var(--semantic-color-surface-primary);
  padding: var(--semantic-size-inset-md);
  border-radius: var(--semantic-border-radius-surface);
  border: var(--semantic-border-width-default) solid var(--semantic-color-border-default);
  box-shadow: var(--semantic-effect-shadow-elevation-low);
  display: grid;
  /* Make both columns flexible and allow them to shrink to zero */
  grid-template-columns: minmax(0, 2fr) minmax(0, 1fr);
  align-items: center;
  gap: var(--semantic-size-stack-md);
  transition: box-shadow var(--semantic-animation-duration-interactive) var(--semantic-animation-easing-exit);
  overflow: hidden;
}
.stat-card:hover {
    box-shadow: var(--semantic-effect-shadow-elevation-medium);
}

.text-content {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-xs);
  /* Allow text to wrap if needed */
  white-space: normal;
  /* Ensure the container can shrink */
  min-width: 0;
}
.stat-label {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
}

.stat-value {
  font: var(--semantic-font-style-metric-display);
  color: var(--semantic-color-text-primary);
  /* Allow the value to break if it's a very long word/number */
  word-break: break-all;
}
.stat-value--positive {
  color: var(--semantic-color-feedback-positive-text);
}
.stat-value--negative {
  color: var(--semantic-color-feedback-negative-text);
}

.win-rate-label {
    display: flex;
    align-items: center;
    flex-wrap: wrap; /* Allow badges to wrap if needed */
    gap: var(--semantic-size-stack-sm);
}
.badges {
    display: flex;
    gap: var(--semantic-size-stack-xxs);
}
.badge {
    font: var(--semantic-font-style-body-xs);
    padding: 0.1rem 0.4rem;
    border-radius: var(--semantic-border-radius-tag);
    flex-shrink: 0; /* Prevent badges from being squished */
}
.badge.win {
    background-color: var(--semantic-color-feedback-positive-surface);
    color: var(--semantic-color-feedback-positive-text);
}
.badge.loss {
    background-color: var(--semantic-color-feedback-negative-surface);
    color: var(--semantic-color-feedback-negative-text);
}

.chart-content {
    display: flex;
    align-items: center;
    justify-content: center;
    /* Let the grid column define the size */
    width: 100%;
    max-width: 60px; /* Set a max size to prevent it from becoming huge */
    margin: 0 auto; /* Center the chart content within its column */
}

/* --- Responsive adjustments --- */
@media (max-width: 480px) {
    .stat-card {
        padding: var(--semantic-size-inset-sm);
        gap: var(--semantic-size-stack-sm);
    }
}
</style>
