<script setup>
import { defineProps, defineEmits } from 'vue';

const props = defineProps({
  tabs: {
    type: Array,
    required: true, // e.g., [{ id: 'stats', label: 'Stats' }]
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
  <div class="base-tabs">
    <div class="tabs-header">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        :class="['tab-button', { 'is-active': modelValue === tab.id }]"
        @click="selectTab(tab.id)"
      >
        {{ tab.label }}
      </button>
    </div>
    <div class="tab-content">
      <slot :name="modelValue"></slot>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.base-tabs {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.tabs-header {
  display: flex;
  border-bottom: 1px solid var(--semantic-color-border-default);
}

.tab-button {
  padding: var(--semantic-size-inset-sm);
  font: var(--semantic-font-style-label-sm);
  color: var(--semantic-color-text-secondary);
  background-color: transparent;
  border: none;
  cursor: pointer;
  position: relative;
  transition: color 0.2s ease;

  &:hover {
    color: var(--semantic-color-text-primary);
  }

  &.is-active {
    color: var(--semantic-color-text-primary);
    font-weight: var(--base-font-weight-semibold);

    &::after {
      content: '';
      position: absolute;
      bottom: -1px; // Align with the parent's border
      left: 0;
      right: 0;
      height: 2px;
      background-color: var(--semantic-color-interactive-primary-default);
    }
  }
}

.tab-content {
  padding-top: var(--semantic-size-stack-lg);
}
</style>