<script setup>
import { computed, onMounted, watch } from 'vue';
import VantageScoreWidget from '../components/dashboard/widgets/charts/VantageScoreWidget.vue';
import RrDistributionWidget from '../components/dashboard/widgets/charts/RrDistributionWidget.vue';
import CumulativePnlWidget from '../components/dashboard/widgets/charts/CumulativePnlWidget.vue';
import CalendarHeatmap from '../components/dashboard/widgets/Calendar/CalendarHeatmap.vue';
import RecentTradesTable from '../components/dashboard/widgets/Table/RecentTradesTable.vue';
import BaseModal from '../components/ui/BaseModal.vue';
import NewTradeForm from '../components/trades/NewTradeForm.vue';
import DashboardZone from '../components/dashboard/zones/DashboardZone.vue';
import StatsZone from '../components/dashboard/zones/StatsZone.vue';
import BaseButton from '../components/ui/BaseButton.vue';
import SettingsIcon from '../components/icons/SettingsIcon.vue';
import PlusIcon from '../components/icons/PlusIcon.vue';
import { useTradesStore } from '../stores/trades';
import { useUiStore } from '../stores/uiStore';
import { useFilterStore } from '../stores/filterStore';
import { useDashboardLayoutStore } from '../stores/dashboardLayout';
import DailySummaryModal from '../components/dashboard/widgets/Calendar/DailySummaryModal.vue';
import WeeklySummaryModal from '../components/dashboard/widgets/Calendar/WeeklySummaryModal.vue';

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

const currentLayoutTemplate = computed(() => dashboardLayoutStore.currentLayoutTemplate);
const currentLayoutData = computed(() => dashboardLayoutStore.currentLayoutData);

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
  <div class="dashboard-view" :class="[currentLayoutTemplate.cssClass, { 'is-editing': uiStore.isLayoutEditing }]">
    <div class="action-bar">
      <div class="layout-selector">
        <label for="layout-select">Layout:</label>
        <select
          id="layout-select"
          :value="dashboardLayoutStore.selectedLayoutId"
          @change="dashboardLayoutStore.selectLayout($event.target.value)"
        >
          <option
            v-for="(template, id) in dashboardLayoutStore.layoutTemplates"
            :key="id"
            :value="id"
          >
            {{ template.name }}
          </option>
        </select>
      </div>
      <BaseButton variant="secondary" @click="uiStore.toggleLayoutEditing()">
        <SettingsIcon />
        <span class="button-text">{{ editButtonText }}</span>
      </BaseButton>

      <BaseButton variant="primary" @click="uiStore.openAddTradeModal">
        <PlusIcon />
        <span class="button-text">Nuovo Trade</span>
      </BaseButton>
    </div>

    <!-- Stats Grid (only for layouts that don't define their own stats slots) -->
    <StatsZone v-if="dashboardLayoutStore.selectedLayoutId === 'layout_a'" />

    <!-- Dynamic Content Grid -->
    <div class="dashboard-content-grid">
      <div
        v-for="slot in currentLayoutTemplate.slots"
        :key="slot.id"
        :style="{ gridArea: slot.id }"
        class="dashboard-slot"
      >
        <DashboardZone
            :zone-id="slot.id"
            :widgets="currentLayoutData[slot.id]"
            :widget-components="widgetComponents"
            :grid-class="'zone-' + slot.id"
            :max-items="slot.max"
            :allowed-widgets="slot.allowed"
            @drag-end="onLayoutDragEnd"
            @add-widget="dashboardLayoutStore.addWidget({ slotId: slot.id, widgetId: $event.widgetId })"
            @remove-widget="dashboardLayoutStore.removeWidget({ slotId: slot.id, widgetId: $event.widgetId })"
        />
      </div>
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
  align-items: center;
  gap: var(--semantic-size-stack-lg);
}
.layout-selector {
  display: flex;
  align-items: center;
  gap: var(--semantic-size-stack-sm);
  margin-right: auto; /* Pushes the other buttons to the right */
  color: var(--semantic-color-text-primary);
}
.layout-selector select {
    background-color: var(--semantic-color-surface-primary);
    color: var(--semantic-color-text-primary);
    border: 1px solid var(--semantic-color-border-default);
    border-radius: var(--semantic-border-radius-md);
    padding: var(--semantic-size-inset-sm);
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
    align-items: start;
}
.stats-grid {
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
}
:deep(.complex-widgets-grid) {
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
}
:deep(.main-content-grid) {
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
}

/* --- Layout A: Standard --- */
.layout-standard .dashboard-content-grid {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-lg);
}
.layout-standard :deep(.zone-main) {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--semantic-size-stack-lg);
}
.layout-standard :deep(.zone-main .widget-wrapper:first-child) {
  grid-column: span 2;
}

/* --- Layout B: Complex --- */
.layout-complex .dashboard-content-grid {
  display: grid;
  gap: var(--semantic-size-stack-lg);
  grid-template-columns: repeat(3, 1fr);
  grid-template-areas:
    "stats1         stats2         stats3"
    "stats4         .              ."
    "chart_v1       calendar_large calendar_large"
    "chart_v2       calendar_large calendar_large"
    "chart_h1       chart_h2       chart_h3";
}

@media (max-width: 1280px) {
  :deep(.main-content-grid),
  :deep(.complex-widgets-grid) {
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  }
  .layout-complex .dashboard-content-grid {
    grid-template-columns: 1fr; /* Stack everything on smaller screens */
    grid-template-areas:
      "stats1"
      "stats2"
      "stats3"
      "stats4"
      "chart_v1"
      "chart_v2"
      "calendar_large"
      "chart_h1"
      "chart_h2"
      "chart_h3";
  }
}
@media (max-width: 640px) {
  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  }
}

@media (max-width: 400px) {
  .action-bar .button-text {
    display: none;
  }
}
/* Common widget styles are now encapsulated in their respective zone components */
</style>
