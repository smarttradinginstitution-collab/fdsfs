<script setup>
import { defineProps, defineEmits } from 'vue';

defineProps({
  tabs: {
    type: Array,
    required: true, // e.g., [{ id: 'trade-note', label: 'Trade note' }]
  },
  modelValue: {
    type: String,
    required: true, // The `id` of the currently active tab
  },
});

const emit = defineEmits(['update:modelValue']);

const selectTab = (tabId) => {
  emit('update:modelValue', tabId);
};
</script>

<template>
  <div class="pill-tabs">
    <button
      v-for="tab in tabs"
      :key="tab.id"
      :class="['pill-tab-button', { 'is-active': modelValue === tab.id }]"
      @click="selectTab(tab.id)"
    >
      {{ tab.label }}
    </button>
  </div>
</template>

<style lang="scss" scoped>
.pill-tabs {
  display: flex;
  gap: var(--semantic-size-gap-sm);
}

.pill-tab-button {
  padding: var(--semantic-size-inset-xs) var(--semantic-size-inset-md);
  font: var(--semantic-font-style-body-sm-bold);
  color: var(--semantic-color-text-secondary);
  background-color: var(--semantic-color-surface-primary);
  border: 1px solid var(--semantic-color-border-neutral-subtle);
  border-radius: var(--semantic-border-radius-actions-sm);
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background-color: var(--semantic-color-surface-secondary);
    color: var(--semantic-color-text-primary);
  }

  &.is-active {
    background-color: var(--semantic-color-surface-secondary);
    color: var(--semantic-color-text-primary);
    border-color: var(--semantic-color-border-neutral-strong);
  }
}
</style>