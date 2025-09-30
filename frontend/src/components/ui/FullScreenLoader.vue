<template>
  <div class="loader-overlay">
    <div class="loader-content">
      <LoadingSpinner />
      <p v-if="message" class="loader-message">{{ message }}</p>
    </div>
  </div>
</template>

<script setup>
import LoadingSpinner from './LoadingSpinner.vue';

defineProps({
  message: {
    type: String,
    default: '',
  },
});
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

.loader-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--semantic-size-stack-lg);
}

.loader-message {
  font: var(--semantic-font-style-body-lg);
  color: var(--semantic-color-text-on-brand);
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}
</style>