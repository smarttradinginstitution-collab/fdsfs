<!--
// =============================================================================
// FILE: components/dashboard/RecentTradesTable.vue
// DESCRIZIONE: Questo componente visualizza una tabella degli ultimi trade
// basandosi sui filtri attualmente attivi nella dashboard.
// =============================================================================
-->
<script setup>
import { computed } from 'vue';
import BaseTable from '../ui/BaseTable.vue';
import { useTradesStore } from '../../stores/trades';

const tradesStore = useTradesStore();

// Le intestazioni sono ora definite direttamente qui per maggiore chiarezza,
// ma potrebbero anche venire dallo store se fossero usate in più posti.
const headers = [
  { key: 'ticker', text: 'Ticker' },
  { key: 'type', text: 'Side' },
  { key: 'pnl', text: 'Net P&L' },
  { key: 'date', text: 'Date' },
];

// Proprietà calcolata per ottenere solo i trade più recenti.
// La lista dei trade nello store è già filtrata dal backend.
const recentTrades = computed(() => {
  // .slice(0, 7) prende al massimo i primi 7 trade.
  return tradesStore.trades.slice(0, 7);
});
</script>

<template>
  <div class="recent-trades-widget">
    <div class="widget-header">
      <h2 class="widget-title">Recent Trades</h2>
      <span class="widget-subtitle">Last 7 filtered trades</span>
    </div>
    <div class="table-container">
      <BaseTable :headers="headers" :items="recentTrades">
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
  border: var(--base-border-width-1) solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-surface);
  box-shadow: var(--semantic-effect-shadow-elevation-low);
  overflow: hidden; /* Nasconde il contenuto che esce dai bordi arrotondati */
}

.widget-header {
  padding: var(--semantic-size-inset-lg);
  border-bottom: var(--base-border-width-1) solid var(--semantic-color-border-default);
  background-color: var(--semantic-color-surface-subtle); /* Sfondo leggero per l'header */
}

.widget-title {
  font-family: var(--semantic-font-style-heading-xl-font-family);
  font-size: var(--semantic-font-style-heading-xl-font-size);
  font-weight: var(--semantic-font-style-heading-xl-font-weight);
  color: var(--semantic-color-text-primary);
  margin: 0;
}

.widget-subtitle {
  font-family: var(--semantic-font-style-body-sm-font-family);
  font-size: var(--semantic-font-style-body-sm-font-size);
  color: var(--semantic-color-text-subtle);
}

.table-container {
  padding: var(--semantic-size-inset-lg);
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
