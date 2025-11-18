<template>
  <div class="rules-editor">
    <h4>Rules Block Editor</h4>
    <pre>{{ content }}</pre>
  </div>
</template>

<script setup>
defineProps({
  content: {
    type: Object,
    required: true,
  },
});
</script>
