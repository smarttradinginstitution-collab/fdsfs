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

// Import per i grafici
import ChartWidget from '../components/dashboard/ChartWidget.vue';
import EquityCurveChart from '../components/dashboard/EquityCurveChart.vue';
import VantageScoreWidget from '../components/dashboard/VantageScoreWidget.vue';
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

// Dati per i grafici, presi direttamente dallo store
const equityCurveData = computed(() => tradesStore.equityCurveData);

const vantageScoreSubScores = computed(() => {
  const stats = tradesStore.processedStats;
  if (!stats) {
    return { 'Win %': 0, 'Profit factor': 0, 'Avg win/loss': 0, 'Recovery factor': 0, 'Max drawdown': 0, 'Consistency': 0 };
  }
  return {
    'Win %': stats.win_rate_score || 0,
    'Profit factor': stats.profit_factor_score || 0,
    'Avg win/loss': stats.avg_win_loss_score || 0,
    'Recovery factor': stats.recovery_factor_score || 0,
    'Max drawdown': stats.max_drawdown_score || 0,
    'Consistency': stats.consistency_score || 0,
  };
});

const vantageFinalScore = computed(() => {
    return tradesStore.processedStats?.vantage_score || 0;
});


// --- Data Fetching ---
onMounted(() => {
  tradesStore.fetchAllDataForDashboard();
});

// Watch for filter changes and refetch all dashboard data
watch(
  () => [filterStore.startDate, filterStore.endDate, filterStore.selectedStrategy],
  () => {
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

    <!-- Sezione per i grafici -->
    <div class="charts-grid">
      <div v-if="tradesStore.isLoading" class="loading-container">
        <LoadingSpinner />
      </div>
      <template v-else>
        <ChartWidget title="Daily Net Cumulative P&L">
          <EquityCurveChart :chart-data="equityCurveData" />
        </ChartWidget>
        <VantageScoreWidget
          :scores="vantageScoreSubScores"
          :final-score="vantageFinalScore"
        />
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
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--semantic-size-stack-md);
}

.charts-grid {
  display: grid;
  gap: var(--semantic-size-stack-lg);
  grid-template-columns: 1fr;
}

@media (min-width: 1024px) {
  .charts-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

.loading-container {
  grid-column: 1 / -1; /* Span all columns */
  display: grid;
  place-items: center;
  min-height: 300px;
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
</style>
