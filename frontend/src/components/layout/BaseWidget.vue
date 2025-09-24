<template>
  <div class="widget-card">
    <div v-if="$slots.header" class="widget-header">
      <slot name="header"></slot>
    </div>
    <div class="widget-content">
      <slot></slot>
    </div>
  </div>
</template>

<style scoped>
.widget-card {
  background-color: var(--semantic-color-surface-primary);
  border-radius: var(--semantic-border-radius-surface);
  border: 1px solid var(--semantic-color-border-default);
  box-shadow: var(--semantic-effect-shadow-elevation-low);
  display: flex;
  flex-direction: column;
  height: 100%;
  min-width: 0;
}

.widget-header {
  position: relative;
  display: flex;
  align-items: center;
  padding: var(--semantic-size-inset-sm) var(--semantic-size-inset-lg);
  border-bottom: 1px solid var(--semantic-color-border-default);
  min-height: 60px;
  flex-shrink: 0; /* Prevent header from shrinking */
}

.widget-content {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  padding: var(--semantic-size-inset-lg);
  /* The header has padding, so the content doesn't need top padding */
  padding-top: 0;
  min-height: 0; /* Allow content to shrink and scroll if needed */
}

@include media-down('sm') {
  .widget-header {
    /* Riduci il padding e l'altezza su mobile */
    padding: var(--semantic-size-inset-sm) var(--semantic-size-inset-md);
    min-height: 50px;
  }
  .widget-content {
    /* Riduci il padding su mobile */
    padding: var(--semantic-size-inset-md);
    padding-top: 0;
  }
}
</style>
