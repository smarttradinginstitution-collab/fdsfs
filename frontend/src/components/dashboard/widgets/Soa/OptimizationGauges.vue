<template>
  <div class="space-y-4 p-4 bg-neutral-700 rounded-lg">
    <div>
      <h4 class="font-semibold text-center mb-2">Ottimizzazione SL/TP</h4>
      <div v-if="advice.sl_advice" class="text-sm text-neutral-300 space-y-2">
        <p v-html="formattedSlAdvice"></p>
      </div>
      <div v-if="advice.tp_advice" class="text-sm text-neutral-300 space-y-2 mt-2">
        <p v-html="formattedTpAdvice"></p>
      </div>
       <div v-if="!advice.sl_advice && !advice.tp_advice" class="text-sm text-center text-neutral-400">
        Dati insufficienti per generare consigli.
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * @file OptimizationGauges.vue
 * @description
 * Displays textual advice for Stop Loss and Take Profit optimization.
 * This component receives pre-formatted advice from the backend and renders it
 * as HTML, including simple markdown like bolding.
 */
import { computed } from 'vue';

const props = defineProps({
  /**
   * The structured advice object from the SOA analysis.
   * @type {Object}
   * @property {string|null} sl_advice - Textual advice for Stop Loss.
   * @property {string|null} tp_advice - Textual advice for Take Profit.
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

const formattedSlAdvice = computed(() => formatMarkdown(props.advice.sl_advice));
const formattedTpAdvice = computed(() => formatMarkdown(props.advice.tp_advice));

</script>
