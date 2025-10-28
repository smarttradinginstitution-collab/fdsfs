<template>
  <div class="space-y-6 p-4 bg-neutral-700 rounded-lg h-full">
    <h4 class="font-semibold text-center text-base">Leve di Ottimizzazione R:R 🔧</h4>

    <!-- Blocco SL -->
    <div v-if="advice.sl_advice">
      <p class="text-sm text-neutral-300 mb-2" v-html="formattedSlAdvice"></p>
      <BulletGraph
        v-if="slValues.isValid"
        :user-value="slValues.user"
        :range-end="slValues.rangeEnd"
        :segment-defs="slValues.segments"
      />
    </div>

    <!-- Blocco TP -->
    <div v-if="advice.tp_advice">
      <p class="text-sm text-neutral-300 mb-2" v-html="formattedTpAdvice"></p>
       <BulletGraph
        v-if="tpValues.isValid"
        :user-value="tpValues.user"
        :range-end="tpValues.rangeEnd"
        :segment-defs="tpValues.segments"
      />
    </div>

    <div v-if="!advice.sl_advice && !advice.tp_advice" class="text-sm text-center text-neutral-400 pt-8">
      Dati insufficienti per l'analisi di ottimizzazione.
    </div>
  </div>
</template>

<script setup>
/**
 * @file OptimizationGauges.vue
 * @description
 * Displays textual advice and bullet graphs for Stop Loss and Take Profit optimization.
 */
import { computed } from 'vue';
import BulletGraph from './BulletGraph.vue';

const props = defineProps({
  /**
   * The structured advice object from the SOA analysis.
   * @type {Object}
   */
  advice: {
    type: Object,
    required: true,
  },
  /**
   * The raw numerical data for parametric optimization.
   * @type {Object}
   */
  optimizationData: {
    type: Object,
    required: true,
  },
});

const slValues = computed(() => {
  const data = props.optimizationData;
  const user = data.avg_user_stress_ratio;
  const p90 = data.sl_optimal_p90;
  const p95 = data.sl_optimal_p95;

  if (user == null || p90 == null || p95 == null) {
    return { isValid: false };
  }

  const rangeEnd = Math.max(user, p95) * 1.2;
  const segments = [
    { start: 0, end: p90, color: 'bg-red-500 bg-opacity-50' }, // Troppo stretto
    { start: p90, end: p95, color: 'bg-green-500 bg-opacity-50' }, // Ottimale
    { start: p95, end: rangeEnd, color: 'bg-yellow-500 bg-opacity-50' }, // Ampio
  ];

  return { isValid: true, user, rangeEnd, segments };
});

const tpValues = computed(() => {
  const data = props.optimizationData;
  const user = data.avg_user_planned_tp_r;
  const median = data.tp_optimal_median;

  if (user == null || median == null) {
    return { isValid: false };
  }

  const rangeEnd = Math.max(user, median) * 1.2;
  const segments = [
    { start: 0, end: median * 0.8, color: 'bg-yellow-500 bg-opacity-50' }, // Conservativo
    { start: median * 0.8, end: median * 1.2, color: 'bg-green-500 bg-opacity-50' }, // Realistico
    { start: median * 1.2, end: rangeEnd, color: 'bg-red-500 bg-opacity-50' }, // Ambizioso
  ];

  return { isValid: true, user, rangeEnd, segments };
});


/**
 * Converts simple markdown (bold) to HTML.
 * @param {string} text - The input text with markdown.
 * @returns {string} The formatted HTML string.
 */
const formatMarkdown = (text) => {
  if (!text) return '';
  return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
};

const formattedSlAdvice = computed(() => formatMarkdown(props.advice.sl_advice));
const formattedTpAdvice = computed(() => formatMarkdown(props.advice.tp_advice));
</script>
