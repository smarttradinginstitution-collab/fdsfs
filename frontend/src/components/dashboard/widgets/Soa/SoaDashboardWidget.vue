<template>
  <div class="rounded-lg bg-neutral-800 p-4">
    <h3 class="text-lg font-semibold mb-4">Diagnosi Performance SOA 🧠</h3>
    <div v-if="isSoaLoading" class="flex items-center justify-center h-48">
      <p>Loading SOA Analysis...</p>
    </div>
    <div v-else-if="soaError" class="flex items-center justify-center h-48">
      <p class="text-red-500">{{ soaError }}</p>
    </div>
    <div v-else-if="soaAnalysisData" class="flex flex-col space-y-4">
      <HeadlineInsight :headline="soaAnalysisData.headline_insight" />
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <SoaDonutChart :clusters-summary="soaAnalysisData.clusters_summary" />
        <div class="flex flex-col justify-between space-y-4">
          <OptimizationGauges :advice="soaAnalysisData.structured_advice" />
          <PsychologicalAlerts :advice="soaAnalysisData.structured_advice" />
        </div>
      </div>
    </div>
    <div v-else class="flex items-center justify-center h-48">
      <p>No SOA data available for the selected period.</p>
    </div>
  </div>
</template>

<script setup>
/**
 * @file SoaDashboardWidget.vue
 * @description
 * This is the main container widget for the Strength & Opportunity Analysis (SOA)
 * dashboard. It orchestrates data fetching from the analyticsStore and passes
 * the relevant data down to its child components for rendering.
 */
import { onMounted } from 'vue';
import { useAnalyticsStore } from '@/stores/analyticsStore';
import { storeToRefs } from 'pinia';
import HeadlineInsight from './HeadlineInsight.vue';
import SoaDonutChart from './SoaDonutChart.vue';
import OptimizationGauges from './OptimizationGauges.vue';
import PsychologicalAlerts from './PsychologicalAlerts.vue';

const analyticsStore = useAnalyticsStore();
const { soaAnalysisData, isSoaLoading, soaError } = storeToRefs(analyticsStore);

onMounted(() => {
  if (!soaAnalysisData.value) {
    analyticsStore.fetchSoaAnalysis();
  }
});
</script>
