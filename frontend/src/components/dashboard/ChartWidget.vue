<script setup>
// Questo componente funge da contenitore generico per i widget della dashboard.
defineProps({
  title: {
    type: String,
    required: true,
  },
});
</script>

<template>
  <div class="chart-widget">
    <header class="widget-header">
      <div class="widget-title">
        <span>{{ title }}</span>
        <span class="info-icon">ⓘ</span>
      </div>
      <!-- Slot per eventuali controlli a destra (es. "View more") -->
      <div class="widget-controls">
        <slot name="controls"></slot>
      </div>
    </header>
    <main class="widget-content">
      <!--
        Questo slot di default ospiterà il contenuto principale del widget,
        come il componente del grafico (es. EquityCurveChart).
      -->
      <slot></slot>
    </main>
  </div>
</template>

<style scoped>
.chart-widget {
  /* Stili della card come da blueprint e Fase 1.4 del piano */
  background-color: var(--semantic-color-surface-primary);
  border: var(--base-border-width-1) solid var(--semantic-color-border-default);
  border-radius: var(--semantic-border-radius-surface);
  padding: var(--semantic-size-inset-lg);

  /* Layout Flexbox per impilare header e content */
  display: flex;
  flex-direction: column;
  gap: var(--semantic-size-stack-md); /* Spazio tra header e content */
}

.widget-header {
  /* Layout Flexbox per allineare titolo e controlli */
  display: flex;
  justify-content: space-between;
  align-items: center;

  /* Linea divisoria e spaziatura come da blueprint */
  border-bottom: var(--base-border-width-1) solid var(--semantic-color-border-default);
  padding-bottom: var(--semantic-size-inset-md);
}

.widget-title {
  /* Stile del titolo e dell'icona come da blueprint */
  font: var(--semantic-font-style-label-sm);
  color: var(--semantic-color-text-secondary);
  display: flex;
  align-items: center;
  gap: var(--semantic-size-stack-sm);
}

.info-icon {
  /* Opzionale: stile aggiuntivo per l'icona se necessario */
  cursor: help;
}

.widget-content {
  /* Il contenuto del grafico andrà qui */
}
</style>
