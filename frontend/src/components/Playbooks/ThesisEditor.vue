<template>
  <div class="thesis-editor">
    <h4>Thesis Block Editor</h4>
    <!-- In future, this will be a rich text editor -->
    <div v-html="content.html"></div>
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
