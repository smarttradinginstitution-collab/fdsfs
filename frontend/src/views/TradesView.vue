<!--
// =============================================================================
// FILE: views/TradesView.vue
// DESCRIZIONE: Questo componente rappresenta la "vista" della pagina "My Trades".
// Il suo unico scopo è mostrare una tabella con la lista completa di tutti
// i trade registrati dall'utente.
// =============================================================================
-->

<script setup>
// --- IMPORTAZIONI ---
import { useRouter } from 'vue-router';
import { useTradesStore } from '@/stores/trades';
import BaseTable from '@/components/ui/BaseTable.vue';


// --- LOGICA DEL COMPONENTE ---
const router = useRouter();
const tradesStore = useTradesStore();

const handleRowClick = (trade) => {
  router.push({ name: 'TradeDetail', params: { id: trade.id } });
};
</script>

<template>
  <!-- Il template definisce la struttura HTML della pagina. -->
  <div class="trades-view">
    <!-- Un semplice titolo per la pagina. -->
    <h1 class="view-title">My Trades</h1>

    <!--
    Qui usiamo il nostro componente `BaseTable`.
    - `:headers` riceve la lista delle intestazioni dal getter dello store.
    - `:items` riceve la lista dei trade direttamente dallo stato dello store.
    - `@row-click` gestisce la navigazione al dettaglio del trade.
    -->
    <BaseTable
      :headers="tradesStore.tradeHeaders"
      :items="tradesStore.trades"
      @row-click="handleRowClick"
    />
  </div>
</template>

<style scoped>
/*
Gli stili "scoped" si applicano solo a questo componente.
In questo caso, sono stati rimossi perché la dashboard-view non esiste in questo file.
Se fossero necessari stili specifici, andrebbero qui. Esempio:
.trades-view {
  padding: var(--semantic-size-inset-xl);
}
*/
.trades-view {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-lg);
  padding: var(--semantic-size-inset-xl); /* Aggiunto padding per coerenza */
  flex-grow: 1; /* Aggiunto per occupare lo spazio disponibile */
}
.view-title {
  font: var(--semantic-font-style-heading-h3);
  color: var(--semantic-color-text-primary);
}
</style>
