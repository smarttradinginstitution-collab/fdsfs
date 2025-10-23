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
import { computed } from 'vue';

const props = defineProps({
  advice: {
    type: Object,
    required: true,
  },
});

// Funzione per convertire il markdown in HTML
const formatMarkdown = (text) => {
  if (!text) return '';
  return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
};

const formattedAdvice = computed(() => formatMarkdown(props.advice.psychological_advice));
</script>
