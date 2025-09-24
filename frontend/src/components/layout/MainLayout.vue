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
import { watch, nextTick } from 'vue';
import { useUiStore } from '../../stores/uiStore';

const uiStore = useUiStore();

// When the sidebar collapses or expands, the width of the main content area changes.
// Charting libraries often need to be explicitly told to redraw when their container
// size changes. Dispatching a global 'resize' event is a standard way to trigger this.
watch(() => uiStore.isSidebarCollapsed, () => {
  // We wait for the next DOM update cycle. This ensures that the CSS transition
  // for the sidebar has started and the new dimensions of the main content
  // are being calculated before we tell the charts to resize.
  nextTick(() => {
    window.dispatchEvent(new Event('resize'));
  });
});
</script>

<style scoped>
.main-layout {
  display: flex;
  flex-direction: column;
  width: 100%; /* Garantisce che il layout occupi tutto lo spazio del wrapper */
}

.layout-header {
  /* Stili richiesti per il contenitore dell'header */
  background-color: var(--semantic-color-surface-primary);
  padding: var(--semantic-size-stack-sm); /* Modificato come da richiesta */
  border-bottom: 1px solid var(--semantic-color-border-default); /* Modificato come da richiesta */
  width: 100%;
}

.layout-main {
  /* Il contenuto principale occuperà lo spazio rimanente */
  flex-grow: 1;
  padding: var(--semantic-size-stack-lg) var(--semantic-size-gutter-screen);
  /* Aggiungo uno sfondo di pagina per coerenza */
  background-color: var(--semantic-color-surface-page);
}

@media (max-width: 400px) {
  .layout-main {
    /* Riduci il padding su schermi molto piccoli, come richiesto */
    padding: var(--semantic-size-stack-md) var(--semantic-size-stack-sm);
  }
}
</style>
