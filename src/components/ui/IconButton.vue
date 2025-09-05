<script setup>
defineProps({
  ariaLabel: {
    type: String,
    required: true,
  }
});
</script>

<template>
  <button class="icon-button" :aria-label="ariaLabel">
    <slot></slot>
  </button>
</template>

<style scoped>
.icon-button {
  display: grid;
  place-items: center;
  width: var(--semantic-size-component-icon-button-size-mobile);
  height: var(--semantic-size-component-icon-button-size-mobile);
  border-radius: var(--base-border-radius-full);
  background-color: transparent;
  color: var(--semantic-color-text-secondary);
  border: none;
  cursor: pointer;
  transition: background-color var(--base-animation-duration-fast), color var(--base-animation-duration-fast);
}

@media (min-width: 768px) {
  .icon-button {
    width: var(--semantic-size-component-icon-button-size-tablet);
    height: var(--semantic-size-component-icon-button-size-tablet);
  }
}

@media (min-width: 1024px) {
  .icon-button {
    width: var(--semantic-size-component-icon-button-size-desktop);
    height: var(--semantic-size-component-icon-button-size-desktop);
  }
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
