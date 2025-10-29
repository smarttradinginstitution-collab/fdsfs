<!--
// =============================================================================
// FILE: views/TradesView.vue
// DESCRIZIONE: Questo componente rappresenta la "vista" della pagina "My Trades".
// Mostra una tabella con la lista completa di tutti i trade, arricchita con
// i dati di clustering SOA (Strength & Opportunity Analysis).
// Include filtri per cluster e azioni di massa.
// =============================================================================
-->
<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useTradesStore } from '@/stores/trades';
import { useAnalyticsStore } from '@/stores/analyticsStore';
import BaseTable from '@/components/ui/BaseTable.vue';
import KpiDashboard from '@/components/KpiDashboard.vue';
import BaseButton from '@/components/ui/BaseButton.vue';
import ClusterBadge from '@/components/ClusterBadge.vue';
import { formatDate, formatCurrency, formatPercentage } from '@/utils/formatters.js';

// --- STORES E STATO LOCALE ---
const tradesStore = useTradesStore();
const analyticsStore = useAnalyticsStore();
const selectedTrades = ref([]);
const selectedCluster = ref(null); // Stato per il filtro del cluster

// --- DATI COMPUTATI ---
// Unisce i trade con i dati SOA quando entrambi sono disponibili.
const tradesWithSoaData = computed(() => {
  if (!tradesStore.trades.length || !analyticsStore.soaAnalysis?.cluster_analysis?.trade_clusters) {
    return [];
  }
  return tradesStore.trades.map(trade => {
    const soaData = analyticsStore.soaAnalysis.cluster_analysis.trade_clusters.find(
      soa => soa.trade_id === trade.id
    );
    return {
      ...trade,
      cluster_id: soaData ? soaData.cluster_id : null,
    };
  });
});

// --- LOGICA DI FILTRAGGIO ---
const applyFilters = () => {
  let params = {};
  if (selectedCluster.value) {
    const filteredTradeIds = tradesWithSoaData.value
      .filter(trade => trade.cluster_id === selectedCluster.value)
      .map(trade => trade.id);

    // Se nessun trade corrisponde al cluster, passiamo un array vuoto per non restituire nulla.
    params.trade_ids = filteredTradeIds.length > 0 ? filteredTradeIds : [];
  } else {
    // Se nessun filtro è selezionato, potremmo voler mostrare tutti i trade.
    // Il backend gestisce un array vuoto come "nessun filtro specifico per ID".
    params.trade_ids = [];
  }
  tradesStore.setTradeIdFilter(params.trade_ids);
};

// --- WATCHERS ---
// Applica i filtri quando il cluster selezionato cambia.
watch(selectedCluster, applyFilters, { immediate: true });

// --- LOGICA DEL COMPONENTE ---
onMounted(async () => {
  // Carica i dati SOA e i trade in parallelo.
  await Promise.all([
    analyticsStore.fetchSoaAnalysis(),
    tradesStore.fetchTrades({ ignoreFilters: true }),
  ]);
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

// --- FUNZIONI DI FORMATTAZIONE ---
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

const formatDuration = (minutes) => {
  if (minutes === null || minutes === undefined) return '-';
  const mins = Math.floor(minutes);
  const secs = Math.round((minutes - mins) * 60);
  return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
};

</script>

<template>
  <div class="trades-view">
    <h1 class="view-title">Trade Log</h1>
    <KpiDashboard />

    <div class="table-actions">
      <!-- Filtro per Cluster -->
      <div class="filter-container">
        <label for="cluster-filter">Filter by Cluster:</label>
        <select id="cluster-filter" v-model="selectedCluster" class="cluster-select">
          <option :value="null">All Clusters</option>
          <option v-for="cluster in analyticsStore.uniqueClusters" :key="cluster" :value="cluster">
            Cluster {{ cluster }}
          </option>
        </select>
      </div>

      <BaseButton
        @click="handleBulkDelete"
        variant="secondary"
        :disabled="selectedTrades.length === 0"
      >
        Bulk Actions
      </BaseButton>
    </div>

    <BaseTable
      :headers="tradesStore.tradeHeadersWithSoa"
      :items="tradesStore.filteredTrades"
      v-model:selected="selectedTrades"
    >
      <!-- Slot per il cluster SOA -->
      <template #cluster_id="{ item }">
        <ClusterBadge v-if="item.cluster_id" :cluster-id="item.cluster_id" />
        <span v-else>-</span>
      </template>

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
      <template #duration_minutes="{ item }">
        {{ formatDuration(item.duration_minutes) }}
      </template>

      <!-- Slot per i valori numerici -->
      <template #entry_price="{ item }">
        {{ item.entry_price ? `$${item.entry_price.toFixed(2)}` : '-' }}
      </template>
      <template #exit_price="{ item }">
        {{ item.exit_price ? `$${item.exit_price.toFixed(2)}` : '-' }}
      </template>
      <template #p_l="{ item }">
        <span :class="getPnlClass(item.p_l)">{{ formatCurrency(item.p_l) }}</span>
      </template>
      <template #net_roi="{ item }">
        <span :class="getPnlClass(item.p_l)">{{ formatPercentage(item.net_roi) }}</span>
      </template>
      <template #vantage_insights="{ item }">-</template>
      <template #setups="{ item }">{{ item.strategy || '-' }}</template>

    </BaseTable>
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
  justify-content: space-between;
  align-items: center;
  padding-bottom: var(--semantic-size-stack-md);
}

.filter-container {
  display: flex;
  align-items: center;
  gap: var(--semantic-size-stack-sm);

  label {
    font: var(--semantic-font-style-label-md);
    color: var(--semantic-color-text-secondary);
  }

  .cluster-select {
    // Stili base per il select
    padding: var(--semantic-size-inset-sm);
    border-radius: var(--semantic-border-radius-pill);
    border: 1px solid var(--semantic-color-border-default);
    background-color: var(--semantic-color-surface-primary);
    color: var(--semantic-color-text-primary);
    font: var(--semantic-font-style-body-md);
  }
}

.status-pill {
  display: inline-block;
  padding: var(--semantic-size-badge-padding-y) var(--semantic-size-badge-padding-x);
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
</style>
