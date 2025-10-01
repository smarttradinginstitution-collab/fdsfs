<template>
  <PopoverMenu class="actions-menu" style="position: relative; z-index: 10;">
    <template #trigger="{ toggle }">
      <button @click.stop="toggle" class="trigger-button">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="icon">
          <path d="M10 3a1.5 1.5 0 110 3 1.5 1.5 0 010-3zM10 8.5a1.5 1.5 0 110 3 1.5 1.5 0 010-3zM11.5 15.5a1.5 1.5 0 10-3 0 1.5 1.5 0 003 0z" />
        </svg>
      </button>
    </template>
    <template #content="{ close }">
      <div class="menu-content" @click.stop>
        <slot :close-menu="close"></slot>
      </div>
    </template>
  </PopoverMenu>
</template>

<script setup>
import PopoverMenu from './PopoverMenu.vue';
</script>

<style scoped>
.trigger-button {
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--semantic-color-text-secondary);
  padding: var(--base-size-spacing-1);
  border-radius: var(--semantic-border-radius-interactive);
}
.trigger-button:hover {
  background-color: var(--semantic-color-surface-hover);
  color: var(--semantic-color-text-primary);
}
.icon {
  width: 1.25rem;
  height: 1.25rem;
}
.menu-content {
  display: flex;
  flex-direction: column;
  padding: var(--base-size-spacing-2) 0;
  min-width: 160px;
}

.menu-content :deep(.menu-item) {
  padding: var(--base-size-spacing-2) var(--base-size-spacing-4);
  font: var(--semantic-font-style-body-lg);
  color: var(--semantic-color-text-primary);
  cursor: pointer;
  white-space: nowrap;
}

.menu-content :deep(.menu-item:hover) {
  background-color: var(--semantic-color-surface-hover);
}

.menu-content :deep(.menu-item-danger) {
  color: var(--semantic-color-danger-default);
}

.menu-content :deep(.menu-item-danger:hover) {
  background-color: var(--semantic-color-danger-surface-hover);
  color: var(--semantic-color-danger-text-hover);
}
</style>