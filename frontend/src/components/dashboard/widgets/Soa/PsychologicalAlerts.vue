<template>
  <div class="p-4 bg-neutral-700 rounded-lg h-full">
    <h4 class="font-semibold text-center text-base mb-4">Monitoraggio Psicologico 🧠</h4>
    <div v-if="hasAlerts" class="space-y-4">
      <div v-if="autocorrelationAlert"
           class="flex items-center space-x-3 p-2 rounded-lg"
           v-tooltip="autocorrelationAlert.tooltip">
        <span class="text-2xl">{{ autocorrelationAlert.icon }}</span>
        <div class="flex flex-col">
          <span class="font-bold text-lg">{{ autocorrelationAlert.value }}</span>
          <span class="text-xs text-neutral-400">R-Autocorr.</span>
        </div>
      </div>
      <div v-if="drawdownAlert"
           class="flex items-center space-x-3 p-2 rounded-lg"
           v-tooltip="drawdownAlert.tooltip">
        <span class="text-2xl">📉</span>
        <div class="flex flex-col">
          <span class="font-bold text-lg">{{ drawdownAlert.value }}</span>
          <span class="text-xs text-neutral-400">Z-Score DD</span>
        </div>
      </div>
    </div>
    <div v-else class="flex flex-col items-center justify-center h-full text-center">
      <span class="text-3xl">✅</span>
      <p class="text-sm text-neutral-300 mt-2">Pattern Stabili</p>
    </div>
  </div>
</template>

<script setup>
/**
 * @file PsychologicalAlerts.vue
 * @description
 * Displays compact alert items for psychological patterns, with detailed
 * advice available in a tooltip.
 */
import { computed } from 'vue';

const props = defineProps({
  /**
   * The full SOA analysis data object.
   * @type {Object}
   */
  analysisData: {
    type: Object,
    required: true,
  },
});

const autocorrelationAlert = computed(() => {
  const r = props.analysisData.predictive_metrics?.r_autocorrelation;
  if (r == null || Math.abs(r) <= 0.15) {
    return null;
  }
  return {
    icon: r > 0 ? '🧠🔵' : '🧠🔴',
    value: r.toFixed(2),
    tooltip: props.analysisData.structured_advice?.psychological_advice,
  };
});

const drawdownAlert = computed(() => {
  const z = props.analysisData.drawdown_z_score?.z_score;
  if (z == null || z <= 1.5) {
    return null;
  }
  return {
    value: `Z: ${z.toFixed(1)}`,
    tooltip: props.analysisData.structured_advice?.psychological_advice,
  };
});

const hasAlerts = computed(() => {
  return !!autocorrelationAlert.value || !!drawdownAlert.value;
});
</script>
