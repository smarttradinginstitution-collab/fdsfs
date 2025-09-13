<script setup>
import { computed, onMounted, watch } from 'vue';
import draggable from 'vuedraggable';

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
import BaseButton from '../components/ui/BaseButton.vue';
import SettingsIcon from '../components/icons/SettingsIcon.vue';
import PlusIcon from '../components/icons/PlusIcon.vue';
import DailySummaryModal from '../components/dashboard/DailySummaryModal.vue';
import WeeklySummaryModal from '../components/dashboard/WeeklySummaryModal.vue';
import PopoverMenu from '../components/ui/PopoverMenu.vue';
import WidgetSelector from '../components/dashboard/WidgetSelector.vue';


// Import stores
import { useTradesStore } from '../stores/trades';
import { useUiStore } from '../stores/uiStore';
import { useFilterStore } from '../stores/filterStore';
import { useDashboardLayoutStore } from '../stores/dashboardLayout';

const tradesStore = useTradesStore();
const uiStore = useUiStore();
const filterStore = useFilterStore();
const dashboardLayoutStore = useDashboardLayoutStore();

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

const layout = computed(() => dashboardLayoutStore.layout);

const editButtonText = computed(() => {
  return uiStore.isLayoutEditing ? 'Fine Modifiche' : 'Modifica Widget';
});

function onDragEnd(zone, event) {
  dashboardLayoutStore.moveWidget({
    zone,
    oldIndex: event.oldIndex,
    newIndex: event.newIndex,
  });
}

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
      <BaseButton variant="secondary" @click="uiStore.toggleLayoutEditing()">
        <SettingsIcon />
        <span>{{ editButtonText }}</span>
      </BaseButton>

      <BaseButton variant="primary" @click="uiStore.openAddTradeModal">
        <PlusIcon />
        <span>Nuovo Trade</span>
      </BaseButton>
    </div>

    <div v-if="layout" class="dashboard-zones">
      <!-- Stats Zone -->
      <div class="dashboard-zone zone-stats">
        <div v-for="widget in layout.stats" :key="widget.i" class="widget-wrapper">
          <component
            :is="widgetComponents[widget.i]"
            class="widget-container"
          />
          <!-- No remove button for the main stats group, by design -->
        </div>
      </div>

      <!-- Main Zone -->
      <draggable
        :list="layout.main"
        item-key="i"
        tag="div"
        class="dashboard-zone zone-main"
        ghost-class="ghost"
        @end="onDragEnd('main', $event)"
        :disabled="!uiStore.isLayoutEditing"
      >
        <template #item="{ element: widget }">
          <div class="widget-wrapper">
            <component
              :is="widgetComponents[widget.i]"
              class="widget-container"
            />
            <button
              v-if="uiStore.isLayoutEditing"
              class="remove-widget-btn"
              @click="dashboardLayoutStore.removeWidget({ zone: 'main', widgetId: widget.i })"
            >
              &times;
            </button>
          </div>
        </template>
        <template #footer>
          <div class="add-widget-wrapper" v-if="uiStore.isLayoutEditing && layout.main.length < dashboardLayoutStore.widgetConfig.main.max">
            <PopoverMenu>
              <template #trigger="{ toggle }">
                <BaseButton @click="toggle" variant="secondary" size="small">
                  <PlusIcon /> Aggiungi Widget
                </BaseButton>
              </template>
              <template #content="{ close }">
                <WidgetSelector
                  zone="main"
                  :allowed-widgets="dashboardLayoutStore.widgetConfig.main.allowed"
                  @add-widget="dashboardLayoutStore.addWidget($event); close()"
                />
              </template>
            </PopoverMenu>
          </div>
        </template>
      </draggable>

      <!-- Charts Zone -->
      <draggable
        :list="layout.charts"
        item-key="i"
        tag="div"
        class="dashboard-zone zone-charts"
        ghost-class="ghost"
        @end="onDragEnd('charts', $event)"
        :disabled="!uiStore.isLayoutEditing"
      >
        <template #item="{ element: widget }">
          <div class="widget-wrapper">
            <component
              :is="widgetComponents[widget.i]"
              class="widget-container"
            />
            <button
              v-if="uiStore.isLayoutEditing"
              class="remove-widget-btn"
              @click="dashboardLayoutStore.removeWidget({ zone: 'charts', widgetId: widget.i })"
            >
              &times;
            </button>
          </div>
        </template>
        <template #footer>
          <div class="add-widget-wrapper" v-if="uiStore.isLayoutEditing && layout.charts.length < dashboardLayoutStore.widgetConfig.charts.max">
            <PopoverMenu>
              <template #trigger="{ toggle }">
                <BaseButton @click="toggle" variant="secondary" size="small">
                  <PlusIcon /> Aggiungi Widget
                </BaseButton>
              </template>
              <template #content="{ close }">
                <WidgetSelector
                  zone="charts"
                  :allowed-widgets="dashboardLayoutStore.widgetConfig.charts.allowed"
                  @add-widget="dashboardLayoutStore.addWidget($event); close()"
                />
              </template>
            </PopoverMenu>
          </div>
        </template>
      </draggable>
    </div>
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

.dashboard-zones {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  grid-template-rows: auto;
  gap: var(--semantic-size-stack-lg);
}

.dashboard-zone {
  display: flex;
  gap: var(--semantic-size-stack-lg);
}

.zone-stats {
  grid-column: span 12;
}

.zone-main {
  grid-column: span 8;
}

.zone-charts {
  grid-column: span 4;
  flex-direction: column;
}

.widget-wrapper {
  position: relative;
  flex-grow: 1;
}

.remove-widget-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 24px;
  height: 24px;
  background-color: rgba(0,0,0,0.3);
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
}

.remove-widget-btn:hover {
  background-color: rgba(0,0,0,0.6);
}

.widget-container {
  background-color: var(--color-background-muted);
  border-radius: var(--semantic-border-radius-lg);
  padding: var(--semantic-size-inset-lg);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  width: 100%;
  height: 100%;
}

.ghost {
    opacity: 0.5;
    background: #c8ebfb;
}

.add-widget-wrapper {
  width: 100%;
  display: flex;
  justify-content: center;
  padding: var(--semantic-size-inset-md);
  border: 2px dashed var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-lg);
}
</style>
