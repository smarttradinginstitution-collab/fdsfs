<template>
  <div class="skeleton-box" :style="{ width, height, borderRadius }"></div>
</template>

<script setup>
defineProps({
  width: {
    type: String,
    default: '100%',
  },
  height: {
    type: String,
    default: '1rem', // Altezza di base simile a una riga di testo
  },
  borderRadius: {
    type: String,
    default: 'var(--semantic-border-radius-container)', // Usa i token di design
  },
});
</script>

<style lang="scss" scoped>
@keyframes pulse {
  0% {
    background-color: var(--semantic-color-surface-secondary);
  }
  50% {
    background-color: var(--semantic-color-surface-tertiary);
  }
  100% {
    background-color: var(--semantic-color-surface-secondary);
  }
}

.skeleton-box {
  display: inline-block;
  animation: pulse 1.5s infinite ease-in-out;
}
</style>
