<template>
  <div class="rounded-lg bg-neutral-800 p-4">
    <h3 class="text-lg font-semibold mb-4">Diagnosi Qualità Esecutiva 🔬</h3>
    <div v-if="isSoaLoading" class="flex items-center justify-center h-64">
      <p>Loading SOA Analysis...</p> <!-- Placeholder per uno skeleton loader -->
    </div>
    <div v-else-if="soaError" class="flex items-center justify-center h-64">
      <p class="text-red-500">{{ soaError }}</p>
    </div>
    <div v-else-if="soaAnalysisData" class="grid grid-cols-10 gap-6">

      <!-- Sezione 1: Diagnosi e Cluster (35% - 3.5/10 -> arrotondato a 4/10 per semplicità di griglia) -->
      <div class="col-span-10 md:col-span-4 flex flex-col space-y-4">
        <HeadlineInsight :headline="soaAnalysisData.headline_insight" />
        <SoaDonutChart :clusters-summary="soaAnalysisData.clusters_summary" />
      </div>

      <!-- Sezione 2: Ottimizzazione Parametrica (40% - 4/10) -->
      <div class="col-span-10 md:col-span-3 flex flex-col">
        <OptimizationGauges :advice="soaAnalysisData.structured_advice" :optimization-data="soaAnalysisData.parametric_optimization" />
      </div>

      <!-- Sezione 3: Pattern Comportamentali (25% - 2.5/10 -> arrotondato a 3/10) -->
      <div class="col-span-10 md:col-span-3 flex flex-col">
        <PsychologicalAlerts :analysis-data="soaAnalysisData" />
      </div>

    </div>
    <div v-else class="flex items-center justify-center h-64">
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
