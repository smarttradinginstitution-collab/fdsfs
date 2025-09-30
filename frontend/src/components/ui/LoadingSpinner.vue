<template>
  <div class="spinner"></div>
</template>

<style scoped>
.spinner {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  /* Use a more opaque color for the track to ensure visibility */
  border: 8px solid var(--semantic-color-surface-secondary);
  border-top-color: var(--semantic-color-action-primary-default);
  animation: spin 1s linear infinite;
}

/* Make the keyframes more explicit for better browser compatibility */
@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>