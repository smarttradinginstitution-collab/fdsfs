<script setup>
import { ref } from 'vue';

const props = defineProps({
  tabs: {
    type: Array,
    required: true,
  },
  modelValue: {
    type: String,
    required: true,
  },
});

const emit = defineEmits(['update:modelValue']);

const selectTab = (tabName) => {
  emit('update:modelValue', tabName);
};
</script>

<template>
  <div class="tabs-container">
    <button
      v-for="tab in tabs"
      :key="tab.name"
      class="tab"
      :class="{ 'is-active': modelValue === tab.name }"
      @click="selectTab(tab.name)"
    >
      {{ tab.label }}
    </button>
  </div>
</template>

<style lang="scss" scoped>
.tabs-container {
  display: flex;
  border-bottom: 1px solid var(--semantic-color-border-default);
}

.tab {
  background: none;
  border: none;
  padding: var(--semantic-size-inset-sm) var(--semantic-size-inset-md);
  cursor: pointer;
  font: var(--semantic-font-style-label-md);
  color: var(--semantic-color-text-secondary);
  position: relative;
  transition: color 0.2s ease-in-out;

  &:hover {
    color: var(--semantic-color-text-primary);
  }

  &.is-active {
    color: var(--semantic-color-text-interactive);
    font-weight: var(--base-font-weight-semibold);
  }

  &.is-active::after {
    content: '';
    position: absolute;
    bottom: -1px;
    left: 0;
    right: 0;
    height: 2px;
    background-color: var(--semantic-color-text-interactive);
  }
}
</style>