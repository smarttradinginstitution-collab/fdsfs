<script setup>
import { ref } from 'vue';

defineProps({
  iconOnly: {
    type: Boolean,
    default: false,
  },
});

const isOpen = ref(false);

function toggle() {
  isOpen.value = !isOpen.value;
}
</script>

<template>
  <div class="dropdown-container">
    <button @click="toggle" class="dropdown-trigger" :class="{ 'icon-only': iconOnly }">
      <span class="trigger-icon">
        <!-- Slot for an optional icon on the left -->
        <slot name="icon" />
      </span>
      <span v-if="!iconOnly" class="trigger-text">
        <!-- Slot for the button text -->
        <slot name="text">Dropdown</slot>
      </span>
      <span v-if="!iconOnly" class="trigger-chevron">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg>
      </span>
    </button>
    <div v-show="isOpen" class="dropdown-content">
      <slot name="content"></slot>
    </div>
  </div>
</template>

<style scoped>
.dropdown-container {
  position: relative;
  display: inline-block;
}

.dropdown-trigger {
  display: inline-flex;
  align-items: center;
  gap: var(--base-size-spacing-2); /* 8px */
  background-color: var(--color-surface-primary);
  border: var(--base-border-width-1) solid var(--color-border-default);
  color: var(--color-text-secondary);
  font: var(--typography-style-label-md);
  padding: var(--base-size-spacing-2) var(--base-size-spacing-3); /* 8px vertical, 12px horizontal */
  border-radius: var(--border-radius-interactive);
  cursor: pointer;
  transition: background-color var(--base-animation-duration-fast), border-color var(--base-animation-duration-fast);
}

/* Stili per la variante solo icona */
.dropdown-trigger.icon-only {
  background-color: transparent;
  border: none;
  border-radius: var(--base-border-radius-full);
  padding: var(--base-size-spacing-1); /* Padding ridotto */
  width: var(--base-size-component-button-min-height-md);
  height: var(--base-size-component-button-min-height-md);
  justify-content: center;
}
.dropdown-trigger.icon-only .trigger-icon > :deep(svg) {
  width: 100%;
  height: 100%;
}

.dropdown-trigger:hover {
  background-color: var(--color-surface-secondary);
}

.dropdown-trigger:focus-visible {
  outline: none;
  box-shadow: var(--shadow-focus-ring);
}

.trigger-icon, .trigger-chevron {
  display: flex;
  align-items: center;
}

.dropdown-content {
  position: absolute;
  top: calc(100% + var(--base-size-spacing-1)); /* 4px gap */
  right: 0;
  background-color: var(--color-surface-primary);
  border: var(--base-border-width-1) solid var(--color-border-default);
  border-radius: var(--border-radius-surface);
  box-shadow: var(--shadow-elevation-medium);
  z-index: var(--base-layer-z-index-dropdown);
  /* min-width rimosso per permettere al menu di adattarsi a schermi piccoli */
  padding: var(--base-size-spacing-2);
}
</style>
