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
    <!-- Layout unificato: testo a sinistra, grafico a destra -->
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
/* Stili di base della card, ora con layout a 2 colonne di default */
.stat-card {
  background-color: var(--semantic-color-surface-primary);
  padding: var(--semantic-size-inset-md);
  border-radius: var(--semantic-border-radius-surface);
  border: var(--base-border-width-1) solid var(--semantic-color-border-default);
  box-shadow: var(--semantic-effect-shadow-elevation-low);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--semantic-size-stack-md);
  transition: box-shadow var(--base-animation-duration-fast) var(--base-animation-easing-out);
  overflow: hidden; /* Aggiunto per contenere meglio gli elementi */
}
.stat-card:hover {
    box-shadow: var(--semantic-effect-shadow-elevation-medium);
}

/* Stili per il testo */
.text-content {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-xs);
  white-space: nowrap;
}
.stat-label {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
}
.stat-value {
  font: var(--semantic-font-style-metric-display); /* Usa il font fluido */
  color: var(--semantic-color-text-primary);
}
.stat-value--positive {
  color: var(--semantic-color-feedback-positive-text);
}
.stat-value--negative {
  color: var(--semantic-color-feedback-negative-text);
}

/* Stili specifici per Win Rate Card */
.win-rate-label {
    display: flex;
    align-items: center;
    gap: var(--semantic-size-stack-sm);
}
.badges {
    display: flex;
    gap: var(--semantic-size-stack-xs);
}
.badge {
    font: var(--semantic-font-style-body-xs);
    padding: 0.1rem 0.4rem;
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
    width: 60px;
}

/* Media Query per schermi piccoli (es. telefoni) */
@media (max-width: 480px) { /* xs breakpoint */
    .stat-card {
        padding: var(--semantic-size-inset-sm);
        gap: var(--semantic-size-stack-sm);
    }
    .chart-content {
        width: 48px;
    }
}
</style>
