<template>
  <div v-if="clusterLabel"
       class="flex items-center justify-center w-6 h-6 rounded-full font-bold text-xs text-white"
       :style="{ backgroundColor: clusterColor }"
       v-tooltip="tooltipContent">
    {{ clusterLabel }}
  </div>
  <div v-else>-</div>
</template>

<script setup>
/**
 * @file ClusterBadge.vue
 * @description
 * Displays a colored badge for an SOA cluster, with a detailed tooltip.
 */
import { computed } from 'vue';

const props = defineProps({
  /**
   * The cluster label (e.g., 'A', 'B').
   * @type {String|null}
   */
  clusterLabel: {
    type: String,
    default: null,
  },
});

const CLUSTER_DETAILS = {
  'A': { name: 'Vincite Ottimali', color: '#4A90E2' },
  'B': { name: 'Stop Out / Breakeven', color: '#F5A623' },
  'C': { name: 'Perdite Controllate', color: '#7ED321' },
  'D': { name: 'Perdite da Reversal', color: '#D0021B' },
  'E': { name: 'Vincite Sub-ottimali', color: '#9013FE' },
};

const clusterColor = computed(() => {
  return CLUSTER_DETAILS[props.clusterLabel]?.color || '#808080'; // Grigio per default
});

const tooltipContent = computed(() => {
  const details = CLUSTER_DETAILS[props.clusterLabel];
  return details ? `${props.clusterLabel}: ${details.name}` : 'Nessun cluster assegnato';
});
</script>
