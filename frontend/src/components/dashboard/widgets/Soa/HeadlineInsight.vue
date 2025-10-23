<template>
  <div v-if="insight" class="mb-4 col-span-full">
    <p class="text-lg font-semibold text-center">
      <span v-if="icon" class="mr-2">{{ icon }}</span>
      {{ text }}
    </p>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  headline: {
    type: String,
    default: '',
  },
});

const icon = computed(() => {
  if (props.headline.includes('⚠')) return '⚠';
  if (props.headline.includes('🧠')) return '🧠';
  if (props.headline.includes('✅')) return '✅';
  return '';
});

const text = computed(() => {
  return props.headline.replace(/^[⚠🧠✅]\s*/, '');
});
</script>
