<script setup>
// No script logic needed for this purely presentational component.
</script>

<template>
  <div class="kpi-card">
    <slot />
  </div>
</template>

<style scoped>
.kpi-card {
  /* A. Stile della Card */
  background-color: var(--semantic-color-surface-primary);
  border-radius: var(--semantic-border-radius-surface);
  box-shadow: var(--semantic-effect-shadow-elevation-low);
  padding: var(--semantic-size-inset-lg);

  /* Layout di base che i figli sovrascriveranno */
  display: flex;
  flex-direction: column;
}
</style>