<template>
  <div class="thesis-block p-4 border rounded-md">
    <h3 class="text-lg font-semibold mb-2">Thesis</h3>
    <textarea
      v-model="editableContent"
      class="w-full h-48 p-2 border rounded"
      placeholder="Enter your playbook thesis..."
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
