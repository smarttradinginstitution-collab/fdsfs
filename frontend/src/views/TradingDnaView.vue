<template>
  <div class="page-container">
    <!-- PAGE HEADER -->
    <div class="header">
      <h1 class="page-title">Trading DNA</h1>
      <p class="page-subtitle">Discover the hidden patterns in your trading performance.</p>
    </div>

    <!-- LOADING & ERROR STATES -->
    <div v-if="store.isLoading && !store.report" class="loading-state">
      <LoadingSpinner />
      <p>Analyzing your trades...</p>
    </div>
    <div v-else-if="store.error" class="error-state">
      <p>An error occurred while analyzing your DNA: {{ store.error }}</p>
    </div>

    <!-- MAIN CONTENT -->
    <div v-else-if="store.report" class="main-content">
      <!-- Insight Cards Section -->
      <div class="section-container">
        <h2 class="section-title">Key Insights</h2>
        <div class="insights-grid">
          <ComboCard v-for="(combo, index) in store.report.golden_combos" :key="`golden-${index}`" title="Golden Combo" :combo="combo" type="golden" />
          <ComboCard v-for="(combo, index) in store.report.toxic_combos" :key="`toxic-${index}`" title="Toxic Combo" :combo="combo" type="toxic" />
        </div>
      </div>

      <!-- DNA Explorer Section -->
      <div class="section-container explorer-section">
        <DnaFilters class="explorer-filters" />
        <div class="explorer-main">
          <GroupPerformanceTable :performance-data="store.report.group_performance" />
          <ComparativeEquityChart :equity-curve-data="store.report.equity_curve" />
        </div>
      </div>
    </div>
     <div v-else class="empty-state">
      <p>No trading data available to generate a report.</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue';
import { useTradingDnaStore } from '@/stores/tradingDnaStore';
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue';
import ComboCard from '@/components/trading-dna/ComboCard.vue';
import DnaFilters from '@/components/trading-dna/DnaFilters.vue';
import GroupPerformanceTable from '@/components/trading-dna/GroupPerformanceTable.vue';
import ComparativeEquityChart from '@/components/trading-dna/ComparativeEquityChart.vue';

const store = useTradingDnaStore();

onMounted(() => {
  // Fetch the initial report without any filters
  store.fetchTradingDnaReport();
});
</script>

<style scoped>
.page-container {
  padding: var(--semantic-size-inset-lg);
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-lg);
}

.header {
  margin-bottom: var(--semantic-size-stack-lg);
}

.page-title {
  font: var(--semantic-font-style-heading-2xl);
}

.page-subtitle {
  font: var(--semantic-font-style-body-base);
  color: var(--semantic-color-text-secondary);
  margin-top: var(--semantic-size-stack-xxs);
}

.loading-state, .empty-state, .error-state {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 50vh;
  gap: var(--semantic-size-stack-md);
  font: var(--semantic-font-style-body-lg);
  color: var(--semantic-color-text-secondary);
}

.section-container {
  margin-bottom: var(--semantic-size-stack-xl);
}

.section-title {
  font: var(--semantic-font-style-heading-xl);
  margin-bottom: var(--semantic-size-stack-md);
}

.insights-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: var(--semantic-size-stack-lg);
}

.explorer-section {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: var(--semantic-size-stack-lg);
  align-items: start;
}

.explorer-main {
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-lg);
}
</style>