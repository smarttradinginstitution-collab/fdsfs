<template>
  <span class="pill">
    <slot></slot>
  </span>
</template>

<style scoped>
.pill {
  display: inline-block;
  padding: var(--semantic-size-inset-xxs) var(--semantic-size-inset-sm);
  border-radius: var(--semantic-border-radius-tag);
  background-color: var(--semantic-color-surface-secondary);
  color: var(--semantic-color-text-secondary);
  font: var(--semantic-font-style-label-sm);
  font-weight: 500;
  text-transform: capitalize;
}
</style>
