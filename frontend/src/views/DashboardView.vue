<script setup>
import { computed, onMounted, watch } from 'vue';
import draggable from 'vuedraggable';
import StatCard from '../components/dashboard/StatCard.vue';
import VantageScoreWidget from '../components/dashboard/VantageScoreWidget.vue';
import RrDistributionWidget from '../components/dashboard/RrDistributionWidget.vue';
import CumulativePnlWidget from '../components/dashboard/CumulativePnlWidget.vue';
import CalendarHeatmap from '../components/dashboard/CalendarHeatmap.vue';
import RecentTradesTable from '../components/dashboard/RecentTradesTable.vue';
import BaseModal from '../components/ui/BaseModal.vue';
import NewTradeForm from '../components/trades/NewTradeForm.vue';
import PopoverMenu from '../components/ui/PopoverMenu.vue';
import StatSelectorMenu from '../components/dashboard/StatSelectorMenu.vue';
import DashboardZone from '../components/dashboard/DashboardZone.vue';
import BaseButton from '../components/ui/BaseButton.vue';
import SettingsIcon from '../components/icons/SettingsIcon.vue';
import PlusIcon from '../components/icons/PlusIcon.vue';
import { useTradesStore } from '../stores/trades';
import { useUiStore } from '../stores/uiStore';
import { useFilterStore } from '../stores/filterStore';
import { useDashboardLayoutStore } from '../stores/dashboardLayout';
import DailySummaryModal from '../components/dashboard/DailySummaryModal.vue';
import WeeklySummaryModal from '../components/dashboard/WeeklySummaryModal.vue';

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

const layout = computed(() => dashboardLayoutStore.layout);

const widgetComponents = {
  'vantageScore': VantageScoreWidget,
  'rrDistribution': RrDistributionWidget,
  'cumulativePnl': CumulativePnlWidget,
  'calendar': CalendarHeatmap,
  'recentTrades': RecentTradesTable,
};

const onLayoutDragEnd = ({ zone, event }) => {
  dashboardLayoutStore.moveWidget({
    zone,
    oldIndex: event.oldIndex,
    newIndex: event.newIndex,
  });
};

const onStatsDragEnd = (event) => {
  uiStore.moveStat({
    oldIndex: event.oldIndex,
    newIndex: event.newIndex,
  });
};

const editButtonText = computed(() => {
  return uiStore.isLayoutEditing ? 'Fine Modifiche' : 'Modifica Widget';
});

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

// Watch for the user finishing layout editing
watch(
  () => uiStore.isLayoutEditing,
  (isEditing) => {
    if (isEditing) {
      // User just entered edit mode, take a snapshot of the current layout
      dashboardLayoutStore.snapshotLayout();
    } else {
      // User just finished editing, check if dirty and save
      if (dashboardLayoutStore.isDirty) {
        dashboardLayoutStore.saveLayout();
      }
    }
  }
);
</script>

