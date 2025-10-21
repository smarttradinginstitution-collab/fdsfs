<!--
// =============================================================================
// FILE: views/TradesView.vue
// DESCRIZIONE: Questo componente rappresenta la "vista" della pagina "My Trades".
// Il suo unico scopo è mostrare una tabella con la lista completa di tutti
// i trade registrati dall'utente.
// =============================================================================
-->

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useTradesStore } from '@/stores/trades';
import BaseTable from '@/components/ui/BaseTable.vue';
import KpiDashboard from '@/components/KpiDashboard.vue';
import BaseButton from '@/components/ui/BaseButton.vue';
import { formatDate, formatCurrency, formatPercentage } from '@/utils/formatters.js';

// --- STORE E STATO LOCALE ---
const tradesStore = useTradesStore();
const selectedTrades = ref([]);
const loader = ref(null); // Riferimento all'elemento osservato

let observer;

// --- LOGICA DEL COMPONENTE ---
onMounted(() => {
  // Esegui in parallelo il caricamento delle statistiche e della prima pagina dei trade
  tradesStore.fetchAllDataForDashboard();
  tradesStore.fetchTrades({ ignoreFilters: true });

  // Configura l'IntersectionObserver per il caricamento infinito
  observer = new IntersectionObserver(
    (entries) => {
      const firstEntry = entries[0];
      if (firstEntry.isIntersecting && tradesStore.hasMorePages && !tradesStore.isLoading) {
        tradesStore.fetchTrades({ ignoreFilters: true, loadMore: true });
      }
    },
    { threshold: 1.0 }
  );

  if (loader.value) {
    observer.observe(loader.value);
  }
});

onUnmounted(() => {
  // Pulisci l'observer quando il componente viene smontato
  if (loader.value) {
    observer.unobserve(loader.value);
  }
});

const handleBulkDelete = () => {
  if (selectedTrades.value.length === 0) {
    alert('Nessun trade selezionato.');
    return;
  }
  if (confirm(`Sei sicuro di voler cancellare ${selectedTrades.value.length} trade? L'azione è irreversibile.`)) {
    tradesStore.deleteSelectedTrades(selectedTrades.value);
    selectedTrades.value = []; // Pulisce la selezione dopo la cancellazione
  }
};

const getStatusClass = (pnl) => {
  if (pnl > 0) return 'status-win';
  if (pnl < 0) return 'status-loss';
  return 'status-breakeven';
};

const getPnlClass = (pnl) => {
  if (pnl > 0) return 'pnl-positive';
  if (pnl < 0) return 'pnl-negative';
  return '';
};
</script>

<template>
  <div class="trades-view">
    <h1 class="view-title">Trade Log</h1>
    <KpiDashboard />

    <div class="table-actions">
      <BaseButton
        @click="handleBulkDelete"
        variant="secondary"
        :disabled="selectedTrades.length === 0"
      >
        Bulk Actions
      </BaseButton>
    </div>

    <BaseTable
      :headers="tradesStore.tradeHeaders"
      :items="tradesStore.trades"
      v-model:selected="selectedTrades"
    >
      <!-- Slot per la cella dello stato -->
      <template #status="{ item }">
        <span class="status-pill" :class="getStatusClass(item.p_l)">
          {{ item.p_l > 0 ? 'WIN' : 'LOSS' }}
        </span>
      </template>

      <!-- Slot per le date -->
      <template #entry_timestamp="{ item }">
        {{ formatDate(item.entry_timestamp) }}
      </template>
      <template #exit_timestamp="{ item }">
        {{ formatDate(item.exit_timestamp) }}
      </template>

      <!-- Slot per i valori numerici -->
      <template #entry_price="{ item }">
        {{ item.entry_price ? `$${item.entry_price.toFixed(2)}` : '-' }}
      </template>
      <template #exit_price="{ item }">
        {{ item.exit_price ? `$${item.exit_price.toFixed(2)}` : '-' }}
      </template>

      <!-- Slot per Net P&L con colore condizionale -->
      <template #p_l="{ item }">
        <span :class="getPnlClass(item.p_l)">
          {{ formatCurrency(item.p_l) }}
        </span>
      </template>

      <!-- Slot per Net ROI con colore condizionale -->
      <template #net_roi="{ item }">
         <span :class="getPnlClass(item.p_l)">
          {{ formatPercentage(item.net_roi) }}
        </span>
      </template>

      <!-- Slot per colonne senza dati -->
      <template #vantage_insights="{ item }">
        -
      </template>
      <template #setups="{ item }">
        {{ item.strategy || '-' }}
      </template>
    </BaseTable>

    <!-- Elemento per l'IntersectionObserver -->
    <div ref="loader" class="loader-trigger"></div>

    <!-- Indicatore di caricamento -->
    <div v-if="tradesStore.isLoading && tradesStore.trades.length > 0" class="loading-indicator">
      Loading more trades...
    </div>
  </div>
</template>

<style lang="scss" scoped>
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

.table-actions {
  display: flex;
  justify-content: flex-end; // Allinea il pulsante a destra
  padding-bottom: var(--semantic-size-stack-md); // Spazio sotto il pulsante
}

.status-pill {
  display: inline-block;
  padding: var(--semantic-size-badge-padding-y) var(--semantic-size-badge-padding-x); // Uso i token specifici per i badge per un controllo migliore
  border-radius: var(--semantic-border-radius-tag);
  font: var(--semantic-font-style-label-sm);
  line-height: 1;
  text-transform: uppercase;

  &.status-win {
    background-color: var(--semantic-color-feedback-positive-surface);
    color: var(--semantic-color-feedback-positive-text);
  }

  &.status-loss {
    background-color: var(--semantic-color-feedback-negative-surface);
    color: var(--semantic-color-feedback-negative-text);
  }
}

.pnl-positive {
  color: var(--semantic-color-feedback-positive-text);
}

.pnl-negative {
  color: var(--semantic-color-feedback-negative-text);
}

.loader-trigger {
  height: 50px; /* Un po' di spazio per attivare l'observer prima della fine esatta della pagina */
}

.loading-indicator {
  text-align: center;
  padding: var(--semantic-size-inset-lg);
  font-style: italic;
  color: var(--semantic-color-text-secondary);
}
</style>
