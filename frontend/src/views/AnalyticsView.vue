<!--
// =============================================================================
// FILE: views/AnalyticsView.vue
// DESCRIZIONE: Questa è la "vista" o "pagina" principale per la sezione di Analisi.
// Il suo compito è quello di assemblare i vari widget e componenti analitici
// in un layout coerente.
// =============================================================================
-->

<script setup>
import { onMounted } from 'vue';
import { useTradesStore } from '@/stores/trades';
import StrategyPerformance from '../components/analytics/StrategyPerformance.vue';
import WinLossDays from '../components/analytics/WinLossDays.vue';

const tradesStore = useTradesStore();

onMounted(() => {
  if (!tradesStore.processedStats) {
    tradesStore.fetchProcessedStats();
  }
});
</script>

<template>
  <div class="analytics-view">
    <!-- Aggiunto un titolo alla pagina per chiarezza -->
    <h1 class="view-title">Analytics</h1>
    <div class="widget-grid">
      <StrategyPerformance />
      <WinLossDays />
      <!-- Qui potremmo aggiungere altri widget in futuro -->
    </div>
  </div>
</template>

<style scoped>
/* Stili specifici per questa pagina. */
.analytics-view {
  width: 100%;
  padding: var(--semantic-size-inset-xl);
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-lg);
}

.widget-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: var(--semantic-size-stack-lg);
}
</style>
