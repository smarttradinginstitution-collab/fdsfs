<template>
  <div class="psychology-block p-4 border rounded-md">
    <h3 class="text-lg font-semibold mb-2">Psychology / Mindset</h3>
    <textarea
      v-model="editableContent"
      class="w-full h-32 p-2 border rounded"
      placeholder="Notes on the required psychological state..."
    ></textarea>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
  content: {
    type: Object,
    default: () => ({ text: '' }),
  },
});

const emit = defineEmits(['update:content']);

const editableContent = ref(props.content.text);

watch(editableContent, (newValue) => {
  emit('update:content', { text: newValue });
});
</script>
