<script setup>
import { computed } from 'vue';
import GaugeChart from './GaugeChart.vue';
import WinLossDonutChart from './WinLossDonutChart.vue';
import HeaderInfoOverlay from '../../../ui/HeaderInfoOverlay.vue';
import { useMetricInfo } from '../../../../composables/useMetricInfo.js';

// --- PROPS ---
const props = defineProps({
  stat: { type: Object, required: true },
});

const { info } = useMetricInfo(props.stat.key);

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
      <HeaderInfoOverlay :aria-label="`Learn more about ${info.title}`" class="header-overlay">
        <template #title>
          <div v-if="isWinRate" class="win-rate-label">
            <span class="stat-label">Win %</span>
            <div class="badges">
              <span class="badge win">{{ stat.wins }}</span>
              <span class="badge loss">{{ stat.losses }}</span>
            </div>
          </div>
          <p v-else class="stat-label">{{ stat.label }}</p>
        </template>
        <template #content>
          <h4 class="info-overlay-title">{{ info.title }}</h4>
          <p class="info-overlay-text">{{ info.description }}</p>
        </template>
      </HeaderInfoOverlay>

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
  grid-template-columns: 1fr auto;
  align-items: center;
  gap: var(--semantic-size-stack-fluid-stat-card-gap);

  transition: box-shadow var(--semantic-animation-duration-interactive) var(--semantic-animation-easing-exit);
}
.stat-card:hover {
    box-shadow: var(--semantic-effect-shadow-elevation-medium);
}

.text-content {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-xs);
}
.stat-label {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
  white-space: nowrap; /* Impedisce al testo di andare a capo */
}

/*
  BEST PRACTICE: Overriding Nested Component Styles
  Usiamo :deep() per raggiungere e modificare gli stili di un componente figlio
  (HeaderInfoOverlay) dall'interno di un componente padre. Questo ci permette
  di adattare il suo layout senza modificare il componente originale, mantenendo
  la modularità.
*/
.header-overlay :deep(.title-container) {
  /* Allinea l'icona info verticalmente con il testo dell'etichetta. */
  align-items: center;
  /* Sovrascrive lo space-between per avvicinare l'icona al testo */
  justify-content: flex-start;
  gap: var(--semantic-size-stack-xxs); /* Riduci lo spazio tra testo e icona */
}
.header-overlay :deep(.info-button) {
    margin-bottom: 0; /* Rimuove il margine se presente */
}

/*
  BEST PRACTICE: Responsive Overlay
  Per risolvere il problema dell'overflow, l'overlay viene posizionato in modo
  assoluto rispetto alla card. Usiamo le media query per adattarne le dimensioni:
  - Su schermi grandi, ha una larghezza fissa per una leggibilità ottimale.
  - Su schermi piccoli, si adatta alla larghezza della card per evitare di
    uscire dai bordi dello schermo.
*/
.header-overlay :deep(.info-overlay) {
  /* Impostazioni di base per tutte le dimensioni */
  left: 0;
  right: auto;
  width: auto; /* L'overlay si adatta al contenuto */
  min-width: 280px; /* Larghezza minima per leggibilità su desktop */
  max-width: 320px;
}

@include media-down('sm') {
  .header-overlay :deep(.info-overlay) {
    /* Su mobile, l'overlay occupa la larghezza della card meno un po' di padding */
    left: 50%;
    transform: translateX(-50%);
    width: calc(100% - var(--semantic-size-inset-md) * 2);
    min-width: unset; /* Rimuoviamo la larghezza minima */
  }
}

/*
  Stili per il contenuto dell'overlay, per garantire che sia leggibile e ben
  formattato quando appare.
*/
.info-overlay-title {
  font: var(--semantic-font-style-label-md);
  color: var(--semantic-color-text-primary);
}

.info-overlay-text {
  font: var(--semantic-font-style-body-sm);
  color: var(--semantic-color-text-secondary);
  line-height: var(--base-font-line-height-tight);
}
/*
  BEST PRACTICE: Tipografia Fluida
  Usiamo un token (`metric-display`) che applica la funzione CSS `clamp()`.
  Questo permette al font di scalare fluidamente con la larghezza dello schermo,
  diventando più piccolo su mobile senza bisogno di molteplici media query.
*/
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
    font: var(--semantic-font-style-body-xxs);
    padding: var(--semantic-size-badge-padding-y) var(--semantic-size-badge-padding-x);
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
    /* BEST PRACTICE: Tokenizzazione delle dimensioni dei componenti
       La larghezza del grafico è gestita da token semantici, rendendo
       facile modificarla in futuro senza toccare il CSS. */
    width: var(--semantic-size-component-stat-card-chart-width);
}
</style>
