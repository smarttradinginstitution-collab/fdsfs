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
    default: 'primary', // 'primary', 'secondary', or 'danger'
    validator: (value) => ['primary', 'secondary', 'danger'].includes(value),
  },
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['medium', 'small'].includes(value),
  },
  isLoading: {
    type: Boolean,
    default: false,
  },
});

const buttonClass = computed(() => {
  let classes = `button button--${props.variant} button--${props.size}`;
  if (props.isLoading) {
    classes += ' is-loading';
  }
  return classes;
});
</script>

<script>
export default {
  inheritAttrs: false,
};
</script>

<template>
  <button :class="buttonClass" :disabled="isLoading" v-bind="$attrs">
    <span v-if="isLoading" class="spinner"></span>
    <span class="content" :class="{ 'is-hidden': isLoading }">
      <slot></slot>
    </span>
  </button>
</template>

<style scoped>
/* Stili di base comuni a tutte le varianti */
.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--base-size-spacing-2);
  border-radius: var(--semantic-border-radius-interactive);
  border: var(--base-border-width-1) solid transparent; /* Bordo trasparente per mantenere le dimensioni */
  cursor: pointer;
  transition: all var(--base-animation-duration-fast);
}

/* Stili per dimensione Medium (default) */
.button--medium {
  font: var(--semantic-font-style-button-label-medium);
  padding-block: var(--semantic-size-button-padding-block-medium);
  padding-inline: var(--semantic-size-button-padding-inline-medium);
}

/* Stili per dimensione Small */
.button--small {
  font: var(--semantic-font-style-button-label-small);
  padding-block: var(--semantic-size-button-padding-block-small);
  padding-inline: var(--semantic-size-button-padding-inline-small);
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

/* Variante Danger */
.button--danger {
  background-color: var(--semantic-color-danger-default);
  color: var(--semantic-color-text-on-brand);
}
.button--danger:hover {
  background-color: var(--semantic-color-danger-hover);
}

/* Stili per lo stato di caricamento */
.button.is-loading {
  cursor: wait;
}

.content.is-hidden {
  visibility: hidden;
}

.spinner {
  position: absolute;
  width: 20px;
  height: 20px;
  border: 2px solid currentColor;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
