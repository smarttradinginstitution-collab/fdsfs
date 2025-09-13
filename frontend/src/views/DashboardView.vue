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
import WidgetSelector from '../components/dashboard/WidgetSelector.vue';
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

const onLayoutDragEnd = (zone, event) => {
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
    if (!isEditing && dashboardLayoutStore.isDirty) {
      dashboardLayoutStore.saveLayout();
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
      <h3 class="zone-title">Statistiche</h3>
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
    <div class="grid-zone-wrapper">
        <h3 class="zone-title">Grafici</h3>
        <draggable :list="layout.charts" item-key="i" tag="div" class="complex-widgets-grid" ghost-class="ghost" @end="onLayoutDragEnd('charts', $event)" :disabled="!uiStore.isLayoutEditing">
            <template #item="{ element: widget }">
                <div class="widget-wrapper">
                    <component :is="widgetComponents[widget.i]" />
                    <button v-if="uiStore.isLayoutEditing" class="remove-widget-btn" @click="dashboardLayoutStore.removeWidget({ zone: 'charts', widgetId: widget.i })">&times;</button>
                </div>
            </template>
             <template #footer>
                <div class="add-widget-wrapper" v-if="uiStore.isLayoutEditing && layout.charts.length < dashboardLayoutStore.widgetConfig.charts.max">
                    <PopoverMenu>
                        <template #trigger="{ toggle }">
                            <button @click="toggle" class="add-widget-button"><PlusIcon /> Aggiungi Widget</button>
                        </template>
                        <template #content="{ close }">
                            <WidgetSelector zone="charts" :allowed-widgets="dashboardLayoutStore.widgetConfig.charts.allowed" @add-widget="dashboardLayoutStore.addWidget($event); close()" />
                        </template>
                    </PopoverMenu>
                </div>
            </template>
        </draggable>
    </div>

    <!-- Main Content Grid -->
    <div class="grid-zone-wrapper">
        <h3 class="zone-title">Contenuto Principale</h3>
        <draggable :list="layout.main" item-key="i" tag="div" class="main-content-grid" ghost-class="ghost" @end="onLayoutDragEnd('main', $event)" :disabled="!uiStore.isLayoutEditing">
            <template #item="{ element: widget }">
                <div class="widget-wrapper">
                    <component :is="widgetComponents[widget.i]" />
                    <button v-if="uiStore.isLayoutEditing" class="remove-widget-btn" @click="dashboardLayoutStore.removeWidget({ zone: 'main', widgetId: widget.i })">&times;</button>
                </div>
            </template>
            <template #footer>
                <div class="add-widget-wrapper" v-if="uiStore.isLayoutEditing && layout.main.length < dashboardLayoutStore.widgetConfig.main.max">
                    <PopoverMenu>
                        <template #trigger="{ toggle }">
                            <button @click="toggle" class="add-widget-button"><PlusIcon /> Aggiungi Widget</button>
                        </template>
                        <template #content="{ close }">
                            <WidgetSelector zone="main" :allowed-widgets="dashboardLayoutStore.widgetConfig.main.allowed" @add-widget="dashboardLayoutStore.addWidget($event); close()" />
                        </template>
                    </PopoverMenu>
                </div>
            </template>
        </draggable>
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
.grid-zone-wrapper {
    /* Styles for the wrapper if needed */
}
.zone-title {
    margin-bottom: var(--semantic-size-stack-sm);
    font: var(--semantic-font-style-heading-lg);
    color: var(--semantic-color-text-primary);
}
.stats-grid, .complex-widgets-grid, .main-content-grid {
    display: grid;
    gap: var(--semantic-size-stack-lg);
    min-width: 0; /* Fix for grid inside flexbox overflow */
}
.stats-grid {
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
}
.complex-widgets-grid {
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
}
.main-content-grid {
  grid-template-columns: 2fr 1fr;
}
@media (max-width: 1280px) {
  .main-content-grid,
  .complex-widgets-grid {
    grid-template-columns: 1fr;
  }
}
@media (max-width: 640px) {
  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  }
}
.ghost {
    opacity: 0.5;
    background: #c8ebfb;
}
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
</style>
