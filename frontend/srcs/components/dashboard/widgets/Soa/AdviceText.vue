<template>
  <p class="advice-text" v-html="formattedText"></p>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  text: {
    type: String,
    default: ''
  }
});

const formattedText = computed(() => {
  if (!props.text || props.text.includes('404:')) {
    return '';
  }
  // A simple markdown-to-html conversion for bold text
  return props.text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
});
</script>

<style scoped>
.advice-text {
  font-size: 0.875rem;
  color: #a0aec0; /* Cool Gray 400 */
  line-height: 1.5;
}
</style>
