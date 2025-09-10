<!--
// =============================================================================
// FILE: views/DashboardView.vue
// DESCRIZIONE: Vista della Dashboard, ora con i bottoni di azione principali
// posizionati in una loro sezione dedicata.
// =============================================================================
-->
<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import StatCard from '../components/dashboard/StatCard.vue';
import CalendarHeatmap from '../components/dashboard/CalendarHeatmap.vue';
import RecentTradesTable from '../components/dashboard/RecentTradesTable.vue';
import BaseModal from '../components/ui/BaseModal.vue';
import NewTradeForm from '../components/trades/NewTradeForm.vue';
import PopoverMenu from '../components/ui/PopoverMenu.vue';
import StatSelectorMenu from '../components/dashboard/StatSelectorMenu.vue';
import BaseButton from '../components/ui/BaseButton.vue';
import SettingsIcon from '../components/icons/SettingsIcon.vue';
import PlusIcon from '../components/icons/PlusIcon.vue';
import { useTradesStore } from '../stores/trades';
import { useUiStore } from '../stores/uiStore';
import { useFilterStore } from '../stores/filterStore';
import DailySummaryModal from '../components/dashboard/DailySummaryModal.vue';
import WeeklySummaryModal from '../components/dashboard/WeeklySummaryModal.vue';

// Nuovi import per i grafici
import ChartWidget from '../components/dashboard/ChartWidget.vue';
import EquityCurveChart from '../components/dashboard/EquityCurveChart.vue';
import VantageScoreSpiderChart from '../components/dashboard/VantageScoreSpiderChart.vue';
import AverageRrChart from '../components/dashboard/AverageRrChart.vue';
import LoadingSpinner from '../components/ui/LoadingSpinner.vue';


const tradesStore = useTradesStore();
const uiStore = useUiStore();
const filterStore = useFilterStore();

const popoverRef = ref(null);

const handleNewTrade = async (tradeData) => {
  try {
    const newTrade = await tradesStore.addTrade(tradeData);
    if (newTrade) {
      uiStore.closeAddTradeModal();
      uiStore.showNotification({
        message: 'Trade successfully created!',
        type: 'success',
      });
    }
  } catch (error) {
    console.error('Failed to add trade:', error);
    const errorMessage = error.response?.data?.detail || 'An unknown error occurred.';
    uiStore.showNotification({
      message: `Error: ${errorMessage}`,
      type: 'error',
    });
  }
};

const visibleStats = computed(() => {
  const visibleKeys = uiStore.visibleStatKeys;
  const allStats = tradesStore.allDashboardStats;
  return visibleKeys.map(key => allStats[key]).filter(Boolean);
});

// I dati del grafico vengono ora presi direttamente dallo store,
// che ha la sua logica di caricamento.
const equityCurveData = computed(() => tradesStore.equityCurveData);

const vantageScoreData = computed(() => {
  // Estraiamo l'intero oggetto delle sotto-metriche per lo spider chart
  const stats = tradesStore.dashboardStats?.stats;
  if (!stats) {
    // Return a default structure if stats are not available
    return {
      profit_factor_score: 0,
      avg_win_loss_score: 0,
      max_drawdown_score: 0,
      win_rate_score: 0,
      consistency_score: 0,
      recovery_factor_score: 0,
    };
  }
  return {
    profit_factor_score: stats.profit_factor_score || 0,
    avg_win_loss_score: stats.avg_win_loss_score || 0,
    max_drawdown_score: stats.max_drawdown_score || 0,
    win_rate_score: stats.win_rate_score || 0,
    consistency_score: stats.consistency_score || 0,
    recovery_factor_score: stats.recovery_factor_score || 0,
  };
});


const averageRr = computed(() => {
  // Planned RR non sembra essere disponibile, usiamo solo realized per ora.
  const realized = tradesStore.dashboardStats?.stats?.avg_realized_rr || 0;
  return {
    planned: 0, // Placeholder
    realized: parseFloat(realized) || 0,
  };
});


// --- Data Fetching ---
onMounted(() => {
  // Questa singola azione carica TUTTI i dati necessari per la dashboard,
  // inclusa la equity curve.
  tradesStore.fetchAllDataForDashboard();
});

// Watch for filter changes and refetch all dashboard data
watch(
  () => [filterStore.startDate, filterStore.endDate, filterStore.selectedStrategy],
  () => {
    // La stessa azione viene richiamata quando i filtri cambiano.
    tradesStore.fetchAllDataForDashboard();
  },
  { deep: true }
);
</script>

