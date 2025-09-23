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
  border-radius: var(--semantic-border-radius-surface);
  border: var(--semantic-border-width-default) solid var(--semantic-color-border-default);
  box-shadow: var(--semantic-effect-shadow-elevation-low);
  display: grid;
  grid-template-columns: 1fr auto;
  align-items: center;
  transition: box-shadow var(--semantic-animation-duration-interactive) var(--semantic-animation-easing-exit);
  overflow: hidden;
  height: 100%; /* Assicura che la card occupi tutta l'altezza della cella di griglia. */
}
.stat-card:hover {
  box-shadow: var(--semantic-effect-shadow-elevation-medium);
}

.text-content {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-xs);
  white-space: normal;
}

.stat-label {
  color: var(--semantic-color-text-secondary);
  white-space: nowrap; /* Impedisce al testo dell'etichetta di andare a capo. */
}

.stat-value {
  font: var(--semantic-font-style-metric-display);
  color: var(--semantic-color-text-primary);
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
  gap: var(--semantic-size-stack-sm);
}
.badges {
  display: flex;
  gap: var(--semantic-size-stack-xxs);
}
.badge {
  border-radius: var(--semantic-border-radius-tag);
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
  flex-shrink: 0;
}

/* === Stili Mobile-First === */

/* Default styles for the smallest screens (< 480px) */
.stat-card {
  gap: var(--semantic-size-stack-sm); /* Using sm as xxs was not defined */
  padding: var(--semantic-size-inset-xs);
}
.stat-label {
  font: var(--semantic-font-style-label-xxs);
}
.chart-content {
  width: var(--semantic-size-component-stat-card-chart-width-mobile);
}
.badge {
  font: var(--semantic-font-style-body-xxs);
  padding: 0.05rem 0.25rem;
}

/* From xs (480px) upwards */
@media (--breakpoint-xs) {
  .stat-card {
    padding: var(--semantic-size-inset-sm);
    gap: var(--semantic-size-stack-sm);
  }
  .stat-label {
    font: var(--semantic-font-style-label-xs);
  }
  .chart-content {
    width: var(--semantic-size-component-stat-card-chart-width-tablet);
  }
}

/* From sm (640px) upwards - Desktop styles */
@media (--breakpoint-sm) {
  .stat-card {
    padding: var(--semantic-size-inset-md);
    gap: var(--semantic-size-stack-md);
  }
  .stat-label {
    font: var(--semantic-font-style-body-sm);
  }
  .chart-content {
    width: var(--semantic-size-component-stat-card-chart-width-desktop);
  }
  .badge {
    font: var(--semantic-font-style-body-xs);
    padding: 0.1rem 0.4rem;
  }
}
</style>
