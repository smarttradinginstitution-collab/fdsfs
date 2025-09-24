<script setup>
import { computed } from 'vue';

const props = defineProps({
  size: {
    type: String,
    default: 'medium', // small, medium, large
    validator: (value) => ['small', 'medium', 'large'].includes(value),
  },
  ariaLabel: {
    type: String,
    required: true,
  },
});

const sizeClasses = computed(() => `icon-button--${props.size}`);
</script>

<template>
  <button :class="['icon-button', sizeClasses]" :aria-label="ariaLabel">
    <slot></slot>
  </button>
</template>

<style scoped>
.icon-button {
  background-color: transparent;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  transition: background-color 0.2s;
  color: inherit; /* Inherit color from parent by default */
}

.icon-button:hover {
  background-color: rgba(0, 0, 0, 0.05);
}
.dark .icon-button:hover {
    background-color: rgba(255, 255, 255, 0.1);
}

/* --- Sizes --- */
.icon-button--small {
  width: 24px;
  height: 24px;
}
.icon-button--medium {
  width: 32px;
  height: 32px;
}
.icon-button--large {
  width: 40px;
  height: 40px;
}

/* --- SVG Icon Sizing --- */
.icon-button--small :deep(svg) {
  width: 16px;
  height: 16px;
}
.icon-button--medium :deep(svg) {
  width: 20px;
  height: 20px;
}
.icon-button--large :deep(svg) {
  width: 24px;
  height: 24px;
}
</style>