<template>
  <div class="toolbar-color-picker">
    <button @click="triggerColorPicker" class="color-picker-button">
      <slot></slot>
      <div class="color-indicator" :style="{ backgroundColor: modelValue }"></div>
    </button>
    <input
      type="color"
      ref="colorInput"
      :value="modelValue"
      @input="emit('update:modelValue', $event.target.value)"
      style="visibility: hidden; width: 0; height: 0; position: absolute;"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue';

defineProps({
  modelValue: {
    type: String,
    required: true,
  },
});

const emit = defineEmits(['update:modelValue']);

const colorInput = ref(null);

const triggerColorPicker = () => {
  colorInput.value?.click();
};
</script>

<style lang="scss" scoped>
.toolbar-color-picker {
  position: relative;
  display: inline-block;
  margin: 0 0.1rem;
}

.color-picker-button {
  position: relative;
  background: none;
  border: 1px solid transparent;
  padding: 0.3rem 0.5rem;
  cursor: pointer;
  border-radius: 4px;
  color: var(--semantic-color-text-primary);
  line-height: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;

  &:hover {
    background-color: var(--semantic-color-surface-tertiary);
  }

  .color-indicator {
    width: 80%;
    height: 3px;
    border-radius: 1px;
    margin-top: 3px;
  }
}
</style>