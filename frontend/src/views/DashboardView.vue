<script setup>
import { computed, onMounted, watch } from 'vue';
import { GridLayout, GridItem } from 'vue-grid-layout-v3';
import VantageScoreWidget from '../components/dashboard/widgets/charts/VantageScoreWidget.vue';
import RrDistributionWidget from '../components/dashboard/widgets/charts/RrDistributionWidget.vue';
import CumulativePnlWidget from '../components/dashboard/widgets/charts/CumulativePnlWidget.vue';
import CalendarHeatmap from '../components/dashboard/widgets/Calendar/CalendarHeatmap.vue';
import RecentTradesTable from '../components/dashboard/widgets/Table/RecentTradesTable.vue';
import BaseModal from '../components/ui/BaseModal.vue';
import NewTradeForm from '../components/trades/NewTradeForm.vue';
import BaseButton from '../components/ui/BaseButton.vue';
import PlusIcon from '../components/icons/PlusIcon.vue';
import DashboardLayoutSelector from '../components/dashboard/DashboardLayoutSelector.vue';
import { useTradesStore } from '../stores/trades';
import { useUiStore } from '../stores/uiStore';
import { useFilterStore } from '../stores/filterStore';
import { useDashboardLayoutStore } from '../stores/dashboardLayoutStore'; // Changed import path
import DailySummaryModal from '../components/dashboard/widgets/Calendar/DailySummaryModal.vue';
import WeeklySummaryModal from '../components/dashboard/widgets/Calendar/WeeklySummaryModal.vue';
import BaseWidget from '../components/layout/BaseWidget.vue';

const tradesStore = useTradesStore();
const uiStore = useUiStore();
const filterStore = useFilterStore();
const dashboardLayoutStore = useDashboardLayoutStore();

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

const layout = computed({
  get: () => dashboardLayoutStore.layout,
  set: (newLayout) => {
    // vue-grid-layout can emit updates. For now, we don't save them.
    // If you want to make layouts user-editable again in the future,
    // you would call a store action here.
    // E.g., dashboardLayoutStore.updateLayout(newLayout);
  }
});


const widgetComponents = {
  vantageScore: VantageScoreWidget,
  rrDistribution: RrDistributionWidget,
  cumulativePnl: CumulativePnlWidget,
  calendar: CalendarHeatmap,
  recentTrades: RecentTradesTable,
};

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
      <DashboardLayoutSelector />
      <BaseButton variant="primary" @click="uiStore.openAddTradeModal">
        <PlusIcon />
        <span class="button-text">Nuovo Trade</span>
      </BaseButton>
    </div>

    <GridLayout
      v-model:layout="layout"
      :col-num="12"
      :row-height="30"
      :is-draggable="false"
      :is-resizable="false"
      :vertical-compact="true"
      :use-css-transforms="true"
    >
      <GridItem
        v-for="item in layout"
        :key="item.i"
        :x="item.x"
        :y="item.y"
        :w="item.w"
        :h="item.h"
        :i="item.i"
      >
        <BaseWidget>
          <component :is="widgetComponents[item.i]" />
        </BaseWidget>
      </GridItem>
    </GridLayout>

    <!-- Modals -->
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
  align-items: center;
}
.vgl-layout {
    --vgl-resizer-size: 20px;
    --vgl-resizer-border-radius: 3px;
    --vgl-resizer-bg: #f0f0f0;
    --vgl-resizer-border: 2px solid #ccc;
    --vgl-border-color: #ddd;
    --vgl-border-width: 1px;
}
@media (max-width: 400px) {
  .action-bar .button-text {
    display: none;
  }
}
</style>
