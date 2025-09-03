<!--
// =============================================================================
// FILE: views/DashboardView.vue
// DESCRIZIONE: Vista della Dashboard, ora con i bottoni di azione principali
// posizionati in una loro sezione dedicata.
// =============================================================================
-->
<script setup>
import { ref, computed } from 'vue';
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

const isAddTradeModalOpen = ref(false);
const isSettingsModalOpen = ref(false);

const handleNewTrade = (tradeData) => {
  tradesStore.addTrade(tradeData);
  isAddTradeModalOpen.value = false;
};

const visibleStats = computed(() => {
  const visibleKeys = uiStore.visibleStatKeys;
  const allStats = tradesStore.allDashboardStats;
  return visibleKeys.map(key => allStats[key]);
});
</script>

<template>
  <div class="dashboard-view">
    <div class="action-bar">
      <BaseButton variant="secondary" @click="isSettingsModalOpen = true">
        <SettingsIcon />
        <span>Modifica Widget</span>
      </BaseButton>
      <BaseButton variant="primary" @click="isAddTradeModalOpen = true">
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
    <BaseModal :show="isAddTradeModalOpen" @close="isAddTradeModalOpen = false">
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

@media (max-width: 1280px) {
  .main-content-grid {
    grid-template-columns: 1fr;
  }
}
</style>
