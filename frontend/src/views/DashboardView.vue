<!--
// =============================================================================
// FILE: views/DashboardView.vue
// DESCRIZIONE: Vista della Dashboard, ora con i bottoni di azione principali
// posizionati in una loro sezione dedicata.
// =============================================================================
-->
<script setup>
import { ref, computed, onMounted } from 'vue';
import apiClient from '../services/api';
import StatCard from '../components/dashboard/StatCard.vue';
import CalendarHeatmap from '../components/dashboard/CalendarHeatmap.vue';
import RecentTradesTable from '../components/dashboard/RecentTradesTable.vue';
import BaseModal from '../components/ui/BaseModal.vue';
import NewTradeForm from '../components/trades/NewTradeForm.vue';
import StatSelector from '../components/dashboard/StatSelector.vue';
import BaseButton from '../components/ui/BaseButton.vue';
import SettingsIcon from '../components/icons/SettingsIcon.vue';
import PlusIcon from '../components/icons/PlusIcon.vue';
import { useTradesStore } from '../stores/trades';
import { useUiStore } from '../stores/uiStore';
import DailySummaryModal from '../components/dashboard/DailySummaryModal.vue';
import WeeklySummaryModal from '../components/dashboard/WeeklySummaryModal.vue';

const tradesStore = useTradesStore();
const uiStore = useUiStore();

const isSettingsModalOpen = ref(false);

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
  return visibleKeys.map(key => allStats[key]);
});

// --- DATA FETCHING EXAMPLE ---
// Esempio di come recuperare i dati dal backend
const backendData = ref(null);
const fetchError = ref(null);

onMounted(() => {
  tradesStore.fetchDashboardStats();
  tradesStore.fetchCalendarData();
});
</script>

<template>
  <div class="dashboard-view">

    <!-- Esempio di visualizzazione dati dal backend -->
    <!-- <div v-if="fetchError" class="error-box">
      <h3>Backend Connection Error</h3>
      <p>{{ fetchError }}</p>
    </div>
    <div v-if="backendData" class="data-box">
      <h3>Data from Backend (for testing):</h3>
      <pre>{{ JSON.stringify(backendData, null, 2) }}</pre>
    </div> -->


    <div class="action-bar">
      <BaseButton variant="secondary" @click="isSettingsModalOpen = true">
        <SettingsIcon />
        <span>Modifica Widget</span>
      </BaseButton>
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

    <div class="main-content-grid">
      <CalendarHeatmap />
      <RecentTradesTable />
    </div>

    <!-- Modale per Aggiungere un Trade -->
    <BaseModal :show="uiStore.isAddTradeModalOpen" @close="uiStore.closeAddTradeModal">
      <template #header><h3>Log New Trade</h3></template>
      <NewTradeForm @submit="handleNewTrade" />
    </BaseModal>

    <!-- Modale per Personalizzare le Statistiche -->
    <BaseModal :show="isSettingsModalOpen" @close="isSettingsModalOpen = false">
      <template #header><h3>Customize Dashboard Stats</h3></template>
      <template #default><StatSelector /></template>
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
