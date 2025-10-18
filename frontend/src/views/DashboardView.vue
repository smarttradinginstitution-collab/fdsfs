<script setup>
import { computed, onMounted, watch, ref } from 'vue';
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
import { useTradingAccountsStore } from '@/stores/tradingAccounts';
import DailySummaryModal from '../components/dashboard/widgets/Calendar/DailySummaryModal.vue';
import WeeklySummaryModal from '../components/dashboard/widgets/Calendar/WeeklySummaryModal.vue';
import StatSelectorPanel from '../components/dashboard/zones/StatSelectorPanel.vue';

const tradesStore = useTradesStore();
const uiStore = useUiStore();
const filterStore = useFilterStore();
const dashboardLayoutStore = useDashboardLayoutStore();
const tradingAccountsStore = useTradingAccountsStore();

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
  // Carica il layout della dashboard al montaggio del componente.
  dashboardLayoutStore.fetchLayout();
});

// Watch for filter changes and refetch all dashboard data
watch(
  () => [
    filterStore.startDate,
    filterStore.endDate,
    filterStore.selectedStrategy,
    tradingAccountsStore.selectedTradingAccount
  ],
  () => {
    // I dati globali (trades, notes, etc.) sono già stati caricati da initSessionData.
    // Qui carichiamo solo i dati aggregati che dipendono dai filtri e dall'account selezionato.
    if (tradingAccountsStore.selectedTradingAccount) {
      tradesStore.fetchAllDataForDashboard();
    }
  },
  { deep: true, immediate: true } // `immediate: true` per caricare i dati al primo render
);

// Watch for the user finishing layout editing
watch(
  () => uiStore.isLayoutEditing,
  (isEditing) => {
    if (isEditing) {
      dashboardLayoutStore.snapshotLayout();
    } else {
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

    <!-- Stat Selector Panel -->
    <div
      v-if="uiStore.isStatSelectorVisible"
      class="stat-selector-overlay"
      @click="uiStore.closeStatSelector"
    ></div>
    <StatSelectorPanel :is-open="uiStore.isStatSelectorVisible" />
  </div>
</template>

<style lang="scss" scoped>
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
  align-items: center; /* Allinea verticalmente gli elementi */
}
.grid-zone-wrapper {
  /* Styles for the wrapper if needed */
}
.zone-title {
  margin-bottom: var(--semantic-size-stack-sm);
  font: var(--semantic-font-style-heading-lg);
  color: var(--semantic-color-text-primary);
}
/* --- BASE GRID STYLES (MOBILE-FIRST) --- */
:deep(.stats-grid),
:deep(.complex-widgets-grid),
:deep(.main-content-grid) {
  display: grid;
  gap: var(--semantic-size-stack-lg);
  align-items: start;
  min-width: 315px; /* Fase 2: width minima di 315px */
}

/* Fase 1: tutte le griglie a 1 colonna (default mobile) */
:deep(.complex-widgets-grid),
:deep(.main-content-grid) {
  grid-template-columns: 1fr;
}

:deep(.stats-grid) {
  /* Layout fluido moderno: le colonne si adattano e vanno a capo automaticamente */
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
}

/* Allow widgets in all grids to shrink and scroll if their content is too wide */
:deep(.main-content-grid .widget-wrapper),
:deep(.complex-widgets-grid .widget-wrapper) {
  min-width: 0;
  overflow-x: auto;
}

/* --- RESPONSIVE BREAKPOINTS (media-up) --- */

@include media-up('md') {
  :deep(.stats-grid) {
    /* Su schermi più grandi, aumentiamo la larghezza minima delle card */
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }
}

/* --- Complex Widgets Grid --- */
@include media-up('sm') {
  :deep(.complex-widgets-grid) {
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  }
}

/* Limite di 3 colonne per i widget complessi su schermi grandi */
@include media-up('lg') {
  :deep(.complex-widgets-grid) {
    grid-template-columns: repeat(3, 1fr);
  }
}

/* Layout specifico per il calendario da 'xl' in su */
@include media-up('xl') {
  :deep(.main-content-grid) {
    /* Griglia a 2 colonne con rapporto 2:1 */
    grid-template-columns: 2fr 1fr;
  }
}

@include media-down('xs') {
  .action-bar .button-text {
    display: none;
  }
}
/* Common widget styles are now encapsulated in their respective zone components */

.stat-selector-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 999; /* Below the panel, above everything else */
  opacity: 0;
  transition: opacity 0.3s;
  pointer-events: none; /* Allow clicks to pass through when hidden */
}

@include media-up('md') {
  .dashboard-view:has(.stat-selector-panel.is-open) .stat-selector-overlay {
    opacity: 1;
    pointer-events: auto; /* Block clicks when visible */
  }
}
</style>