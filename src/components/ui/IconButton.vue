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
  width: var(--base-size-component-button-min-height-md); /* 40px */
  height: var(--base-size-component-button-min-height-md); /* 40px */
  border-radius: var(--base-border-radius-full);
  background-color: transparent;
  color: var(--semantic-color-text-secondary);
  border: none;
  cursor: pointer;
  transition: background-color var(--base-animation-duration-fast), color var(--base-animation-duration-fast);
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
