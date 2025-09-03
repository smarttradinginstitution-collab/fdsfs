<!--
// =============================================================================
// FILE: components/dashboard/RecentTradesTable.vue
// DESCRIZIONE: Questo componente visualizza una tabella di trade recenti.
// È stato rifattorizzato per leggere i dati direttamente dallo store Pinia,
// rendendolo reattivo ai cambiamenti dello stato centrale.
// =============================================================================
-->

<script setup>
// --- IMPORTAZIONI ---
import BaseTable from '../ui/BaseTable.vue';
// 1. Importiamo lo store dei trade.
import { useTradesStore } from '../../stores/trades';

// --- LOGICA DEL COMPONENTE ---
// 2. Creiamo un'istanza dello store.
const tradesStore = useTradesStore();

// 3. I dati finti locali (`recentTrades`) sono stati rimossi.
//    Useremo direttamente i getters dello store nel template.
//    Anche le intestazioni le prendiamo dallo store per coerenza.
const headers = tradesStore.tradeHeaders;
</script>

<template>
  <div class="recent-trades-card">
    <h2 class="card-title">Recent Trades</h2>
    <!--
    Ora `:items` è collegato al getter `recentTrades` dello store.
    Qualsiasi modifica alla lista dei trade nello store (es. un nuovo trade aggiunto)
    verrà automaticamente riflessa qui.
    -->
    <BaseTable :headers="headers" :items="tradesStore.recentTrades">
      <!-- La personalizzazione dello slot per il P&L rimane invariata. -->
      <template #pnl="{ item }">
        <span :class="item.pnl >= 0 ? 'pnl-positive' : 'pnl-negative'">
          {{ item.pnl >= 0 ? '+' : '' }}${{ Math.abs(item.pnl).toFixed(2) }}
        </span>
      </template>
    </BaseTable>
  </div>
</template>

<style scoped>
/*
// =============================================================================
// STYLING: components/dashboard/RecentTradesTable.vue
// DESCRIZIONE: Aggiunta di stili iper-responsive al contenitore della tabella.
// =============================================================================
*/
.recent-trades-card {
  display: flex;
  flex-direction: column;
  /* Spaziatura e padding fluidi */
  gap: clamp(var(--semantic-size-stack-sm), 3vw, var(--semantic-size-stack-md));
  background-color: var(--semantic-color-surface-primary);
  border: var(--base-border-width-1) solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-surface);
  box-shadow: var(--semantic-effect-shadow-elevation-low);
  padding: clamp(var(--semantic-size-inset-md), 4vw, var(--semantic-size-inset-lg));
  overflow-x: auto; /* Aggiunge scroll orizzontale se necessario su schermi medi */
}
.card-title {
  /* Titolo fluido */
  font-family: var(--base-font-family-palette-sans);
  font-weight: var(--base-font-weight-bold);
  font-size: clamp(var(--base-font-size-lg), 4vw, var(--base-font-size-xl));
  color: var(--semantic-color-text-primary);
}

.pnl-positive {
  color: var(--semantic-color-feedback-positive-text);
  font-family: var(--semantic-font-style-data-numeric-font-family);
}
.pnl-negative {
  color: var(--semantic-color-feedback-negative-text);
  font-family: var(--semantic-font-style-data-numeric-font-family);
}

/* Nasconde lo scroll orizzontale quando la tabella diventa a card */
@media (max-width: 768px) {
  .recent-trades-card {
    overflow-x: hidden;
  }
}
</style>
