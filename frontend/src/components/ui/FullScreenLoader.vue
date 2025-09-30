<template>
  <div class="loader-overlay">
    <LoadingSpinner />
  </div>
</template>

<script setup>
import LoadingSpinner from './LoadingSpinner.vue';
</script>

<style scoped>
.loader-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  z-index: 9999; /* Ensure it's on top of everything */
}
</style>