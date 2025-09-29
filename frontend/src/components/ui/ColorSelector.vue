<script setup>
import { defineProps, defineEmits } from 'vue';

const props = defineProps({
  modelValue: {
    type: String,
    default: '#4A90E2', // A default color
  },
});

const emit = defineEmits(['update:modelValue']);

const colors = [
  '#4A90E2', // Blue
  '#50E3C2', // Teal
  '#B8E986', // Green
  '#F8E71C', // Yellow
  '#F5A623', // Orange
  '#D0021B', // Red
  '#BD10E0', // Purple
  '#9013FE', // Violet
];

const selectColor = (color) => {
  emit('update:modelValue', color);
};
</script>

<template>
  <div class="color-selector">
    <div
      v-for="color in colors"
      :key="color"
      class="color-option"
      :style="{ backgroundColor: color }"
      :class="{ 'is-selected': modelValue === color }"
      @click="selectColor(color)"
      role="radio"
      :aria-checked="modelValue === color"
      :aria-label="`Color ${color}`"
    >
      <div v-if="modelValue === color" class="checkmark">✔</div>
    </div>
  </div>
</template>

<style scoped>
.color-selector {
  display: flex;
  flex-wrap: wrap;
  gap: var(--semantic-size-stack-sm);
}

.color-option {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  cursor: pointer;
  border: 2px solid transparent;
  transition: transform 0.2s ease, border-color 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.color-option:hover {
  transform: scale(1.1);
}

.color-option.is-selected {
  border-color: var(--semantic-color-border-focus);
  box-shadow: 0 0 0 1px var(--semantic-color-surface-primary), 0 0 0 3px var(--semantic-color-border-focus);
}

.checkmark {
  color: white;
  font-size: 0.8rem;
  font-weight: bold;
  text-shadow: 0 0 2px rgba(0, 0, 0, 0.5);
}
</style>