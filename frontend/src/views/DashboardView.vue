<script setup>
import { computed, onMounted, watch } from 'vue';
import VantageScoreWidget from '../components/dashboard/widgets/charts/VantageScoreWidget.vue';
import RrDistributionWidget from '../components/dashboard/widgets/charts/RrDistributionWidget.vue';
import CumulativePnlWidget from '../components/dashboard/widgets/charts/CumulativePnlWidget.vue';
import CalendarHeatmap from '../components/dashboard/widgets/Calendar/CalendarHeatmap.vue';
import RecentTradesTable from '../components/dashboard/widgets/Table/RecentTradesTable.vue';
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
        <span class="button-text">{{ editButtonText }}</span>
      </BaseButton>

      <router-link to="/add-trade" custom v-slot="{ navigate }">
        <BaseButton variant="primary" @click="navigate">
          <PlusIcon />
          <span class="button-text">Nuovo Trade</span>
        </BaseButton>
      </router-link>
    </div>

    <!-- Stats Grid -->
    <StatsZone />

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
    <DailySummaryModal />
    <WeeklySummaryModal />
  </div>
</template>

<style lang="scss" scoped>
.dashboard-view {
  width: 100%;
  padding: var(--semantic-size-inset-xl);
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-sm);
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
  gap: var(--semantic-size-stack-sm);
  min-width: 0; /* Fix for grid inside flexbox overflow */
  align-items: start;
}

/* Allow widgets in the main grid to shrink and scroll if their content is too wide */
:deep(.main-content-grid .widget-wrapper) {
  min-width: 0;
  overflow-x: auto;
}

/* --- Mobile First Grid Layout --- */

/* Default (Mobile): 1 colonna per tutto */
:deep(.complex-widgets-grid),
:deep(.main-content-grid) {
  grid-template-columns: 1fr;
}

/* Tablet */
@include media-up('md') {
  :deep(.complex-widgets-grid) {
    grid-template-columns: repeat(2, 1fr);
  }
  :deep(.main-content-grid) {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* Desktop */
@include media-up('lg') {
  :deep(.complex-widgets-grid) {
    grid-template-columns: repeat(3, 1fr);
  }
  :deep(.main-content-grid) {
    grid-template-columns: 2fr 1fr;
  }
}

/* Hide button text on very small screens to save space */
@include media-down('xs') {
  .action-bar .button-text {
    display: none;
  }
}
/* Common widget styles are now encapsulated in their respective zone components */
</style>
