<script setup>
import { defineProps } from 'vue';

const props = defineProps({
  steps: {
    type: Array,
    required: true,
  },
  currentStep: {
    type: Number,
    required: true,
  },
});
</script>

<template>
  <div class="stepper">
    <div
      v-for="(step, index) in steps"
      :key="index"
      :class="['step-item', { 'is-active': index === currentStep, 'is-complete': index < currentStep }]"
    >
      <div class="step-circle">{{ index + 1 }}</div>
      <div class="step-label">{{ step }}</div>
    </div>
  </div>
</template>

<style scoped>
.stepper {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--semantic-size-stack-xl);
  padding: var(--semantic-size-inset-md) 0;
}

.step-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: var(--semantic-color-text-disabled);
  transition: color 0.3s ease;
}

.step-circle {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: var(--semantic-color-surface-secondary);
  border: 1px solid var(--semantic-color-border-default);
  display: flex;
  align-items: center;
  justify-content: center;
  font: var(--semantic-font-style-body-md-bold);
  margin-bottom: var(--semantic-size-stack-xs);
  transition: background-color 0.3s ease, border-color 0.3s ease, color 0.3s ease;
}

.step-label {
  font: var(--semantic-font-style-body-sm);
}

/* Active Step Styling */
.step-item.is-active .step-circle {
  background-color: var(--semantic-color-primary-default);
  border-color: var(--semantic-color-primary-default);
  color: var(--semantic-color-text-on-primary);
}

.step-item.is-active .step-label {
  color: var(--semantic-color-text-primary);
  font-weight: 600;
}

/* Completed Step Styling */
.step-item.is-complete .step-circle {
  background-color: var(--semantic-color-surface-success);
  border-color: var(--semantic-color-border-success);
  color: var(--semantic-color-text-success);
}

.step-item.is-complete .step-label {
  color: var(--semantic-color-text-secondary);
}
</style>