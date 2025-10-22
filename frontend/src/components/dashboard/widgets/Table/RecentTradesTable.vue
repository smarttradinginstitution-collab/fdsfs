<!--
// =============================================================================
// FILE: components/dashboard/RecentTradesTable.vue
// DESCRIZIONE: Questo componente visualizza una tabella degli ultimi trade
// basandosi sui filtri attualmente attivi nella dashboard.
// =============================================================================
-->
<script setup>
import { computed } from 'vue';
import { useMediaQuery } from '@vueuse/core';
import BaseTable from '../../../ui/BaseTable.vue';
import { useTradesStore } from '../../../../stores/trades';

const tradesStore = useTradesStore();

const headers = [
  { key: 'symbol_snapshot', text: 'Symbol' },
  { key: 'type', text: 'Side' },
  { key: 'pnl', text: 'Net P&L' },
  { key: 'date', text: 'Date' },
];

const recentTrades = computed(() => {
  return tradesStore.trades.slice(0, 7);
});

const isSmallScreen = useMediaQuery('(max-width: 768px)');
const tableSize = computed(() => (isSmallScreen.value ? 'small' : 'medium'));
</script>

<template>
  <div class="recent-trades-widget">
    <div class="widget-header">
      <h2 class="widget-title">Recent Trades</h2>
    </div>
    <div class="table-container">
      <BaseTable :headers="headers" :items="recentTrades" :size="tableSize">
        <!-- Slot per formattare la colonna P&L -->
        <template #pnl="{ item }">
          <span :class="item.pnl >= 0 ? 'pnl-positive' : 'pnl-negative'">
            {{ item.pnl >= 0 ? '+' : '' }}${{ Math.abs(item.pnl).toFixed(2) }}
          </span>
        </template>
        <!-- Slot per formattare la data -->
        <template #date="{ item }">
          {{ new Date(item.date).toLocaleDateString() }}
        </template>
      </BaseTable>
      <div v-if="recentTrades.length === 0" class="no-trades-message">
        <p>No recent trades match the current filters.</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.recent-trades-widget {
  display: flex;
  flex-direction: column;
  background-color: var(--semantic-color-surface-primary);
  border: var(--base-border-width-1);
  border-radius: var(--semantic-border-radius-surface);
  box-shadow: var(--semantic-effect-shadow-elevation-low);
  overflow: hidden; /* Nasconde il contenuto che esce dai bordi arrotondati */
}

.widget-header {
  /* Padding: block (vertical) inline (horizontal) */
  padding: var(--semantic-size-inset-md) var(--semantic-size-inset-lg);
  border-bottom: var(--base-border-width-1) solid var(--semantic-color-border-default);
  background-color: var(--semantic-color-surface-subtle); /* Sfondo leggero per l'header */
  display: flex;
  align-items: center;
  /* Impostiamo un'altezza minima per allinearci con l'header del calendario,
     che ha un'altezza guidata dal suo contenuto (es. pulsanti e titolo) */
  min-height: 68px; /* Valore basato sull'altezza tipica dell'header del calendario. Potrebbe richiedere un token. */
}

.widget-title {
  font-family: var(--semantic-font-style-heading-xl-font-family);
  font-size: var(--semantic-font-style-heading-xl-font-size);
  font-weight: var(--semantic-font-style-heading-xl-font-weight);
  color: var(--semantic-color-text-primary);
  margin: 0;
}

.table-container {
  /* top | horizontal | bottom */
  padding: 0 var(--semantic-size-inset-lg) var(--semantic-size-inset-xl);
}

.pnl-positive {
  color: var(--semantic-color-feedback-positive-text);
  font-family: var(--semantic-font-style-data-numeric-font-family);
}

.pnl-negative {
  color: var(--semantic-color-feedback-negative-text);
  font-family: var(--semantic-font-style-data-numeric-font-family);
}

.no-trades-message {
  text-align: center;
  padding: var(--semantic-size-inset-xl);
  font-family: var(--semantic-font-style-body-md-font-family);
  color: var(--semantic-color-text-subtle);
}
</style>
