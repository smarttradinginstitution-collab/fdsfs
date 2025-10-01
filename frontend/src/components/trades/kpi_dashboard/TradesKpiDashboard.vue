<script setup>
import { computed } from 'vue';
import { useTradesStore } from '@/stores/trades';
import { storeToRefs } from 'pinia';

// Placeholder imports for the KPI cards that will be created later
import NetPnlCard from './NetPnlCard.vue';
import ProfitFactorCard from './ProfitFactorCard.vue';
import WinRateCard from './WinRateCard.vue';
import AvgWinLossCard from './AvgWinLossCard.vue';
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue';

const tradesStore = useTradesStore();
const { isKpiLoading, kpiDashboardData } = storeToRefs(tradesStore);

const stats = computed(() => kpiDashboardData.value?.stats);
const pnlOverTime = computed(() => kpiDashboardData.value?.pnl_over_time);

</script>

<template>
  <div v-if="isKpiLoading" class="kpi-dashboard-loading">
    <LoadingSpinner />
  </div>
  <div v-else-if="stats" class="kpi-dashboard">
    <!-- Net Cumulative P&L Card -->
    <NetPnlCard :stats="stats" :pnl-data="pnlOverTime" />

    <!-- Profit Factor Card -->
    <ProfitFactorCard :stats="stats" />

    <!-- Win % Card -->
    <WinRateCard :stats="stats" />

    <!-- Avg win/loss trade Card -->
    <AvgWinLossCard :stats="stats" />
  </div>
</template>

<style scoped>
.kpi-dashboard {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--semantic-size-gutter-md);
}

.kpi-dashboard-loading {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 150px;
}

/* Responsive layout: 2 columns on screens smaller than 1200px */
@media (max-width: 1200px) {
  .kpi-dashboard {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* 1 column on screens smaller than 768px */
@media (max-width: 768px) {
  .kpi-dashboard {
    grid-template-columns: 1fr;
  }
}
</style>