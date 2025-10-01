<script setup>
// No script logic needed for this purely presentational component.
</script>

<template>
  <div class="kpi-card">
    <div class="card-header">
      <slot name="title" />
    </div>
    <div class="card-body">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.kpi-card {
  /* A. Stile della Card */
  background-color: var(--semantic-color-surface-primary);
  border-radius: var(--semantic-border-radius-surface);
  box-shadow: var(--semantic-effect-shadow-elevation-low);
  padding: var(--semantic-size-inset-lg);

  /* Layout interno */
  display: flex;
  flex-direction: column;
  gap: 8px; /* Spazio tra header e body */
}

.card-header {
  /* Stile per il titolo della card, usando i token specificati */
  font: var(--semantic-font-style-heading-sm);
  color: var(--semantic-color-text-secondary);
}

.card-body {
  /* Il corpo della card si adatterà al contenuto (metrica + grafico) */
  flex-grow: 1;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}
</style>