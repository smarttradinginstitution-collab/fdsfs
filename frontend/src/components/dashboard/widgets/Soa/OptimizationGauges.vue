<template>
  <div class="space-y-4">
    <div class="text-center">
      <h4 class="font-semibold">Ottimizzazione Stop Loss</h4>
      <div class="relative w-full h-8 bg-neutral-700 rounded-full overflow-hidden">
        <div
          class="absolute top-0 left-0 h-full bg-blue-500"
          :style="{ width: `${slPercentage}%` }"
        ></div>
        <div
          class="absolute top-0 h-full border-r-2 border-dashed border-white"
          :style="{ left: `${slOptimalPercentage}%` }"
        ></div>
      </div>
      <div class="text-xs mt-1">
        Tuo: {{ slTpData.avg_user_stress_ratio?.toFixed(2) }} R | Ottimale (P95): {{ slTpData.sl_optimal_p95?.toFixed(2) }} R
      </div>
    </div>
    <div class="text-center">
      <h4 class="font-semibold">Ottimizzazione Take Profit</h4>
      <div class="relative w-full h-8 bg-neutral-700 rounded-full overflow-hidden">
        <div
          class="absolute top-0 left-0 h-full bg-green-500"
          :style="{ width: `${tpPercentage}%` }"
        ></div>
        <div
          class="absolute top-0 h-full border-r-2 border-dashed border-white"
          :style="{ left: `${tpOptimalPercentage}%` }"
        ></div>
      </div>
      <div class="text-xs mt-1">
        Tuo: {{ slTpData.avg_user_planned_tp_r?.toFixed(2) }} R | Mediana: {{ slTpData.tp_optimal_median?.toFixed(2) }} R
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  slTpData: {
    type: Object,
    required: true,
  },
});

// Nota: Questi calcoli percentuali sono semplificati.
// Una vera gauge avrebbe una scala più complessa.
// Qui normalizziamo rispetto al valore ottimale.
const slPercentage = computed(() => {
  if (!props.slTpData.sl_optimal_p95 || !props.slTpData.avg_user_stress_ratio) return 0;
  const max = Math.max(props.slTpData.sl_optimal_p95, props.slTpData.avg_user_stress_ratio);
  return (props.slTpData.avg_user_stress_ratio / max) * 100;
});

const slOptimalPercentage = computed(() => {
  if (!props.slTpData.sl_optimal_p95 || !props.slTpData.avg_user_stress_ratio) return 0;
  const max = Math.max(props.slTpData.sl_optimal_p95, props.slTpData.avg_user_stress_ratio);
  return (props.slTpData.sl_optimal_p95 / max) * 100;
});

const tpPercentage = computed(() => {
  if (!props.slTpData.tp_optimal_median || !props.slTpData.avg_user_planned_tp_r) return 0;
  const max = Math.max(props.slTpData.tp_optimal_median, props.slTpData.avg_user_planned_tp_r);
  return (props.slTpData.avg_user_planned_tp_r / max) * 100;
});

const tpOptimalPercentage = computed(() => {
  if (!props.slTpData.tp_optimal_median || !props.slTpData.avg_user_planned_tp_r) return 0;
  const max = Math.max(props.slTpData.tp_optimal_median, props.slTpData.avg_user_planned_tp_r);
  return (props.slTpData.tp_optimal_median / max) * 100;
});
</script>
