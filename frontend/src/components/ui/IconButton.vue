<script setup>
import { computed } from 'vue';

const props = defineProps({
  ariaLabel: {
    type: String,
    required: true,
  },
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['medium', 'small'].includes(value),
  }
});

const buttonClass = computed(() => `icon-button icon-button--${props.size}`);
</script>

<template>
  <button :class="buttonClass" :aria-label="ariaLabel">
    <slot></slot>
  </button>
</template>

<style scoped>
.icon-button {
  display: grid;
  place-items: center;
  border-radius: var(--base-border-radius-full);
  background-color: transparent;
  color: var(--semantic-color-text-secondary);
  border: none;
  cursor: pointer;
  transition: background-color var(--base-animation-duration-fast), color var(--base-animation-duration-fast);
}

/* Medium Size */
.icon-button--medium {
  width: var(--semantic-size-component-icon-button-size-medium);
  height: var(--semantic-size-component-icon-button-size-medium);
}

/* Small Size */
.icon-button--small {
  width: var(--semantic-size-component-icon-button-size-small);
  height: var(--semantic-size-component-icon-button-size-small);
}

.icon-button:hover {
  background-color: var(--semantic-color-surface-secondary);
}

.icon-button:focus-visible {
  outline: none;
  box-shadow: var(--semantic-effect-shadow-focus-ring);
}

/* Make the SVG inside the button scale nicely */
.icon-button > :deep(svg) {
  width: 60%;
  height: 60%;
}
</style>
