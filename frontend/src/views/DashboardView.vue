<!--
// =============================================================================
// FILE: views/DashboardView.vue
// DESCRIZIONE: Vista della Dashboard, refattorizzata per usare un layout a griglia dinamico.
// =============================================================================
-->
<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { GridLayout, GridItem } from 'vue-grid-layout';

// Stores
import { useDashboardLayoutStore } from '../stores/dashboardLayout';
import { useTradesStore } from '../stores/trades';
import { useUiStore } from '../stores/uiStore';
import { useFilterStore } from '../stores/filterStore';

// Import all possible widget components
import VantageScoreWidget from '../components/dashboard/VantageScoreWidget.vue';
import RrDistributionWidget from '../components/dashboard/RrDistributionWidget.vue';
import CumulativePnlWidget from '../components/dashboard/CumulativePnlWidget.vue';
import CalendarHeatmap from '../components/dashboard/CalendarHeatmap.vue';
import RecentTradesTable from '../components/dashboard/RecentTradesTable.vue';
// StatCard will be handled differently in a future phase.

// UI Components
import BaseModal from '../components/ui/BaseModal.vue';
import NewTradeForm from '../components/trades/NewTradeForm.vue';
import PopoverMenu from '../components/ui/PopoverMenu.vue';
import StatSelectorMenu from '../components/dashboard/StatSelectorMenu.vue';
import BaseButton from '../components/ui/BaseButton.vue';
import SettingsIcon from '../components/icons/SettingsIcon.vue';
import PlusIcon from '../components/icons/PlusIcon.vue';
import DailySummaryModal from '../components/dashboard/DailySummaryModal.vue';
import WeeklySummaryModal from '../components/dashboard/WeeklySummaryModal.vue';

// Map string keys from layout config to actual imported Vue components
const widgetMap = {
  VantageScoreWidget,
  RrDistributionWidget,
  CumulativePnlWidget,
  CalendarHeatmap,
  RecentTradesTable,
};

const tradesStore = useTradesStore();
const uiStore = useUiStore();
const filterStore = useFilterStore();
const dashboardLayoutStore = useDashboardLayoutStore();

const layout = computed(() => dashboardLayoutStore.layout);

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
  // Fetch data for widgets
  tradesStore.fetchAllDataForDashboard();
  // Fetch the layout configuration
  dashboardLayoutStore.fetchLayout();
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
      <PopoverMenu>
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

    <grid-layout
        v-if="layout.length"
        :layout.sync="layout"
        :col-num="12"
        :row-height="100"
        :is-draggable="false"
        :is-resizable="false"
        :vertical-compact="true"
        :use-css-transforms="true"
    >
        <grid-item
            v-for="item in layout"
            :key="item.i"
            :x="item.x"
            :y="item.y"
            :w="item.w"
            :h="item.h"
            :i="item.i"
        >
            <component :is="widgetMap[item.i]" v-if="widgetMap[item.i]" />
            <div v-else class="widget-placeholder">
              Widget '{{ item.i }}' not found.
            </div>
        </grid-item>
    </grid-layout>
    <div v-else class="loading-placeholder">
      Loading dashboard...
    </div>

    <!-- Modals remain the same -->
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

.widget-placeholder {
  padding: 1rem;
  text-align: center;
  color: var(--semantic-color-text-secondary);
  background-color: var(--semantic-color-surface-secondary);
  border: 1px dashed var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-surface);
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-placeholder {
  flex-grow: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--semantic-color-text-secondary);
  font-size: 1.2rem;
}
</style>