<template>
  <div class="dashboard-view" :class="{ 'is-editing': uiStore.isLayoutEditing }">
    <div class="action-bar">
      <BaseButton variant="secondary" @click="uiStore.toggleLayoutEditing()">
        <SettingsIcon />
        <span>{{ editButtonText }}</span>
      </BaseButton>

      <BaseButton variant="primary" @click="uiStore.openAddTradeModal">
        <PlusIcon />
        <span>Nuovo Trade</span>
      </BaseButton>
    </div>

    <!-- Stats Grid -->
    <div class="grid-zone-wrapper">
      <draggable
        :list="uiStore.visibleStatKeys"
        item-key="key"
        tag="div"
        class="stats-grid"
        ghost-class="ghost"
        @end="onStatsDragEnd"
        :disabled="!uiStore.isLayoutEditing"
      >
        <template #item="{ element: statKey }">
          <div class="widget-wrapper">
            <StatCard :stat="tradesStore.allDashboardStats[statKey]" />
            <button v-if="uiStore.isLayoutEditing" class="remove-widget-btn" @click="uiStore.toggleStatVisibility(statKey)">&times;</button>
          </div>
        </template>
        <template #footer>
            <PopoverMenu v-if="uiStore.isLayoutEditing">
                <template #trigger="{ toggle }">
                    <button @click="toggle" class="add-widget-button">
                        <PlusIcon /> Aggiungi o Rimuovi Stat
                    </button>
                </template>
                <template #content="{ close }">
                    <StatSelectorMenu @close="close" />
                </template>
            </PopoverMenu>
        </template>
      </draggable>
    </div>

    <!-- Charts Zone -->
    <DashboardZone
      zone-id="charts"
      :widgets="layout.charts"
      :widget-components="widgetComponents"
      grid-class="complex-widgets-grid"
      :max-items="dashboardLayoutStore.widgetConfig.charts.max"
      :allowed-widgets="dashboardLayoutStore.widgetConfig.charts.allowed"
      @drag-end="onLayoutDragEnd"
      @add-widget="dashboardLayoutStore.addWidget($event)"
      @remove-widget="dashboardLayoutStore.removeWidget($event)"
    />

    <!-- Main Content Grid -->
    <DashboardZone
      zone-id="main"
      :widgets="layout.main"
      :widget-components="widgetComponents"
      grid-class="main-content-grid"
      :max-items="dashboardLayoutStore.widgetConfig.main.max"
      :allowed-widgets="dashboardLayoutStore.widgetConfig.main.allowed"
      @drag-end="onLayoutDragEnd"
      @add-widget="dashboardLayoutStore.addWidget($event)"
      @remove-widget="dashboardLayoutStore.removeWidget($event)"
    />

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
.grid-zone-wrapper {
    /* Styles for the wrapper if needed */
}
.zone-title {
    margin-bottom: var(--semantic-size-stack-sm);
    font: var(--semantic-font-style-heading-lg);
    color: var(--semantic-color-text-primary);
}
.stats-grid,
:deep(.complex-widgets-grid),
:deep(.main-content-grid) {
    display: grid;
    gap: var(--semantic-size-stack-lg);
    min-width: 0; /* Fix for grid inside flexbox overflow */
}
.stats-grid {
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
}
:deep(.complex-widgets-grid) {
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
}
:deep(.main-content-grid) {
  grid-template-columns: 2fr 1fr;
}
@media (max-width: 1280px) {
  :deep(.main-content-grid),
  :deep(.complex-widgets-grid) {
    grid-template-columns: 1fr;
  }
}
@media (max-width: 640px) {
  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  }
}
/* The styles for ghost, widget-wrapper, remove-widget-btn, and add-widget-button
   have been moved to the DashboardZone.vue and StatsZone components */
.widget-wrapper {
  position: relative;
}
.dashboard-view.is-editing .widget-wrapper {
    cursor: grab;
}
.dashboard-view.is-editing .widget-wrapper:active {
    cursor: grabbing;
}
.remove-widget-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 24px;
  height: 24px;
  background-color: rgba(0,0,0,0.4);
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 16px;
  line-height: 1;
  transition: background-color 0.2s;
  z-index: 10;
}
.remove-widget-btn:hover {
  background-color: rgba(0,0,0,0.7);
}
.add-widget-button {
    background-color: var(--semantic-color-surface-primary);
    border: 2px dashed var(--semantic-color-border-default);
    color: var(--semantic-color-text-secondary);
    border-radius: var(--semantic-border-radius-lg);
    padding: var(--semantic-size-inset-lg);
    cursor: pointer;
    width: 100%;
    min-height: 100px;
    display: flex;
    justify-content: center;
    align-items: center;
    gap: var(--semantic-size-stack-sm);
    transition: all 0.2s;
}
.add-widget-button:hover {
    background-color: var(--semantic-color-surface-secondary);
    color: var(--semantic-color-text-primary);
    border-color: var(--semantic-color-border-focus);
}
.ghost {
  opacity: 0.5;
  background-color: var(--semantic-color-surface-secondary);
}
</style>
