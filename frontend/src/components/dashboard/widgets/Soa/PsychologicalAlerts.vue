<template>
  <div class="p-4 bg-neutral-700 rounded-lg">
    <h4 class="font-semibold text-center mb-2">Alert Psicologici</h4>
    <div v-if="advice.psychological_advice" class="text-sm text-neutral-300">
      <p v-html="formattedAdvice" class="whitespace-pre-wrap"></p>
    </div>
    <div v-else class="text-sm text-center text-neutral-400">
      Nessun alert psicologico rilevato.
    </div>
  </div>
</template>

<script setup>
/**
 * @file PsychologicalAlerts.vue
 * @description
 * Displays textual advice related to psychological patterns detected
 * in the SOA analysis (e.g., autocorrelation, drawdown z-score).
 * Renders pre-formatted advice from the backend as HTML.
 */
import { computed } from 'vue';

const props = defineProps({
  /**
   * The structured advice object from the SOA analysis.
   * @type {Object}
   * @property {string|null} psychological_advice - Textual advice for psychological patterns.
   */
  advice: {
    type: Object,
    required: true,
  },
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

const formattedAdvice = computed(() => formatMarkdown(props.advice.psychological_advice));
</script>