<template>
  <div class="dashboard-view">

    <div class="action-bar">
      <PopoverMenu ref="popoverRef">
        <template #trigger="{ toggle }">
          <BaseButton variant="secondary" @click="toggle">
            <SettingsIcon />
            <span>Modifica Widget</span>
          </BaseButton>
        </template>
        <template #content="{ close }">
          <StatSelectorMenu @close="close" />
        </template>
      </PopoverMenu>

      <BaseButton variant="primary" @click="uiStore.openAddTradeModal">
        <PlusIcon />
        <span>Nuovo Trade</span>
      </BaseButton>
    </div>

    <div class="stats-grid">
      <StatCard
        v-for="stat in visibleStats"
        :key="stat.key"
        :stat="stat"
      />
    </div>

    <!-- Sezione per i nuovi grafici -->
    <div class="charts-grid">
      <div v-if="tradesStore.isLoading" class="loading-container">
        <LoadingSpinner />
      </div>
      <template v-else>
        <ChartWidget title="Daily Net Cumulative P&L">
          <EquityCurveChart :chart-data="equityCurveData" />
        </ChartWidget>
        <ChartWidget title="Vantage Score">
          <VantageScoreSpiderChart :scores="vantageScoreData" />
        </ChartWidget>
        <ChartWidget title="Average R:R">
          <AverageRrChart :planned-rr="averageRr.planned" :realized-rr="averageRr.realized" />
        </ChartWidget>
      </template>
    </div>


    <div class="main-content-grid">
      <CalendarHeatmap />
      <RecentTradesTable />
    </div>

    <!-- Modale per Aggiungere un Trade -->
    <BaseModal :show="uiStore.isAddTradeModalOpen" @close="uiStore.closeAddTradeModal">
      <template #header><h3>Log New Trade</h3></template>
      <NewTradeForm @submit="handleNewTrade" />
    </BaseModal>

    <!-- Modale per il Riepilogo Giornaliero -->
    <DailySummaryModal />
    <!-- Modale per il Riepilogo Settimanale -->
    <WeeklySummaryModal />
  </div>
</template>

<style scoped>
.dashboard-view {
  width: 100%;
  padding: var(--semantic-size-inset-xl);
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-lg);
}

.action-bar {
  display: flex;
  justify-content: flex-end;
  gap: var(--semantic-size-stack-sm);
}

.stats-grid {
  display: grid;
  /*
    BEST PRACTICE: Griglia Responsiva
    - `repeat(auto-fit, ...)`: Crea tante colonne quante ce ne stanno nello spazio disponibile.
    - `minmax(200px, 1fr)`: Ogni colonna deve essere larga almeno 200px. Se c'è più spazio,
      `1fr` le fa espandere equamente per riempire la larghezza.
    Questo crea una griglia fluida su desktop e tablet.
  */
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--semantic-size-stack-md);
}

.charts-grid {
  display: grid;
  gap: var(--semantic-size-stack-lg);
  /* Default a una colonna per mobile */
  grid-template-columns: 1fr;
}

/* Su schermi medi e grandi, passa a una griglia a 3 colonne */
@media (min-width: 1024px) {
  .charts-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

.loading-container {
  display: grid;
  place-items: center;
  min-height: 300px; /* Altezza simile a quella del grafico */
  background-color: var(--semantic-color-surface-primary);
  border-radius: var(--semantic-border-radius-surface);
  border: var(--base-border-width-1) solid var(--semantic-color-border-default);
}

.main-content-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: var(--semantic-size-stack-lg);
  grid-auto-flow: dense;
}

.main-content-grid > * {
  min-width: 0;
}

.error-box, .data-box {
  padding: var(--semantic-size-inset-lg);
  border-radius: var(--semantic-border-radius-lg);
  background-color: var(--color-background-muted);
  border: 1px solid var(--color-border-subtle);
}

.error-box {
  background-color: var(--color-background-negative-subtle);
  border-color: var(--color-border-negative);
  color: var(--color-text-negative);
}

.data-box pre {
  white-space: pre-wrap;
  word-break: break-all;
  background-color: var(--color-background-subtle);
  padding: var(--semantic-size-inset-md);
  border-radius: var(--semantic-border-radius-md);
}

@media (max-width: 1280px) {
  .main-content-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) { /* sm breakpoint */
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
