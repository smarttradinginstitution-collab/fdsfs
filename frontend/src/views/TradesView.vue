<!--
// =============================================================================
// FILE: views/TradesView.vue
// DESCRIZIONE: Questo componente rappresenta la "vista" della pagina "My Trades".
// Ora include la logica per caricare i dati in modo reattivo.
// =============================================================================
-->

<script setup>
// --- IMPORTAZIONI ---
import { onMounted, watch } from 'vue';
import { storeToRefs } from 'pinia';

// Importiamo gli store Pinia necessari.
import { useTradesStore } from '@/stores/trades';
import { useFilterStore } from '@/stores/filterStore';
import { useTradingAccountsStore } from '@/stores/tradingAccounts';

// Importiamo il nostro componente riutilizzabile `BaseTable` per visualizzare i dati.
import BaseTable from '@/components/ui/BaseTable.vue';
import TradesKpiDashboard from '@/components/trades/kpi_dashboard/TradesKpiDashboard.vue';


// --- LOGICA DEL COMPONENTE ---

// Creiamo istanze degli store.
const tradesStore = useTradesStore();
const filterStore = useFilterStore();
const tradingAccountsStore = useTradingAccountsStore();

// Usiamo storeToRefs per creare riferimenti reattivi agli stati che osserveremo.
const { selectedTradingAccount } = storeToRefs(tradingAccountsStore);
const { startDate, endDate } = storeToRefs(filterStore);

// --- LIFECYCLE HOOKS E WATCHERS ---

// Al montaggio del componente, carichiamo tutti i dati necessari.
onMounted(() => {
  tradesStore.fetchAllDataForDashboard();
});

// Osserviamo i cambiamenti nell'account di trading selezionato.
// Se cambia, ricarichiamo tutti i dati.
watch(selectedTradingAccount, (newAccount, oldAccount) => {
  // Eseguiamo il fetch solo se l'ID del nuovo account è diverso da quello vecchio
  // per evitare fetch non necessari all'inizializzazione.
  if (newAccount?.id !== oldAccount?.id) {
    tradesStore.fetchAllDataForDashboard();
  }
});

// Osserviamo i cambiamenti nelle date del filtro.
// Se cambiano, ricarichiamo tutti i dati.
watch([startDate, endDate], () => {
  tradesStore.fetchAllDataForDashboard();
});

</script>

<template>
  <!-- Il template definisce la struttura HTML della pagina. -->
  <div class="trades-view">
    <!-- Un semplice titolo per la pagina. -->
    <h1 class="view-title">My Trades</h1>

    <!-- KPI Dashboard Section -->
    <TradesKpiDashboard />

    <!--
    Qui usiamo il nostro componente `BaseTable`.
    - `:headers` riceve la lista delle intestazioni dal getter dello store.
    - `:items` riceve la lista dei trade direttamente dallo stato dello store.
    -->
    <BaseTable
      :headers="tradesStore.tradeHeaders"
      :items="tradesStore.trades"
    />
  </div>
</template>

<style scoped>
.trades-view {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-lg);
  padding: var(--semantic-size-inset-xl);
  flex-grow: 1;
}
.view-title {
  font: var(--semantic-font-style-heading-h3);
  color: var(--semantic-color-text-primary);
}
</style>