<template>
  <svg :viewBox="`0 0 ${size} ${size}`" class="doughnut-chart">
    <circle
      class="doughnut-chart-bg"
      :cx="center"
      :cy="center"
      :r="radius"
      :stroke-width="strokeWidth"
    />
    <circle
      class="doughnut-chart-fg"
      :cx="center"
      :cy="center"
      :r="radius"
      :stroke-width="strokeWidth"
      :stroke-dasharray="circumference"
      :stroke-dashoffset="dashOffset"
      :transform="`rotate(-90 ${center} ${center})`"
    />
  </svg>
</template>

<script setup>
import { computed, defineProps } from 'vue';

const props = defineProps({
  percentage: {
    type: Number,
    required: true,
    validator: (value) => value >= 0 && value <= 100,
  },
  size: {
    type: Number,
    default: 40,
  },
  strokeWidth: {
    type: Number,
    default: 4,
  },
});

const center = computed(() => props.size / 2);
const radius = computed(() => center.value - props.strokeWidth / 2);
const circumference = computed(() => 2 * Math.PI * radius.value);

const dashOffset = computed(() => {
  const progress = props.percentage / 100;
  return circumference.value * (1 - progress);
});
</script>

<style scoped>
.doughnut-chart {
  width: 100%;
  height: 100%;
}

.doughnut-chart-bg {
  fill: none;
  stroke: var(--semantic-color-surface-secondary);
}

.doughnut-chart-fg {
  fill: none;
  stroke: var(--semantic-color-interactive-primary-default);
  stroke-linecap: round;
  transition: stroke-dashoffset 0.3s ease-in-out;
}
</style>