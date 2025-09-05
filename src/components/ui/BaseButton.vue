<!--
// =============================================================================
// FILE: components/ui/BaseButton.vue
// DESCRIZIONE: Componente di base per un pulsante, ora con supporto per
// varianti "primary" e "secondary" per diverse priorità di azione.
// =============================================================================
-->
<script setup>
import { computed } from 'vue';

const props = defineProps({
  variant: {
    type: String,
    default: 'primary', // 'primary' o 'secondary'
    validator: (value) => ['primary', 'secondary'].includes(value),
  },
});

const buttonClass = computed(() => `button button--${props.variant}`);
</script>

<template>
  <button :class="buttonClass">
    <slot></slot>
  </button>
</template>

<style scoped>
/* Stili di base comuni a tutte le varianti */
.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--base-size-spacing-2);
  font: var(--semantic-font-style-button-label);
  padding-block: var(--semantic-size-button-padding-block-mobile);
  padding-inline: var(--semantic-size-button-padding-inline-mobile);
  border-radius: var(--semantic-border-radius-interactive);
  border: var(--base-border-width-1) solid transparent; /* Bordo trasparente per mantenere le dimensioni */
  cursor: pointer;
  transition: all var(--base-animation-duration-fast);
}

/* Tablet and larger */
@media (min-width: 768px) {
  .button {
    padding-block: var(--semantic-size-button-padding-block-tablet);
    padding-inline: var(--semantic-size-button-padding-inline-tablet);
  }
}

/* Desktop and larger */
@media (min-width: 1024px) {
  .button {
    padding-block: var(--semantic-size-button-padding-block-desktop);
    padding-inline: var(--semantic-size-button-padding-inline-desktop);
  }
}

.button:focus-visible {
  outline: none;
  box-shadow: var(--semantic-effect-shadow-focus-ring);
}

/* Variante Primaria */
.button--primary {
  background-color: var(--semantic-color-interactive-primary-default);
  color: var(--semantic-color-text-on-brand);
}
.button--primary:hover {
  background-color: var(--semantic-color-interactive-primary-hover);
}

/* Variante Secondaria */
.button--secondary {
  background-color: var(--semantic-color-surface-primary);
  color: var(--semantic-color-text-interactive);
  border-color: var(--semantic-color-border-default);
}
.button--secondary:hover {
  background-color: var(--semantic-color-surface-secondary);
  border-color: var(--semantic-color-border-subtle);
}
</style>
