<script setup>
import { useUiStore } from '../../stores/uiStore';
import SunIcon from '../icons/SunIcon.vue';
import MoonIcon from '../icons/MoonIcon.vue';

const uiStore = useUiStore();
</script>

<template>
  <button @click="uiStore.toggleTheme" class="theme-toggle">
    <SunIcon v-if="uiStore.theme === 'dark'" />
    <MoonIcon v-if="uiStore.theme === 'light'" />
    <span class="sr-only">Toggle theme</span>
  </button>
</template>

<style scoped>
.theme-toggle {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--semantic-color-text-secondary);
  padding: var(--semantic-size-inset-sm);
  border-radius: var(--semantic-border-radius-interactive);
  display: flex;
  justify-content: center;
  align-items: center;
  transition: all var(--base-animation-duration-fast);
}

.theme-toggle:hover {
  color: var(--semantic-color-text-primary);
  background-color: var(--semantic-color-surface-secondary);
}
</style>
