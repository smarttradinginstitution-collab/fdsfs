<!--
// =============================================================================
// FILE: views/DashboardView.vue
// DESCRIZIONE: Vista della Dashboard, refactored per usare un layout a griglia
// dinamico caricato dal backend, gestendo sia widget complessi che StatCards.
// =============================================================================
-->
<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useTradesStore } from '../stores/trades';
import { useUiStore } from '../stores/uiStore';
import { useFilterStore } from '../stores/filterStore';
import { useAuthStore } from '../stores/auth';
import { useDashboardLayoutStore } from '../stores/dashboardLayout';

// Importa i componenti di vue-grid-layout
import { GridLayout, GridItem } from 'vue-grid-layout-v3';

// Importa i componenti dei widget
import StatCard from '../components/dashboard/StatCard.vue';
import VantageScoreWidget from '../components/dashboard/VantageScoreWidget.vue';
import RrDistributionWidget from '../components/dashboard/RrDistributionWidget.vue';
import CumulativePnlWidget from '../components/dashboard/CumulativePnlWidget.vue';
import CalendarHeatmap from '../components/dashboard/CalendarHeatmap.vue';
import RecentTradesTable from '../components/dashboard/RecentTradesTable.vue';

// Importa componenti UI e icone
import BaseModal from '../components/ui/BaseModal.vue';
import NewTradeForm from '../components/trades/NewTradeForm.vue';
import PopoverMenu from '../components/ui/PopoverMenu.vue';
import StatSelectorMenu from '../components/dashboard/StatSelectorMenu.vue';
import BaseButton from '../components/ui/BaseButton.vue';
import SettingsIcon from '../components/icons/SettingsIcon.vue';
import PlusIcon from '../components/icons/PlusIcon.vue';
import DailySummaryModal from '../components/dashboard/DailySummaryModal.vue';
import WeeklySummaryModal from '../components/dashboard/WeeklySummaryModal.vue';

// Inizializzazione degli store
const tradesStore = useTradesStore();
const uiStore = useUiStore();
const filterStore = useFilterStore();
const authStore = useAuthStore();
const dashboardLayoutStore = useDashboardLayoutStore();

const popoverRef = ref(null);

// Mappa per risolvere dinamicamente i componenti dei widget COMPLESSI
const widgetMap = {
  VantageScore: VantageScoreWidget,
  RrDistribution: RrDistributionWidget,
  CumulativePnlChart: CumulativePnlWidget,
  CalendarHeatmap: CalendarHeatmap,
  RecentTrades: RecentTradesTable,
};

// Getter per accedere facilmente alle statistiche calcolate
const allStats = computed(() => tradesStore.allDashboardStats);

// Handler per la creazione di un nuovo trade
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

// --- Data Fetching ---
onMounted(() => {
  tradesStore.fetchAllDataForDashboard();
  if (authStore.user?.id) {
    dashboardLayoutStore.fetchLayout(authStore.user.id);
  }
});

// Watch per i filtri
watch(
  () => [filterStore.startDate, filterStore.endDate, filterStore.selectedStrategy],
  () => {
    tradesStore.fetchAllDataForDashboard();
  },
  { deep: true }
);

// Watch per il login dell'utente
watch(
  () => authStore.user,
  (newUser) => {
    if (newUser?.id && dashboardLayoutStore.layout.length === 0) {
      dashboardLayoutStore.fetchLayout(newUser.id);
    }
  },
  { immediate: true } // immediate: true per eseguirlo al mount se l'utente è già loggato
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

    <!-- Layout a Griglia Dinamico -->
    <div v-if="dashboardLayoutStore.isLoading" class="loading-spinner">
      Caricamento layout...
    </div>
    <div v-else-if="dashboardLayoutStore.error" class="error-box">
      <h3>Layout Error</h3>
      <p>{{ dashboardLayoutStore.error }}</p>
    </div>
    <grid-layout
      v-else
      v-model:layout="dashboardLayoutStore.layout"
      :col-num="12"
      :row-height="30"
      :is-draggable="false"
      :is-resizable="false"
      :vertical-compact="true"
      :use-css-transforms="true"
    >
      <grid-item
        v-for="item in dashboardLayoutStore.layout"
        :key="item.i"
        :x="item.x"
        :y="item.y"
        :w="item.w"
        :h="item.h"
        :i="item.i"
        class="widget-container"
      >
        <!-- Logica di rendering condizionale -->
        <div v-if="widgetMap[item.component]" class="widget-content">
          <component :is="widgetMap[item.component]" />
        </div>
        <div v-else-if="item.component === 'StatCard'" class="widget-content">
          <StatCard v-if="allStats[item.i]" :stat="allStats[item.i]" />
          <div v-else class="placeholder">Stat '{{ item.i }}' not found</div>
        </div>
        <div v-else class="placeholder">
          Widget '{{ item.component }}' non riconosciuto.
        </div>
      </grid-item>
    </grid-layout>

    <!-- Modali -->
    <BaseModal :show="uiStore.isAddTradeModalOpen" @close="uiStore.closeAddTradeModal">
      <template #header><h3>Log New Trade</h3></template>
      <NewTradeForm @submit="handleNewTrade" />
    </BaseModal>
    <DailySummaryModal />
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

.widget-container {
  background-color: var(--color-background-subtle);
  border-radius: var(--semantic-border-radius-lg);
  padding: var(--semantic-size-inset-lg);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.widget-content {
  width: 100%;
  height: 100%;
}

.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  color: var(--color-text-subtle);
}

.loading-spinner {
  text-align: center;
  padding: 50px;
  font-size: 1.2rem;
}

.error-box {
  padding: var(--semantic-size-inset-lg);
  border-radius: var(--semantic-border-radius-lg);
  background-color: var(--color-background-negative-subtle);
  border: 1px solid var(--color-border-negative);
  color: var(--color-text-negative);
}
</style>