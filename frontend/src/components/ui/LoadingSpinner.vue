<template>
  <div class="spinner"></div>
</template>

<style scoped>
.spinner {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  border: 8px solid var(--semantic-color-surface-subtle);
  border-top-color: var(--semantic-color-action-primary-default);
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>