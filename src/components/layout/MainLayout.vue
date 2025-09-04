<template>
  <div class="main-layout">
    <header class="layout-header">
      <slot name="header"></slot>
    </header>
    <main class="layout-main">
      <slot name="main"></slot>
    </main>
  </div>
</template>

<script setup>
// Questo componente non ha bisogno di logica, è puramente strutturale e stilistico.
</script>

<style scoped>
.main-layout {
  display: flex;
  flex-direction: column;
  width: 100%; /* Garantisce che il layout occupi tutto lo spazio del wrapper */
}

.layout-header {
  /* Stili richiesti per il contenitore dell'header */
  background-color: var(--color-surface-primary);
  padding: var(--size-stack-sm); /* Modificato come da richiesta */
  border-bottom: 1px solid var(--color-border-default); /* Modificato come da richiesta */
  width: 100%;
}

.layout-main {
  /* Il contenuto principale occuperà lo spazio rimanente */
  flex-grow: 1;
  padding: var(--size-stack-lg) var(--size-gutter-screen);
  /* Aggiungo uno sfondo di pagina per coerenza */
  background-color: var(--color-surface-page);
}
</style>
