<template>
  <BaseWidget>
    <template #title>
      <div class="flex items-center gap-2">
        <SvgIcon name="analyze" size="24" />
        <span>Sintesi Predittiva SOA</span>
      </div>
    </template>
    <template #actions>
      <router-link to="/soa-analysis" class="text-sm text-blue-400 hover:underline">
        Scopri di più
      </router-link>
    </template>

    <div v-if="isLoading" class="flex items-center justify-center h-64">
      <LoadingSpinner />
    </div>
    <div v-else-if="!analysisData || analysisData.error" class="flex items-center justify-center h-64">
      <p class="text-gray-400">{{ analysisData?.error || "Nessun dato disponibile per l'analisi." }}</p>
    </div>
    <div v-else class="grid grid-cols-1 md:grid-cols-12 gap-6">
      <!-- Sezione 1: Diagnosi e Cluster -->
      <div class="col-span-12 md:col-span-4 p-4 bg-neutral-800 rounded-lg">
        <h3 class="flex items-center gap-2 font-semibold mb-3">
          <SvgIcon name="microscope" size="20" />
          Diagnosi Qualità Esecutiva
        </h3>
        <HeadlineInsight :text="analysisData.headline_insight" :icon="headlineIcon" />
        <SOADonutChart :data="analysisData.cluster_percentages" class="mt-4" />
      </div>

      <!-- Sezione 2: Ottimizzazione Parametrica -->
      <div class="col-span-12 md:col-span-5 p-4 bg-neutral-800 rounded-lg">
        <h3 class="flex items-center gap-2 font-semibold mb-3">
          <SvgIcon name="wrench" size="20" />
          Leve di Ottimizzazione R:R
        </h3>
        <div class="flex flex-col gap-4">
          <!-- Blocco SL -->
          <div>
            <AdviceText :text="analysisData.structured_advice.sl_advice" />
            <BulletGraph v-if="slBulletData" v-bind="slBulletData" />
          </div>
          <!-- Blocco TP -->
          <div>
            <AdviceText :text="analysisData.structured_advice.tp_advice" />
            <BulletGraph v-if="tpBulletData" v-bind="tpBulletData" />
          </div>
        </div>
      </div>

      <!-- Sezione 3: Pattern Comportamentali -->
      <div class="col-span-12 md:col-span-3 p-4 bg-neutral-800 rounded-lg">
        <h3 class="flex items-center gap-2 font-semibold mb-3">
          <SvgIcon name="brain" size="20" />
          Monitoraggio Psicologico
        </h3>
        <div v-if="shouldShowAutocorrAlert || shouldShowDrawdownAlert" class="flex flex-col gap-3">
          <AlertItem
            v-if="shouldShowAutocorrAlert"
            type="autocorrelation"
            :value="analysisData.predictive_metrics.r_autocorrelation"
            label="R-Autocorr."
            :tooltip="analysisData.structured_advice.psychological_advice"
            :threshold="0.3"
          />
          <AlertItem
            v-if="shouldShowDrawdownAlert"
            type="drawdown"
            :value="analysisData.drawdown_z_score.z_score"
            label="Z-Score DD"
            :tooltip="analysisData.structured_advice.psychological_advice"
            :threshold="2.0"
          />
        </div>
        <div v-else class="flex items-center gap-2 text-green-400">
          <SvgIcon name="circle-check" size="20" />
          <span>Pattern Stabili</span>
        </div>
      </div>
    </div>
  </BaseWidget>
</template>

<script setup>
import { computed } from 'vue';
import BaseWidget from '@/components/layout/BaseWidget.vue';
import HeadlineInsight from './HeadlineInsight.vue';
import SOADonutChart from './SoaDonutChart.vue';
import AdviceText from './AdviceText.vue';
import BulletGraph from './BulletGraph.vue';
import AlertItem from './AlertItem.vue';
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue';
import SvgIcon from '@/components/ui/SvgIcon.vue';

const props = defineProps({
  analysisData: {
    type: Object,
    default: () => null,
  },
  isLoading: {
    type: Boolean,
    default: false,
  },
});

// --- Sezione 1 Logic ---
const headlineIcon = computed(() => {
  const text = props.analysisData?.headline_insight?.toLowerCase() || '';
  if (['costosi', 'limitano', 'problema', 'rischio', 'eccessivo', 'negativo', 'stretto', 'stretti'].some(kw => text.includes(kw))) {
    return 'warning';
  }
  if (['solida', 'allineato', 'opportunità', 'efficace', 'positivo', 'ottimale'].some(kw => text.includes(kw))) {
    return 'positive';
  }
  return 'neutral';
});

// --- Sezione 2 Logic ---
const slData = computed(() => props.analysisData?.parametric_optimization);
const tpData = computed(() => props.analysisData?.parametric_optimization);

const slBulletData = computed(() => {
  if (!slData.value || slData.value.sl_optimal_p95 == null) return null;
  const { sl_optimal_p90, sl_optimal_p95, avg_user_stress_ratio } = slData.value;
  return {
    title: "Stop Loss",
    value: avg_user_stress_ratio,
    target: sl_optimal_p95,
    ranges: [
      { value: sl_optimal_p90, color: '#f56565', label: 'Stretta' }, // Red
      { value: sl_optimal_p95, color: '#48bb78', label: 'Ottimale' }, // Green
      { value: sl_optimal_p95 * 1.2, color: '#4299e1', label: 'Ampia' }, // Blue
    ],
    labels: { value: "SL Medio", target: "Target P95" },
  };
});

const tpBulletData = computed(() => {
    if (!tpData.value || tpData.value.tp_optimal_median == null) return null;
    const { tp_optimal_median, avg_user_planned_tp_r } = tpData.value;
    const median = tp_optimal_median;
    return {
        title: "Take Profit",
        value: avg_user_planned_tp_r,
        target: median,
        ranges: [
            { value: median * 0.8, color: '#f6e05e', label: 'Conservativa' }, // Yellow
            { value: median * 1.2, color: '#48bb78', label: 'Realistica' }, // Green
            { value: median * 2.0, color: '#4299e1', label: 'Ambiziosa' }, // Blue
        ],
        labels: { value: "TP Medio Pianif.", target: "Mediana Reale" },
    };
});


// --- Sezione 3 Logic ---
const AUTOCORR_THRESHOLD = 0.3;
const DRAWDOWN_Z_SCORE_THRESHOLD = 2.0;

const shouldShowAutocorrAlert = computed(() => {
  const autocorr = props.analysisData?.predictive_metrics?.r_autocorrelation;
  return autocorr != null && Math.abs(autocorr) > AUTOCORR_THRESHOLD;
});

const shouldShowDrawdownAlert = computed(() => {
  const zScore = props.analysisData?.drawdown_z_score?.z_score;
  return zScore != null && zScore > DRAWDOWN_Z_SCORE_THRESHOLD;
});

</script>
