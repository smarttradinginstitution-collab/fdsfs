<template>
  <div class="space-y-2">
    <h4 class="font-semibold text-center">Alert Psicologici</h4>
    <div v-if="hasAlerts" class="flex flex-col items-center space-y-2">
      <div v-if="autocorrelationAlert" class="flex items-center space-x-2 text-sm">
        <span :class="autocorrelationAlert.color">🧠</span>
        <span>{{ autocorrelationAlert.text }}</span>
      </div>
      <div v-if="drawdownAlert" class="flex items-center space-x-2 text-sm text-red-500">
        <span>📉</span>
        <span>{{ drawdownAlert.text }}</span>
      </div>
    </div>
    <div v-else class="text-center text-sm text-green-500">
      <span>✅</span>
      <span>Pattern psicologici stabili.</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  predictiveMetrics: {
    type: Object,
    required: true,
  },
  drawdownZScore: {
    type: Object,
    required: true,
  },
});

const autocorrelationAlert = computed(() => {
  const r = props.predictiveMetrics.r_autocorrelation;
  if (Math.abs(r) > 0.15) {
    return {
      text: `${r.toFixed(2)} R-Autocorr.`,
      color: r > 0 ? 'text-blue-500' : 'text-red-500',
    };
  }
  return null;
});

const drawdownAlert = computed(() => {
  const z = props.drawdownZScore.z_score;
  if (z > 1.5) {
    return {
      text: `DD Z-Score: ${z.toFixed(1)}`,
    };
  }
  return null;
});

const hasAlerts = computed(() => {
  return !!autocorrelationAlert.value || !!drawdownAlert.value;
});
</script>
