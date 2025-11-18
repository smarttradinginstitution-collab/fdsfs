<template>
  <div class="gallery-editor">
    <h4>Gallery Block Editor</h4>
    <!-- In future, this will be an image uploader -->
    <div class="image-grid">
      <div v-for="image in content.images" :key="image.url" class="img-placeholder">
        <img :src="image.url" alt="Gallery image" />
      </div>
    </div>
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
