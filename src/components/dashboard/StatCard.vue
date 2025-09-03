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
  <div class="stat-card" :class="{ 'stat-card--with-chart': isProfitFactor || isWinRate }">

    <!-- Layout per Win Rate -->
    <template v-if="isWinRate">
        <div class="text-content">
            <div class="win-rate-label">
                <span class="stat-label">Win %</span>
                <div class="badges">
                    <span class="badge win">{{ stat.wins }}</span>
                    <span class="badge loss">{{ stat.losses }}</span>
                </div>
            </div>
            <p :class="valueClasses">{{ stat.value }}</p>
        </div>
        <div class="chart-content">
            <WinLossDonutChart :wins="stat.wins" :losses="stat.losses" :breakevens="stat.breakevens" />
        </div>
    </template>

    <!-- Layout per Profit Factor -->
    <template v-else-if="isProfitFactor">
        <div class="text-content">
            <p class="stat-label">{{ stat.label }}</p>
            <p :class="valueClasses">{{ stat.value }}</p>
        </div>
        <div class="chart-content">
            <GaugeChart :value="numericValue" />
        </div>
    </template>

    <!-- Layout di default per tutte le altre card -->
    <div v-else class="text-content-default">
      <p class="stat-label">{{ stat.label }}</p>
      <p :class="valueClasses">{{ stat.value }}</p>
    </div>
  </div>
</template>

<style scoped>
/*
// =============================================================================
// STYLING: components/dashboard/StatCard.vue
// DESCRIZIONE: Aggiunta di stili iper-responsive per le card delle statistiche.
//
// NOTE:
// - Tipografia e spaziature rese fluide con clamp().
// - Dimensione del grafico resa fluida per adattarsi meglio.
// - Migliorata la gestione del layout su schermi piccoli.
// =============================================================================
*/

/* Stili di base della card */
.stat-card {
  background-color: var(--semantic-color-surface-primary);
  /* Padding fluido */
  padding: clamp(var(--base-size-spacing-3), 3vw, var(--semantic-size-inset-md));
  border-radius: var(--semantic-border-radius-surface);
  border: var(--base-border-width-1) solid var(--semantic-color-border-default);
  box-shadow: var(--semantic-effect-shadow-elevation-low);
  display: flex;
  transition: box-shadow var(--base-animation-duration-fast) var(--base-animation-easing-out);
}
.stat-card:hover {
    box-shadow: var(--semantic-effect-shadow-elevation-medium);
}

/* Layout di default (verticale) */
.text-content-default {
    display: flex;
    flex-direction: column;
    gap: clamp(var(--base-size-spacing-0-5), 1vw, var(--semantic-size-stack-xs));
}

/* Layout per card con grafici (2 colonne) */
.stat-card--with-chart {
    justify-content: space-between;
    align-items: center;
    gap: clamp(var(--base-size-spacing-2), 2vw, var(--semantic-size-stack-md));
}

/* Stili per il testo */
.text-content {
  display: flex;
  flex-direction: column;
  gap: clamp(var(--base-size-spacing-0-5), 1vw, var(--semantic-size-stack-xs));
}
.stat-label {
  /* Font fluido per l'etichetta */
  font-size: clamp(var(--base-font-size-xs), 2.5vw, var(--base-font-size-sm));
  font-family: var(--base-font-family-palette-sans);
  font-weight: var(--base-font-weight-medium);
  color: var(--semantic-color-text-secondary);
  white-space: nowrap;
}
.stat-value {
  /* Font fluido per il valore principale */
  font-size: clamp(var(--base-font-size-lg), 5vw, var(--base-font-size-2xl));
  font-family: var(--base-font-family-palette-sans);
  font-weight: var(--base-font-weight-bold);
  color: var(--semantic-color-text-primary);
  line-height: var(--base-font-line-height-tight);
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
    /* Font e padding fluidi per i badge */
    font-size: clamp(0.6rem, 1.8vw, 0.75rem);
    padding: clamp(0.05rem, 0.5vw, 0.1rem) clamp(0.2rem, 1vw, 0.4rem);
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
    /* Larghezza fluida per il contenitore del grafico */
    width: clamp(45px, 12vw, 60px);
}

/* Responsive Stacking per le card con grafici */
@media (max-width: 480px) {
    .stat-card--with-chart {
        flex-direction: column;
        align-items: flex-start;
        gap: var(--semantic-size-stack-sm); /* Leggermente ridotto per schermi piccoli */
    }

    .text-content {
        width: 100%; /* Assicura che il testo occupi tutta la larghezza */
    }
}

/* Breakpoint aggiuntivo per card con grafici su schermi molto stretti */
@media (max-width: 280px) {
    .stat-card--with-chart {
        /* Su schermi piccolissimi, il grafico potrebbe sovrapporsi.
           Qui potremmo nasconderlo o ridurlo ulteriormente se necessario.
           Per ora, lo manteniamo ma con spaziature ridotte. */
        gap: var(--semantic-size-stack-xs);
    }

    .stat-value {
        /* Riduciamo un po' la dimensione massima del font del valore principale */
        font-size: clamp(var(--base-font-size-lg), 8vw, var(--base-font-size-xl));
    }
}
</style>
