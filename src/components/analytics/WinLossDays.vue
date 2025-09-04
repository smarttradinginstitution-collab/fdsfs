<!--
// =============================================================================
// FILE: components/analytics/WinLossDays.vue
// DESCRIZIONE: Un componente-widget che visualizza il conteggio dei giorni
// di trading positivi, negativi e in pareggio.
// =============================================================================
-->

<script setup>
import { computed } from 'vue';
import { useTradesStore } from '../../stores/trades';

const tradesStore = useTradesStore();

// Usiamo una computed property per accedere ai dati in modo reattivo.
const stats = computed(() => tradesStore.winLossDays);

const totalDays = computed(() => {
  return stats.value.winningDays + stats.value.losingDays + stats.value.breakEvenDays;
});
</script>

<template>
  <div class="breakdown-card">
    <h3 class="card-title">Win / Loss Days</h3>
    <div v-if="totalDays > 0" class="stats-container">
      <div class="stat-item">
        <span class="stat-value positive">{{ stats.winningDays }}</span>
        <span class="stat-label">Winning Days</span>
      </div>
      <div class="stat-item">
        <span class="stat-value negative">{{ stats.losingDays }}</span>
        <span class="stat-label">Losing Days</span>
      </div>
      <div class="stat-item">
        <span class="stat-value neutral">{{ stats.breakEvenDays }}</span>
        <span class="stat-label">Break-Even Days</span>
      </div>
    </div>
    <div v-else class="no-data-placeholder">
      <p>No trading days in the selected period.</p>
    </div>
  </div>
</template>

<style scoped>
/* Riusiamo lo stile di BreakdownCard per coerenza */
.breakdown-card {
  background-color: var(--color-surface-primary);
  border: 1px solid var(--color-border-default);
  border-radius: var(--border-radius-surface);
  padding: var(--size-inset-lg);
  display: flex;
  flex-direction: column;
  gap: var(--size-stack-md);
}

.card-title {
  font: var(--typography-style-heading-md);
  color: var(--color-text-primary);
}

.stats-container {
  display: flex;
  justify-content: space-around;
  text-align: center;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: var(--size-stack-xs);
}

.stat-value {
  font: var(--typography-style-heading-xl);
  font-weight: var(--base-font-weight-bold);
}

.stat-label {
  font: var(--typography-style-body-sm);
  color: var(--color-text-secondary);
}

.positive {
  color: var(--color-text-positive);
}

.negative {
  color: var(--color-text-negative);
}

.neutral {
  color: var(--color-text-secondary);
}

.no-data-placeholder {
  text-align: center;
  color: var(--color-text-tertiary);
  padding: var(--size-inset-xl);
  font: var(--typography-style-body-md);
}
</style>
