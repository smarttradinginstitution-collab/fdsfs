<template>
  <div class="w-full">
    <div class="relative w-full h-6 bg-neutral-600 rounded-full">
      <!-- Segmenti colorati di sfondo -->
      <div v-for="(segment, index) in segments" :key="index"
           class="absolute top-0 h-full rounded-full"
           :class="segment.color"
           :style="{ left: `${segment.start}%`, width: `${segment.width}%` }">
      </div>

      <!-- Indicatore del valore dell'utente (linea verticale) -->
      <div class="absolute top-0 h-full w-px bg-white transform -translate-x-1/2"
           :style="{ left: `${userValuePercentage}%` }"
           v-tooltip="`Tuo: ${userValue.toFixed(2)}`">
      </div>
    </div>
    <div class="flex justify-between text-xs mt-1 px-1">
      <span>0</span>
      <span>{{ (rangeEnd / 2).toFixed(1) }}</span>
      <span>{{ rangeEnd.toFixed(1) }}R</span>
    </div>
  </div>
</template>

<script setup>
/**
 * @file BulletGraph.vue
 * @description
 * A custom bullet graph component to visualize a value against colored segments
 * representing performance zones (e.g., optimal, too tight, too wide).
 */
import { computed } from 'vue';

const props = defineProps({
  /**
   * The main value to display as an indicator line.
   * @type {Number}
   */
  userValue: {
    type: Number,
    required: true,
  },
  /**
   * The end of the graph's range.
   * @type {Number}
   */
  rangeEnd: {
    type: Number,
    required: true,
  },
  /**
   * An array of objects defining the colored segments.
   * @type {Array<Object>}
   * @property {number} start - The start value of the segment.
   * @property {number} end - The end value of the segment.
   * @property {string} color - The Tailwind CSS background color class.
   */
  segmentDefs: {
    type: Array,
    required: true,
  },
});

const userValuePercentage = computed(() => {
  if (props.rangeEnd <= 0) return 0;
  // Cap the value to the range end for visualization
  const cappedValue = Math.min(props.userValue, props.rangeEnd);
  return (cappedValue / props.rangeEnd) * 100;
});

const segments = computed(() => {
  if (props.rangeEnd <= 0) return [];
  return props.segmentDefs.map(def => ({
    start: (def.start / props.rangeEnd) * 100,
    width: ((def.end - def.start) / props.rangeEnd) * 100,
    color: def.color,
  }));
});
</script>
