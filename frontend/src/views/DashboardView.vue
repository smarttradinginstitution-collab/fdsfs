<script setup>
import { computed, onMounted, watch, ref } from 'vue';
import { GridLayout, GridItem } from 'vue-grid-layout-v3';

// Import all widgets
import StatsGridWidget from '../components/dashboard/StatsGridWidget.vue';
import VantageScoreWidget from '../components/dashboard/VantageScoreWidget.vue';
import RrDistributionWidget from '../components/dashboard/RrDistributionWidget.vue';
import CumulativePnlWidget from '../components/dashboard/CumulativePnlWidget.vue';
import CalendarHeatmap from '../components/dashboard/CalendarHeatmap.vue';
import RecentTradesTable from '../components/dashboard/RecentTradesTable.vue';

// Import UI components
import BaseModal from '../components/ui/BaseModal.vue';
import NewTradeForm from '../components/trades/NewTradeForm.vue';
import PopoverMenu from '../components/ui/PopoverMenu.vue';
import WidgetSelector from '../components/dashboard/WidgetSelector.vue';
import BaseButton from '../components/ui/BaseButton.vue';
import SettingsIcon from '../components/icons/SettingsIcon.vue';
import PlusIcon from '../components/icons/PlusIcon.vue';
import DailySummaryModal from '../components/dashboard/DailySummaryModal.vue';
import WeeklySummaryModal from '../components/dashboard/WeeklySummaryModal.vue';

// Import stores
import { useTradesStore } from '../stores/trades';
import { useUiStore } from '../stores/uiStore';
import { useFilterStore } from '../stores/filterStore';
import { useDashboardLayoutStore } from '../stores/dashboardLayout';

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

// Get layout from the store
const layout = computed(() => dashboardLayoutStore.layout);

// --- Data Fetching ---
onMounted(() => {
  tradesStore.fetchAllDataForDashboard();
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

const onLayoutUpdated = (newLayout) => {
  dashboardLayoutStore.saveLayout(newLayout);
};

const editButtonText = computed(() => {
  return uiStore.isLayoutEditing ? 'Fine Modifiche' : 'Modifica Widget';
});

// Map widget keys to components
const widgetComponents = {
  stats: StatsGridWidget,
  vantageScore: VantageScoreWidget,
  rrDistribution: RrDistributionWidget,
  cumulativePnl: CumulativePnlWidget,
  calendar: CalendarHeatmap,
  recentTrades: RecentTradesTable,
};
</script>

<template>
  <div class="dashboard-view">
    <div class="action-bar">
      <PopoverMenu v-if="uiStore.isLayoutEditing">
        <template #trigger="{ toggle }">
          <BaseButton variant="secondary" @click="toggle">
            <PlusIcon />
            <span>Aggiungi Widget</span>
          </BaseButton>
        </template>
        <template #content="{ close }">
          <WidgetSelector
            @add-widget="dashboardLayoutStore.addWidget($event); close()"
            @remove-widget="dashboardLayoutStore.removeWidget"
          />
        </template>
      </PopoverMenu>

      <BaseButton variant="secondary" @click="uiStore.toggleLayoutEditing()">
        <SettingsIcon />
        <span>{{ editButtonText }}</span>
      </BaseButton>

      <BaseButton variant="primary" @click="uiStore.openAddTradeModal">
        <PlusIcon />
        <span>Nuovo Trade</span>
      </BaseButton>
    </div>

    <grid-layout
      v-if="layout.length"
      :layout.sync="layout"
      :col-num="12"
      :row-height="30"
      :is-draggable="uiStore.isLayoutEditing"
      :is-resizable="uiStore.isLayoutEditing"
      :vertical-compact="true"
      :use-css-transforms="true"
      class="dashboard-grid"
      :class="{ 'is-editing': uiStore.isLayoutEditing }"
      @layout-updated="onLayoutUpdated"
    >
      <grid-item
        v-for="item in layout"
        :key="item.i"
        :x="item.x"
        :y="item.y"
        :w="item.w"
        :h="item.h"
        :i="item.i"
        class="widget-container"
      >
        <component :is="widgetComponents[item.i]" />
      </grid-item>
    </grid-layout>
    <div v-else class="loading-placeholder">
      Loading dashboard...
    </div>

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
}

.dashboard-grid {
  width: 100%;
}

.widget-container {
  background-color: var(--color-background-muted);
  border-radius: var(--semantic-border-radius-lg);
  padding: var(--semantic-size-inset-lg);
  display: flex;
  flex-direction: column;
  overflow: hidden; /* Ensure content respects the container boundaries */
}

.loading-placeholder {
  width: 100%;
  height: 500px;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: var(--font-size-xl);
  color: var(--color-text-subtle);
}
</style>
<style>
/* vue-grid-layout-v3 optional styles */
.vue-grid-layout {
  background: transparent;
}
.vue-grid-layout.is-editing {
  border: 2px dashed var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-lg);
  padding: var(--base-size-spacing-2);
}
.vue-grid-item:not(.vue-grid-placeholder) {
  background: var(--color-background-muted);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--semantic-border-radius-lg);
}
.vue-grid-item .resizing {
  opacity: 0.9;
}
.vue-grid-item .static {
  background: #cce;
}
.vue-grid-item .text {
  font-size: 24px;
  text-align: center;
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  margin: auto;
  height: 100%;
  width: 100%;
}
.vue-grid-item .minMax {
  font-size: 12px;
}
.vue-grid-item .add {
  cursor: pointer;
}
.vue-draggable-handle {
  position: absolute;
  width: 20px;
  height: 20px;
  top: 0;
  left: 0;
  background: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='10' height='10'><circle cx='5' cy='5' r='5' fill='#999999'/></svg>") no-repeat;
  background-position: bottom right;
  padding: 0 8px 8px 0;
  background-repeat: no-repeat;
  background-origin: content-box;
  box-sizing: border-box;
  cursor: pointer;
}
</style>
