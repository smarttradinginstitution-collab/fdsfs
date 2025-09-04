<template>
  <span class="pill">
    <slot></slot>
  </span>
</template>

<style scoped>
.pill {
  display: inline-block;
  padding: var(--base-size-spacing-1) var(--base-size-spacing-3);
  border-radius: var(--base-border-radius-full);
  background-color: var(--color-surface-secondary);
  color: var(--color-text-secondary);
  font: var(--typography-style-label-sm);
  font-weight: 500;
  text-transform: capitalize;
}
</style>
